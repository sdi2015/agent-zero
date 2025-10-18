param(
  [switch]$AgentOnly
)
$ErrorActionPreference = "Stop"
Set-Location "$PSScriptRoot"
.\.venv\Scripts\Activate.ps1
if (-not $env:OPENAI_API_KEY) { Write-Warning "OPENAI_API_KEY not set" }
if ($AgentOnly) { python .\agent.py } else { python .\run_ui.py }
