@echo off
cd /d "%~dp0"
echo Проверка зависимостей...
py -m pip install -r requirements.txt --quiet
echo Запуск игры...
py src/main.py
pause