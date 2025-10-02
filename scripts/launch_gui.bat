@echo off
echo ===============================================
echo    ЗАПУСК GUI ПРИЛОЖЕНИЯ ДЛЯ АНАЛИЗА КОФЕ
echo ===============================================
echo.

REM Переходим в директорию проекта
cd /d "d:\Cursor Projects\Granit DB analize sales"

REM Проверяем, что мы в правильной директории
echo Текущая директория: %CD%
echo.

REM Проверяем существование файла приложения
if not exist "run_gui_with_logs.py" (
    echo ОШИБКА: Файл run_gui_with_logs.py не найден!
    echo Доступные Python файлы:
    dir *.py /b
    echo.
    pause
    exit /b 1
)

REM Активируем виртуальное окружение (если существует)
if exist "venv\Scripts\activate.bat" (
    echo Активация виртуального окружения...
    call venv\Scripts\activate.bat
    echo Виртуальное окружение активировано
) else (
    echo Виртуальное окружение не найдено. Используем системный Python.
)

echo.
echo Запуск GUI приложения...
echo ===============================================
echo.

REM Запускаем GUI приложение
python run_gui_with_logs.py

echo.
echo Приложение завершено.
pause
