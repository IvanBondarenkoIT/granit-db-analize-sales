# PowerShell скрипт для запуска GUI приложения
# Автоматически переходит в правильную директорию

Write-Host "=== ЗАПУСК GUI ПРИЛОЖЕНИЯ ===" -ForegroundColor Green
Write-Host ""

# Определяем путь к проекту
$ProjectPath = "d:\Cursor Projects\Granit DB analize sales"

# Проверяем существование директории проекта
if (-not (Test-Path $ProjectPath)) {
    Write-Host "ОШИБКА: Директория проекта не найдена: $ProjectPath" -ForegroundColor Red
    Write-Host "Текущая директория: $(Get-Location)" -ForegroundColor Yellow
    Write-Host "Доступные диски:" -ForegroundColor Yellow
    Get-PSDrive -PSProvider FileSystem | ForEach-Object { Write-Host "  $($_.Name):" -ForegroundColor Cyan }
    Read-Host "Нажмите Enter для выхода"
    exit 1
}

# Переходим в директорию проекта
Write-Host "Переход в директорию проекта: $ProjectPath" -ForegroundColor Yellow
Set-Location $ProjectPath

# Проверяем, что мы в правильной директории
Write-Host "Текущая директория: $(Get-Location)" -ForegroundColor Cyan

# Проверяем существование файла приложения
$GuiFile = "run_gui_with_logs.py"
if (-not (Test-Path $GuiFile)) {
    Write-Host "ОШИБКА: Файл $GuiFile не найден в директории проекта!" -ForegroundColor Red
    Write-Host "Доступные Python файлы:" -ForegroundColor Yellow
    Get-ChildItem -Name "*.py" | ForEach-Object { Write-Host "  $_" -ForegroundColor Cyan }
    Read-Host "Нажмите Enter для выхода"
    exit 1
}

# Проверяем существование виртуального окружения
if (Test-Path "venv\Scripts\activate.ps1") {
    Write-Host "Активация виртуального окружения..." -ForegroundColor Yellow
    try {
        & "venv\Scripts\activate.ps1"
        Write-Host "Виртуальное окружение активировано" -ForegroundColor Green
    } catch {
        Write-Host "Предупреждение: Не удалось активировать виртуальное окружение" -ForegroundColor Yellow
    }
} else {
    Write-Host "Виртуальное окружение не найдено. Используем системный Python." -ForegroundColor Yellow
}

# Запускаем GUI приложение
Write-Host ""
Write-Host "Запуск GUI приложения..." -ForegroundColor Green
Write-Host "===============================================" -ForegroundColor Cyan

try {
    python $GuiFile
} catch {
    Write-Host "ОШИБКА при запуске приложения: $($_.Exception.Message)" -ForegroundColor Red
    Write-Host "Попробуйте запустить вручную: python $GuiFile" -ForegroundColor Yellow
}

Write-Host ""
Write-Host "Приложение завершено. Нажмите любую клавишу для выхода..." -ForegroundColor Cyan
$null = $Host.UI.RawUI.ReadKey("NoEcho,IncludeKeyDown")
