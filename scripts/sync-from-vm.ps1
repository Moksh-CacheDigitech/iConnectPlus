#Requires -Version 5.1
<#
.SYNOPSIS
  Pull Postgres + MinIO data from the ERP VM into the local Docker `erp` stack.

.DESCRIPTION
  Mirrors VM services (172.16.200.30 by default) onto local containers started via
  docker-compose.local.yml. Aborts if VM Postgres is unreachable.

  Usage:
    powershell -File scripts/sync-from-vm.ps1
    powershell -File scripts/sync-from-vm.ps1 -VmHost 172.16.200.30 -SkipMinio
#>
[CmdletBinding()]
param(
  [string]$VmHost = "172.16.200.30",
  [int]$PostgresPort = 5433,
  [int]$MinioPort = 9000,
  [string]$ComposeFile = "docker-compose.local.yml",
  [string]$Project = "erp",
  [switch]$SkipPostgres,
  [switch]$SkipMinio
)

$ErrorActionPreference = "Stop"
$RepoRoot = Split-Path -Parent $PSScriptRoot
Set-Location $RepoRoot

function Test-TcpPort {
  param([string]$HostName, [int]$Port, [int]$TimeoutMs = 2500)
  try {
    $client = New-Object System.Net.Sockets.TcpClient
    $iar = $client.BeginConnect($HostName, $Port, $null, $null)
    if (-not $iar.AsyncWaitHandle.WaitOne($TimeoutMs, $false)) {
      $client.Close()
      return $false
    }
    $client.EndConnect($iar)
    $client.Close()
    return $true
  } catch {
    return $false
  }
}

function Read-DotEnvValue {
  param([string]$Key, [string]$Default = "")
  $envPath = Join-Path $RepoRoot ".env"
  if (-not (Test-Path $envPath)) { return $Default }
  foreach ($line in Get-Content $envPath) {
    if ($line -match "^\s*#") { continue }
    if ($line -match "^\s*$Key\s*=\s*(.*)$") {
      return $Matches[1].Trim().Trim('"').Trim("'")
    }
  }
  return $Default
}

Write-Host "Sync local erp stack FROM VM $VmHost ..." -ForegroundColor Cyan

$pgUser = Read-DotEnvValue "POSTGRES_USER" "erp-postgres"
$pgPass = Read-DotEnvValue "POSTGRES_PASSWORD" "erp-postgres"
$pgDb = Read-DotEnvValue "POSTGRES_DB" "erp"
$minioUser = Read-DotEnvValue "MINIO_ROOT_USER" "erp_minio"
$minioPass = Read-DotEnvValue "MINIO_ROOT_PASSWORD" "erp_minio_password"
$bucket = Read-DotEnvValue "S3_BUCKET" "cache-erp-bucket"

if (-not $SkipPostgres -and -not (Test-TcpPort -HostName $VmHost -Port $PostgresPort)) {
  throw @"
VM Postgres is unreachable at ${VmHost}:${PostgresPort}.
Connect to the ERP LAN/VPN (this host is often on 172.16.110.x while the VM is 172.16.200.30),
bring the VM up, then re-run this script.
"@
}

if (-not $SkipMinio -and -not (Test-TcpPort -HostName $VmHost -Port $MinioPort)) {
  Write-Warning "VM MinIO unreachable at ${VmHost}:${MinioPort} - skipping object sync."
  $SkipMinio = $true
}

Write-Host "Ensuring local postgres is up..." -ForegroundColor Yellow
docker compose -f $ComposeFile -p $Project up -d postgres | Out-Null
if (-not $SkipMinio) {
  docker compose -f $ComposeFile -p $Project --profile minio up -d minio minio-init 2>$null | Out-Null
}

$stamp = Get-Date -Format "yyyyMMdd-HHmmss"
$dumpDir = Join-Path $RepoRoot "var\vm-sync"
New-Item -ItemType Directory -Force -Path $dumpDir | Out-Null
$dumpName = "erp-vm-$stamp.dump"
$dumpFile = Join-Path $dumpDir $dumpName

if (-not $SkipPostgres) {
  Write-Host "Dumping VM Postgres ${VmHost}:${PostgresPort}/$pgDb ..." -ForegroundColor Cyan
  docker run --rm `
    -e "PGPASSWORD=$pgPass" `
    -v "${dumpDir}:/out" `
    postgres:16-alpine `
    pg_dump -h $VmHost -p $PostgresPort -U $pgUser -d $pgDb -Fc -f "/out/$dumpName"

  if (-not (Test-Path $dumpFile)) {
    throw "Dump file missing: $dumpFile"
  }

  Write-Host "Restoring into local erp-postgres (drop/recreate database for a clean mirror)..." -ForegroundColor Cyan
  docker cp $dumpFile "erp-postgres:/tmp/erp-vm.dump"
  $sqlPath = Join-Path $dumpDir "recreate-$pgDb.sql"
  @(
    "SELECT pg_terminate_backend(pid) FROM pg_stat_activity WHERE datname = '$pgDb' AND pid <> pg_backend_pid();"
    "DROP DATABASE IF EXISTS `"$pgDb`";"
    "CREATE DATABASE `"$pgDb`" OWNER `"$pgUser`";"
  ) | Set-Content -Path $sqlPath -Encoding ascii
  docker cp $sqlPath "erp-postgres:/tmp/recreate-erp.sql"
  docker exec -e "PGPASSWORD=$pgPass" erp-postgres `
    psql -U $pgUser -d postgres -v ON_ERROR_STOP=1 -f /tmp/recreate-erp.sql
  if ($LASTEXITCODE -ne 0) {
    throw "Failed to recreate database $pgDb (owner $pgUser)."
  }
  docker exec -e "PGPASSWORD=$pgPass" erp-postgres `
    pg_restore -U $pgUser -d $pgDb --no-owner --no-acl /tmp/erp-vm.dump
  $restoreExit = $LASTEXITCODE
  docker exec erp-postgres sh -c "rm -f /tmp/erp-vm.dump /tmp/recreate-erp.sql" | Out-Null
  if ($restoreExit -ne 0) {
    Write-Warning "pg_restore exited $restoreExit (some non-fatal errors can still occur). Verify with: docker exec erp-postgres psql -U $pgUser -d $pgDb -c '\dn'"
  } else {
    Write-Host "Postgres sync complete." -ForegroundColor Green
  }
}

if (-not $SkipMinio) {
  Write-Host "Mirroring MinIO bucket '$bucket' from VM -> local erp-minio ..." -ForegroundColor Cyan
  $mcScript = @(
    "mc alias set vm http://${VmHost}:${MinioPort} ${minioUser} ${minioPass}"
    "mc alias set local http://minio:9000 ${minioUser} ${minioPass}"
    "mc mb --ignore-existing local/${bucket}"
    "mc mirror --overwrite --remove vm/${bucket} local/${bucket}"
  ) -join " && "

  docker run --rm --network "${Project}_default" `
    --add-host "host.docker.internal:host-gateway" `
    quay.io/minio/mc:latest `
    /bin/sh -c $mcScript

  if ($LASTEXITCODE -ne 0) {
    Write-Warning "MinIO mirror failed (exit $LASTEXITCODE). Check VM MinIO credentials / bucket."
  } else {
    Write-Host "MinIO sync complete." -ForegroundColor Green
  }
}

Write-Host ""
Write-Host "Done. Restart API/web to pick up synced data:" -ForegroundColor Green
Write-Host "  docker compose -f $ComposeFile -p $Project up -d api web" -ForegroundColor Green
