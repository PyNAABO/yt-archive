<#
    Refresh the archive and publish it.

    Runs: cookies -> download -> rebuild -> sanity check -> commit -> push.
    Cookies come from the saved browser session and are deleted again afterwards.

    .EXAMPLE
    .\refresh.ps1

    .EXAMPLE
    .\refresh.ps1 -Root 'C:\Users\mhodn\Desktop\Essentials\NAABO\YouTube\ne00sa'   # old account
    .\refresh.ps1 -SkipPush                                                       # dry run
#>
param(
    [string]$Root = (Resolve-Path "$PSScriptRoot\..").Path,
    [switch]$SkipPush
)

$ErrorActionPreference = 'Stop'
$Root = (Resolve-Path $Root).Path
$env:YT_ROOT = $Root

$py = 'C:\Python314\python.exe'
if (-not (Test-Path $py)) { $py = (Get-Command py -ErrorAction SilentlyContinue).Source }
if (-not $py) { throw 'No Python found.' }

$cookies = Join-Path $Root 'cookies.txt'
$state = 'C:\.playwright-mcp\yt_state.json'
$wl = Join-Path $Root 'watch_later.json'

Push-Location $Root
try {
    if (-not (Test-Path $cookies)) {
        if (-not (Test-Path $state)) {
            throw "No cookies.txt and no browser state at $state. Save the session from the agent first."
        }
        & $py (Join-Path $PSScriptRoot 'state2cookies.py')
    }

    $before = 0
    $liveBefore = 0
    if (Test-Path $wl) {
        $prev = (Get-Content $wl -Raw | ConvertFrom-Json)
        $before = $prev.count
        $liveBefore = @($prev.videos | Where-Object { $_.title -and $_.title -notmatch '^\[(Private|Deleted) video\]$' }).Count
    }

    & $py (Join-Path $PSScriptRoot 'export_playlists.py')
    if ($LASTEXITCODE -ne 0) { throw "export_playlists.py failed ($LASTEXITCODE)" }
    & $py (Join-Path $PSScriptRoot 'export_subscriptions.py') 2>&1 | Select-Object -Last 6
    if ($LASTEXITCODE -ne 0) { 'subscriptions refresh failed, keeping the old file' }
    & $py (Join-Path $PSScriptRoot 'finalize_export.py')
    if ($LASTEXITCODE -ne 0) { throw "finalize_export.py failed ($LASTEXITCODE)" }

    $after = (Get-Content $wl -Raw | ConvertFrom-Json).count
    if ($before -gt 0 -and $after -lt ($before * 0.5)) {
        throw "Watch Later shrank from $before to $after. Nothing committed. Restore with: git checkout -- ."
    }
    $liveAfter = @((Get-Content $wl -Raw | ConvertFrom-Json).videos |
        Where-Object { $_.title -and $_.title -notmatch '^\[(Private|Deleted) video\]$' }).Count
    if ($liveBefore -gt 0 -and $liveAfter -lt ($liveBefore - 20)) {
        throw "Titled entries dropped from $liveBefore to $liveAfter - the fetch was partial. Nothing committed. Restore with: git checkout -- ."
    }
    "watch later: $before -> $after ($liveBefore -> $liveAfter with a title)"

    & $py (Join-Path $PSScriptRoot 'diff_exports.py') 2>&1 | Select-Object -First 40

    Remove-Item $cookies -ErrorAction SilentlyContinue
    Remove-Item (Join-Path $Root 'raw') -Recurse -Force -ErrorAction SilentlyContinue

    git add -A
    if (git status --porcelain) {
        git -c user.name='PyNAABO' -c user.email='pynaabo@users.noreply.github.com' commit -m ('refresh ' + (Get-Date -Format 'yyyy-MM-dd HH:mm')) | Out-Null
        if ($SkipPush) {
            'committed, not pushed (-SkipPush)'
        } else {
            git push 2>&1 | Select-Object -Last 2
            if ($LASTEXITCODE -ne 0) {
                # yt-archive belongs to PyNAABO; gh flips to nabhan-007 and pushes 403
                gh auth switch --user PyNAABO | Out-Null
                git push 2>&1 | Select-Object -Last 2
            }
        }
    } else {
        'no changes'
    }
}
finally {
    Pop-Location
}
