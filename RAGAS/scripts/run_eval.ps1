param(
    [int]$MaxSamples = 0,
    [switch]$UpdateBaseline,
    [switch]$FailOnRegression
)

Set-Location $PSScriptRoot\..

if (-not (Test-Path ".env")) {
    Copy-Item ".env.example" ".env"
    Write-Host "Created .env from .env.example. Update OPENAI_API_KEY and EVAL_SECRET before running."
}

$argsList = @()
if ($MaxSamples -gt 0) {
    $argsList += @("--max-samples", "$MaxSamples")
}
if ($UpdateBaseline) {
    $argsList += "--update-baseline"
}
if ($FailOnRegression) {
    $argsList += "--fail-on-regression"
}

uv run ragas-eval @argsList
