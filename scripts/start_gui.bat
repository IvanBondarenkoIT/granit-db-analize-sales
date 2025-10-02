@echo off
echo Запуск GUI приложения для анализа продаж кофе...
echo.

REM Переходим в директорию проекта
cd /d "d:\Cursor Projects\Granit DB analize sales"

REM Активируем виртуальное окружение
call venv\Scripts\activate.bat

REM Запускаем GUI приложение
python run_gui_with_logs.py

REM Пауза для просмотра ошибок (если есть)
pause
