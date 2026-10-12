<#
.SYNOPSIS
  Rewrite commit authors to the repo owner and force-push to GitHub remotes.

.DESCRIPTION
  Builds a temporary history where every author/committer is the owner, force-pushes
  to the listed remotes, then resets local branch to that rewritten tip.

  Default remotes: origin, iconnectplus, iconnectplus-erp.
#>
param(
  [string]$Branch = "",
  [string]$OwnerName = "Moksh Sharma",
  [string]$OwnerEmail = "moksh-sharma@users.noreply.github.com",
  [string[]]$Remotes = @("origin", "iconnectplus", "iconnectplus-erp"),
  [string]$RemoteBranch = "main",
  [switch]$SkipLocalReset
)

$ErrorActionPreference = "Continue"

$repoRoot = (git rev-parse --show-toplevel 2>$null)
if (-not $repoRoot) { throw "Not inside a git repository." }
Set-Location $repoRoot

if (-not $Branch) {
  $Branch = (git rev-parse --abbrev-ref HEAD).Trim()
}
if ($Branch -eq "HEAD") { throw "Detached HEAD is not supported; check out a branch first." }

# Ensure personal mirror remote exists
$erpUrl = "https://github.com/moksh-sharma/iConnectPlus-ERP.git"
git remote get-url iconnectplus-erp 2>$null | Out-Null
if ($LASTEXITCODE -ne 0) {
  git remote add iconnectplus-erp $erpUrl
}

$tempBranch = "tmp/owner-history-mirror"
Write-Host "Source: $Branch @ $(git rev-parse --short HEAD)"
Write-Host "Owner:  $OwnerName <$OwnerEmail>"
Write-Host "Remotes: $($Remotes -join ', ') -> $RemoteBranch"

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
$env:FILTER_BRANCH_SQUELCH_WARNING = "1"
git filter-branch -f --env-filter $envFilter $tempBranch
if ($LASTEXITCODE -ne 0) {
  git branch -D $tempBranch 2>$null | Out-Null
  throw "git filter-branch failed"
}

$rewritten = (git rev-parse $tempBranch).Trim()
Write-Host "Rewritten tip: $rewritten"

foreach ($remote in $Remotes) {
  git remote get-url $remote 2>$null | Out-Null
  if ($LASTEXITCODE -ne 0) {
    Write-Host "Skip missing remote: $remote"
    continue
  }
  Write-Host "Force-pushing to ${remote}:${RemoteBranch} ..."
  # Push by SHA to avoid relying on dual pushurl side effects for named remotes
  if ($remote -eq "origin") {
    # Push only the primary origin URL first, then org mirror, to make failures clear
    $primary = (git remote get-url origin).Trim()
    git push --force $primary "${rewritten}:refs/heads/$RemoteBranch"
    if ($LASTEXITCODE -ne 0) { throw "Force push to origin primary failed" }
    $extra = git config --get-all remote.origin.pushurl 2>$null
    foreach ($url in $extra) {
      if ($url -and ($url -ne $primary)) {
        Write-Host "Force-pushing origin pushurl: $url"
        git push --force $url "${rewritten}:refs/heads/$RemoteBranch"
        if ($LASTEXITCODE -ne 0) { throw "Force push to $url failed" }
      }
    }
  } else {
    git push --force $remote "${rewritten}:refs/heads/$RemoteBranch"
    if ($LASTEXITCODE -ne 0) { throw "Force push to $remote failed" }
  }
}

if (-not $SkipLocalReset) {
  Write-Host "Resetting local $Branch to rewritten tip ..."
  git checkout $Branch | Out-Null
  git reset --hard $rewritten
  if ($LASTEXITCODE -ne 0) { throw "Failed to reset local $Branch" }
  git branch -u "origin/$RemoteBranch" $Branch 2>$null | Out-Null
}

git branch -D $tempBranch | Out-Null
git for-each-ref --format="%(refname)" refs/original/ | ForEach-Object { git update-ref -d $_ 2>$null }

Write-Host "Done. Remotes now show only $OwnerName as commit author."
git shortlog -sne HEAD | Select-Object -First 5
