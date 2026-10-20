# Ejecutar con PowerShell desde la raíz del proyecto.
$ErrorActionPreference = 'Stop'
Set-Location (Split-Path -Parent $PSScriptRoot)
if (-not (Test-Path .env)) {
  $rng = [System.Security.Cryptography.RandomNumberGenerator]::Create()
  try {
    $dbBytes = New-Object byte[] 24
    $jwtBytes = New-Object byte[] 48
    $rng.GetBytes($dbBytes)
    $rng.GetBytes($jwtBytes)
    $dbSecret = [System.BitConverter]::ToString($dbBytes).Replace('-', '')
    $jwtSecret = [System.BitConverter]::ToString($jwtBytes).Replace('-', '')
  } finally { $rng.Dispose() }
  $content = [System.IO.File]::ReadAllText((Join-Path (Get-Location) '.env.example'))
  $content = $content.Replace('CHANGE_ME_DB_RANDOM_SECRET', $dbSecret).Replace('CHANGE_ME_JWT_RANDOM_SECRET_MIN_32_CHARS', $jwtSecret)
  [System.IO.File]::WriteAllText((Join-Path (Get-Location) '.env'), $content)
  Write-Host 'Archivo .env creado con contraseñas aleatorias (NO subir a Git).'
} else { Write-Host '.env ya existe; no se ha modificado.' }
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
Write-Host 'Arranque Docker: docker compose up --build -d'
