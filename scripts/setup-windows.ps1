# Ejecutar con PowerShell desde la raíz del proyecto.
$ErrorActionPreference = 'Stop'
Set-Location (Split-Path -Parent $PSScriptRoot)
$rng = [System.Security.Cryptography.RandomNumberGenerator]::Create()
try {
  if (-not (Test-Path .env)) {
    $dbBytes = New-Object byte[] 24
    $rng.GetBytes($dbBytes)
    $dbSecret = [System.BitConverter]::ToString($dbBytes).Replace('-', '')
    $content = [System.IO.File]::ReadAllText((Join-Path (Get-Location) '.env.example'))
    $content = $content.Replace('CHANGE_ME_DB_RANDOM_SECRET', $dbSecret)
    [System.IO.File]::WriteAllText((Join-Path (Get-Location) '.env'), $content)
    Write-Host 'Archivo .env creado únicamente para PostgreSQL (NO subir a Git).'
  } else { Write-Host '.env ya existe; no se ha modificado.' }

  if (-not (Test-Path backend/.env)) {
    $jwtBytes = New-Object byte[] 48
    $rng.GetBytes($jwtBytes)
    $jwtSecret = [System.BitConverter]::ToString($jwtBytes).Replace('-', '')
    $backendContent = [System.IO.File]::ReadAllText((Join-Path (Get-Location) 'backend/.env.example'))
    $backendContent = $backendContent.Replace('CHANGE_ME_JWT_RANDOM_SECRET_MIN_32_CHARS', $jwtSecret)
    [System.IO.File]::WriteAllText((Join-Path (Get-Location) 'backend/.env'), $backendContent)
    Write-Host 'backend/.env creado con secreto JWT aleatorio (NO subir a Git).'
  } else { Write-Host 'backend/.env ya existe; no se ha modificado.' }
} finally { $rng.Dispose() }

if (-not (Test-Path frontend/.env)) {
  Copy-Item frontend/.env.example frontend/.env
  Write-Host 'frontend/.env creado para desarrollo local.'
} else { Write-Host 'frontend/.env ya existe; no se ha modificado.' }
if (Get-Command npm -ErrorAction SilentlyContinue) {
  Push-Location frontend
  try {
    npm install --package-lock-only --no-audit --no-fund
    if ($LASTEXITCODE -ne 0) { throw 'No se pudo generar package-lock.json (verifica acceso a npm).' }
    Write-Host 'frontend/package-lock.json generado: versionarlo en Git.'
  } finally { Pop-Location }
} else {
  Write-Warning 'No se encontró npm: instala Node 20 y ejecuta `cd frontend; npm install` antes del PR.'
}
Write-Host 'Arranque Docker: docker compose -f docker-compose.yml up --build -d'
