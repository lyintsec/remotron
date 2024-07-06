@echo off
chcp 1251 >nul 2>&1

rem Установка размера окна консоли
mode con: cols=80 lines=25

rem Проверка установки Python
python --version >nul 2>&1
if errorlevel 1 (
    echo Python не установлен. Пожалуйста, установите Python и попробуйте снова.
    timeout /t 10 >nul
    exit /b 1
)

rem Проверка установки pip
python -m pip --version >nul 2>&1
if errorlevel 1 (
    echo pip не установлен. Пожалуйста, установите pip и попробуйте снова.
    timeout /t 10 >nul
    exit /b 1
)

rem Проверка установки модуля venv
python -m venv --help >nul 2>&1
if errorlevel 1 (
    echo Модуль venv не установлен. Пожалуйста, установите Python с поддержкой venv и попробуйте снова.
    timeout /t 10 >nul
    exit /b 1
)

rem Создание виртуального окружения
echo Создание виртуального окружения...
python -m venv env
if errorlevel 1 (
    echo Произошла ошибка при создании виртуального окружения.
    timeout /t 10 >nul
    exit /b 1
)

rem Активация виртуального окружения
echo Активация виртуального окружения...
call env\Scripts\Activate.bat

rem Обновление pip
echo Обновление pip...
python -m pip install --upgrade pip >nul 2>&1
if errorlevel 1 (
    echo Ошибка обновления pip
)

rem Установка зависимостей
echo Установка зависимостей...
python -m pip install -r requirements.txt >nul 2>&1
if errorlevel 1 (
    echo Произошла ошибка при установке зависимостей.
    timeout /t 10 >nul
    exit /b 1
)

rem Упаковка приложения с помощью pyinstaller
echo Упаковка приложения с использованием pyinstaller...
pyinstaller --noconfirm --onedir --windowed --log-level=ERROR --icon "data\remotron.ico" --name "Remotron" --clean --add-data "data;data/" "main.py"
if errorlevel 1 (
    echo Произошла ошибка при упаковке приложения.
    timeout /t 10 >nul
    exit /b 1
)

rem Удаление папки build и файла .spec
rmdir /s /q build >nul 2>&1
del Remotron.spec >nul 2>&1

echo Все зависимости установлены, и приложение успешно упаковано.
echo Упакованное приложение находится в папке dist.
echo Окно закроется через 10 секунд...

timeout /t 10

exit /b 0
