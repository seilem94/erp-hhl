Write-Host "Iniciando HHL ERP - Entorno de Desarrollo Local" -ForegroundColor Cyan
Start-Process powershell -ArgumentList "-NoExit", "-Command", "cd backend; .\venv\Scripts\Activate.ps1; python -m uvicorn src.main:app --reload --port 8000"
Start-Process powershell -ArgumentList "-NoExit", "-Command", "cd frontend; npm run dev"
Write-Host "Servicios iniciados en ventanas separadas." -ForegroundColor Green
