<#
.SYNOPSIS
  Sync current HEAD to moksh-sharma/iConnectPlus-ERP with all commits attributed to the repo owner.

.DESCRIPTION
  Creates a temporary rewritten history (author + committer = owner), force-pushes to
  iconnectplus-erp, then deletes the temporary branch. Does NOT rewrite origin/main.
#>
param(
  [string]$Branch = "",
  [string]$OwnerName = "Moksh Sharma",
  [string]$OwnerEmail = "moksh-sharma@users.noreply.github.com",
  [string]$Remote = "iconnectplus-erp",
  [string]$RemoteBranch = "main"
)

$ErrorActionPreference = "Continue"
# Native git writes warnings to stderr; only throw on explicit checks below.

$repoRoot = (git rev-parse --show-toplevel 2>$null)
if (-not $repoRoot) { throw "Not inside a git repository." }
Set-Location $repoRoot

if (-not $Branch) {
  $Branch = (git rev-parse --abbrev-ref HEAD).Trim()
}
if ($Branch -eq "HEAD") { throw "Detached HEAD is not supported; check out a branch first." }

$remoteUrl = git remote get-url $Remote 2>$null
if (-not $remoteUrl) {
  git remote add $Remote "https://github.com/moksh-sharma/iConnectPlus-ERP.git"
  $remoteUrl = git remote get-url $Remote
}

$tempBranch = "tmp/iconnectplus-erp-owner-mirror"
Write-Host "Source: $Branch @ $(git rev-parse --short HEAD)"
Write-Host "Owner:  $OwnerName <$OwnerEmail>"
Write-Host "Target: $Remote ($remoteUrl) -> $RemoteBranch"

# Fresh temp branch from current tip
git show-ref --verify --quiet "refs/heads/$tempBranch"
if ($LASTEXITCODE -eq 0) {
  git branch -D $tempBranch | Out-Null
}
git branch $tempBranch $Branch
if ($LASTEXITCODE -ne 0) { throw "Failed to create temp branch $tempBranch" }

$envFilter = @"
export GIT_AUTHOR_NAME='$OwnerName'
export GIT_AUTHOR_EMAIL='$OwnerEmail'
export GIT_COMMITTER_NAME='$OwnerName'
export GIT_COMMITTER_EMAIL='$OwnerEmail'
"@

Write-Host "Rewriting authors on $tempBranch ..."
# filter-branch needs sh; Git for Windows provides it
$env:FILTER_BRANCH_SQUELCH_WARNING = "1"
git filter-branch -f --env-filter $envFilter $tempBranch
if ($LASTEXITCODE -ne 0) {
  git branch -D $tempBranch 2>$null | Out-Null
  git update-ref -d "refs/original/refs/heads/$tempBranch" 2>$null | Out-Null
  throw "git filter-branch failed"
}

Write-Host "Force-pushing rewritten history to ${Remote}:${RemoteBranch} ..."
git push --force $Remote "${tempBranch}:${RemoteBranch}"
if ($LASTEXITCODE -ne 0) {
  git branch -D $tempBranch 2>$null | Out-Null
  git update-ref -d "refs/original/refs/heads/$tempBranch" 2>$null | Out-Null
  throw "Force push to $Remote failed"
}

# Cleanup
git branch -D $tempBranch | Out-Null
git update-ref -d "refs/original/refs/heads/$tempBranch" 2>$null | Out-Null
# Drop backup refs left by filter-branch
git for-each-ref --format="%(refname)" refs/original/ | ForEach-Object { git update-ref -d $_ 2>$null }

Write-Host "Done. $Remote now shows only $OwnerName as commit author."
