[Console]::OutputEncoding = New-Object System.Text.UTF8Encoding
$env:PYTHONIOENCODING = 'utf-8'
$ErrorActionPreference = 'Stop'
$projectRoot = Split-Path -Parent $PSScriptRoot
$pythonPath = Join-Path $projectRoot '.venv\Scripts\python.exe'
if (-not (Test-Path -LiteralPath $pythonPath)) { throw 'Primero ejecuta instalar.cmd.' }
& $pythonPath (Join-Path $PSScriptRoot 'configurar.py')
if ($LASTEXITCODE -ne 0) { throw 'No se pudo preparar la configuración.' }
$occupiedPorts = @()
foreach ($listenPort in @(8000,5173)) {
    $probe = New-Object System.Net.Sockets.TcpClient
    $occupied = $false
    try { $probe.Connect('127.0.0.1', $listenPort); $occupied = $true } catch { } finally { $probe.Dispose() }
    if ($occupied) { $occupiedPorts += $listenPort }
}
if ($occupiedPorts.Count -eq 2) {
    try {
        $existingApi = Invoke-RestMethod -Uri 'http://127.0.0.1:8000/openapi.json' -TimeoutSec 3
        $existingWeb = Invoke-WebRequest -Uri 'http://127.0.0.1:5173' -UseBasicParsing -TimeoutSec 3
        if ($existingApi.info.title -like 'La Gaitana*' -and $existingWeb.Content -like '*<title>La Gaitana*') {
            Write-Host 'El prototipo ya esta disponible: http://localhost:5173'
            exit 0
        }
    } catch { }
}
if ($occupiedPorts.Count -gt 0) { throw "Hay puertos ocupados: $occupiedPorts. Si es este prototipo, ejecuta detener.cmd antes de reiniciar." }
Push-Location (Join-Path $projectRoot 'backend')
try { & $pythonPath -m alembic upgrade head; if ($LASTEXITCODE -ne 0) { throw 'Fallaron las migraciones.' } }
finally { Pop-Location }
$logsPath = Join-Path $projectRoot 'storage'
$startedProcesses = @()
try {
    $backendProcess = Start-Process -FilePath $pythonPath -ArgumentList @('-m','uvicorn','app.main:app','--host','127.0.0.1','--port','8000') -WorkingDirectory (Join-Path $projectRoot 'backend') -WindowStyle Hidden -PassThru -RedirectStandardOutput (Join-Path $logsPath 'api.out.log') -RedirectStandardError (Join-Path $logsPath 'api.err.log')
    $startedProcesses += $backendProcess
    $workerScript = Join-Path $PSScriptRoot 'run_worker.py'
    $workerProcess = Start-Process -FilePath $pythonPath -ArgumentList @('"' + $workerScript + '"') -WorkingDirectory (Join-Path $projectRoot 'backend') -WindowStyle Hidden -PassThru -RedirectStandardOutput (Join-Path $logsPath 'worker.out.log') -RedirectStandardError (Join-Path $logsPath 'worker.err.log')
    $startedProcesses += $workerProcess
    $viteScript = Join-Path $projectRoot 'frontend\node_modules\vite\bin\vite.js'
    $webProcess = Start-Process -FilePath 'node.exe' -ArgumentList @('"' + $viteScript + '"','--host','127.0.0.1','--port','5173') -WorkingDirectory (Join-Path $projectRoot 'frontend') -WindowStyle Hidden -PassThru -RedirectStandardOutput (Join-Path $logsPath 'web.out.log') -RedirectStandardError (Join-Path $logsPath 'web.err.log')
    $startedProcesses += $webProcess
    $recordPath = Join-Path $logsPath 'processes.json'
    $records = @()
    if (Test-Path -LiteralPath $recordPath) {
        $previousRecords = Get-Content -LiteralPath $recordPath -Raw | ConvertFrom-Json
        foreach ($item in $previousRecords) { $records += $item }
    }
    foreach ($item in $startedProcesses) { $records += @{id=$item.Id;start=$item.StartTime.ToUniversalTime().Ticks} }
    ConvertTo-Json -InputObject $records | Set-Content -LiteralPath $recordPath -Encoding UTF8
    $ready = $false
    for ($attempt=0; $attempt -lt 20; $attempt++) {
        try {
            $null = Invoke-WebRequest -Uri 'http://127.0.0.1:8000/api/health' -UseBasicParsing -TimeoutSec 2
            $null = Invoke-WebRequest -Uri 'http://127.0.0.1:5173' -UseBasicParsing -TimeoutSec 2
            $ready = $true; break
        } catch { Start-Sleep -Milliseconds 500 }
    }
    if (-not $ready) { throw 'Los servicios no arrancaron. Revisa los logs de storage/.' }
    Write-Host 'Interfaz: http://localhost:5173'
    Write-Host 'API y documentación: http://localhost:8000/docs'
    Write-Host 'Los servicios tardan unos segundos en estar listos. Logs en storage/.'
    Write-Host 'Para detener sólo estos procesos: .\detener.cmd'
} catch {
    foreach ($started in $startedProcesses) { & taskkill.exe /PID $started.Id /T /F | Out-Null }
    throw
}
