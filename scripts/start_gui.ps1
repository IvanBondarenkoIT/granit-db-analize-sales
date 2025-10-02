# PowerShell скрипт для запуска GUI приложения
Write-Host "Запуск GUI приложения для анализа продаж кофе..." -ForegroundColor Green
Write-Host ""

# Переходим в директорию проекта
Set-Location "d:\Cursor Projects\Granit DB analize sales"

# Проверяем существование виртуального окружения
if (Test-Path "venv\Scripts\activate.ps1") {
    Write-Host "Активация виртуального окружения..." -ForegroundColor Yellow
    & "venv\Scripts\activate.ps1"
} else {
    Write-Host "Виртуальное окружение не найдено. Используем системный Python." -ForegroundColor Yellow
}

# Проверяем существование файла приложения
if (Test-Path "run_gui_with_logs.py") {
    Write-Host "Запуск GUI приложения..." -ForegroundColor Yellow
    python run_gui_with_logs.py
} else {
    Write-Host "Файл run_gui_with_logs.py не найден!" -ForegroundColor Red
    Write-Host "Доступные Python файлы:" -ForegroundColor Yellow
    Get-ChildItem -Name "*.py" | ForEach-Object { Write-Host "  $_" }
}

Write-Host ""
Write-Host "Нажмите любую клавишу для выхода..." -ForegroundColor Cyan
$null = $Host.UI.RawUI.ReadKey("NoEcho,IncludeKeyDown")
