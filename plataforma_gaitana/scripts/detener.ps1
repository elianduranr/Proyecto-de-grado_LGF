[Console]::OutputEncoding = New-Object System.Text.UTF8Encoding
$env:PYTHONIOENCODING = 'utf-8'
$projectRoot = Split-Path -Parent $PSScriptRoot
$recordPath = Join-Path $projectRoot 'storage\processes.json'
if (-not (Test-Path -LiteralPath $recordPath)) { Write-Host 'No hay procesos registrados.'; exit }
$records = @()
$parsed = Get-Content -LiteralPath $recordPath -Raw | ConvertFrom-Json
foreach ($item in $parsed) { $records += $item }
$previousPath = Join-Path $projectRoot 'storage\processes.previous.json'
if (Test-Path -LiteralPath $previousPath) {
    $parsed = Get-Content -LiteralPath $previousPath -Raw | ConvertFrom-Json
    foreach ($item in $parsed) { $records += $item }
}
foreach ($record in $records) {
    $running = Get-Process -Id $record.id -ErrorAction SilentlyContinue
    if ($running -and -not $running.StartTime) { throw "No se puede verificar el inicio del proceso $($record.id). Reinicia este comando con permisos suficientes; se conservará el registro." }
    if ($running -and $running.StartTime.ToUniversalTime().Ticks -eq $record.start) {
        # Incluye los hijos del lanzador de Python de Windows, sólo tras validar
        # PID y fecha de inicio de la ejecución registrada.
        & taskkill.exe /PID $running.Id /T /F | Out-Null
        if ($LASTEXITCODE -ne 0) { throw "No se pudo detener el proceso $($running.Id). No se declarará detenido hasta verificarlo." }
    }
}
Set-Content -LiteralPath $recordPath -Value '[]' -Encoding UTF8
if (Test-Path -LiteralPath $previousPath) { Set-Content -LiteralPath $previousPath -Value '[]' -Encoding UTF8 }
Write-Host 'Procesos de esta ejecución detenidos. Los datos y versiones se conservan.'
