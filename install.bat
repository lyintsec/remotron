@echo off
chcp 1251 >nul 2>&1

rem ��������� ������� ���� �������
mode con: cols=80 lines=25

rem �������� ��������� Python
python --version >nul 2>&1
if errorlevel 1 (
    echo Python �� ����������. ����������, ���������� Python � ���������� �����.
    timeout /t 10 >nul
    exit /b 1
)

rem �������� ��������� pip
python -m pip --version >nul 2>&1
if errorlevel 1 (
    echo pip �� ����������. ����������, ���������� pip � ���������� �����.
    timeout /t 10 >nul
    exit /b 1
)

rem �������� ��������� ������ venv
python -m venv --help >nul 2>&1
if errorlevel 1 (
    echo ������ venv �� ����������. ����������, ���������� Python � ���������� venv � ���������� �����.
    timeout /t 10 >nul
    exit /b 1
)

rem �������� ������������ ���������
echo �������� ������������ ���������...
python -m venv env
if errorlevel 1 (
    echo ��������� ������ ��� �������� ������������ ���������.
    timeout /t 10 >nul
    exit /b 1
)

rem ��������� ������������ ���������
echo ��������� ������������ ���������...
call env\Scripts\Activate.bat

rem ���������� pip
echo ���������� pip...
python -m pip install --upgrade pip >nul 2>&1
if errorlevel 1 (
    echo ������ ���������� pip
)

rem ��������� ������������
echo ��������� ������������...
python -m pip install -r requirements.txt >nul 2>&1
if errorlevel 1 (
    echo ��������� ������ ��� ��������� ������������.
    timeout /t 10 >nul
    exit /b 1
)

rem �������� ���������� � ������� pyinstaller
echo �������� ���������� � �������������� pyinstaller...
pyinstaller --noconfirm --onedir --windowed --log-level=ERROR --icon "data\remotron.ico" --name "Remotron" --clean --add-data "data;data/" "main.py"
if errorlevel 1 (
    echo ��������� ������ ��� �������� ����������.
    timeout /t 10 >nul
    exit /b 1
)

rem �������� ����� build � ����� .spec
rmdir /s /q build >nul 2>&1
del Remotron.spec >nul 2>&1

echo ��� ����������� �����������, � ���������� ������� ���������.
echo ����������� ���������� ��������� � ����� dist.
echo ���� ��������� ����� 10 ������...

timeout /t 10

exit /b 0
