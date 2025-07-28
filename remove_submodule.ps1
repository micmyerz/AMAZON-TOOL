# remove_submodule.ps1
$gitmodulesPath = ".gitmodules"

if (Test-Path $gitmodulesPath) {
    $lines = Get-Content $gitmodulesPath
    $insideBlock = $false
    $newLines = @()

    foreach ($line in $lines) {
        # Start of the KennethStewart submodule block
        if ($line -match '^\[submodule "KennethStewart"\]') {
            $insideBlock = $true
            continue
        }
        # Blank line signals end of block, stop skipping
        if ($insideBlock -and ($line.Trim() -eq '')) {
            $insideBlock = $false
            continue
        }
        # Skip all lines while inside the block
        if (-not $insideBlock) {
            $newLines += $line
        }
    }

    # Save the cleaned .gitmodules file
    $newLines | Set-Content $gitmodulesPath
    Write-Host "Removed KennethStewart submodule block from .gitmodules"
} else {
    Write-Host ".gitmodules file not found"
}
