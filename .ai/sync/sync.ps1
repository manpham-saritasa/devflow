# Sync .ai/rules/core.md to your AI tool's root file
# Usage: .\sync.ps1 zed | cursor | copilot | claude | gemini | windsurf | codeium | aider | jetbrains | all
param([string]$Tool = "all")

$source = ".ai/rules/core.md"
$tools = @{
    zed       = @{ Path = ".rules";                    Type = "symlink" }
    claude    = @{ Path = "CLAUDE.md";                  Type = "symlink" }
    gemini    = @{ Path = "GEMINI.md";                  Type = "symlink" }
    windsurf  = @{ Path = ".windsurfrules";             Type = "symlink" }
    codeium   = @{ Path = ".codeiumrules";              Type = "symlink" }
    aider     = @{ Path = "CONVENTIONS.md";             Type = "symlink" }
    cursor    = @{ Path = ".cursor/rules/main.mdc";     Type = "copy" }
    copilot   = @{ Path = ".github/copilot-instructions.md"; Type = "copy" }
    jetbrains = @{ Path = ".rules";                     Type = "symlink" }
}

function Sync-One($name, $cfg) {
    $dir = Split-Path $cfg.Path -Parent
    if ($dir -and !(Test-Path $dir)) {
        New-Item -ItemType Directory -Force -Path $dir | Out-Null
    }
    if ($cfg.Type -eq "symlink") {
        if (Test-Path $cfg.Path) { Remove-Item $cfg.Path -Force }
        python -c "import os; os.symlink('$source', '$($cfg.Path)')"
        Write-Host "  $name -> $($cfg.Path) (symlink)"
    } else {
        Copy-Item $source $cfg.Path -Force
        Write-Host "  $name -> $($cfg.Path) (copy)"
    }
}

if ($Tool -eq "all") {
    Write-Host "Syncing all tools..."
    foreach ($name in $tools.Keys) {
        Sync-One $name $tools[$name]
    }
} elseif ($tools.ContainsKey($Tool)) {
    Write-Host "Syncing $Tool..."
    Sync-One $Tool $tools[$Tool]
} else {
    Write-Host "Unknown tool: $Tool"
    Write-Host "Usage: sync.ps1 [zed|cursor|copilot|claude|gemini|windsurf|codeium|aider|jetbrains|all]"
    exit 1
}

Write-Host "Done."
