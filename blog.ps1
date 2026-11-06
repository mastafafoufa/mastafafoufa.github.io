$python = Join-Path $PSScriptRoot '.venv\Scripts\python.exe'
$script = Join-Path $PSScriptRoot 'scripts\blog.py'
if (-not (Test-Path -LiteralPath $python)) {
    Write-Error 'Set up blog authoring first: python -m venv .venv; .\.venv\Scripts\python.exe -m pip install -r requirements.txt'
    exit 1
}
& $python -X utf8 $script @args
exit $LASTEXITCODE
