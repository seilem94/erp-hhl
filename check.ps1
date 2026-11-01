Write-Host "--- 1. Validando Backend ---" -ForegroundColor Cyan
Set-Location backend
.\venv\Scripts\ruff check .
.\venv\Scripts\ruff format --check .
.\venv\Scripts\mypy src/
Set-Location ..

Write-Host "`n--- 2. Validando Frontend ---" -ForegroundColor Cyan
Set-Location frontend
npm run lint
npm run type-check
Set-Location ..

Write-Host "`n[OK] Todo validado con exito." -ForegroundColor Green
