# Set console window size
$Host.UI.RawUI.WindowSize = New-Object Management.Automation.Host.Size(80, 25)

# Check Python installation
& python --version 2>&1 | Out-Null
if ($LASTEXITCODE -ne 0) {
    Write-Host "Python is not installed. Please install Python and try again."
    Start-Sleep -Seconds 10
    exit 1
}

# Check pip installation
& python -m pip --version 2>&1 | Out-Null
if ($LASTEXITCODE -ne 0) {
    Write-Host "pip is not installed. Please install pip and try again."
    Start-Sleep -Seconds 10
    exit 1
}

# Check venv module installation
& python -m venv --help 2>&1 | Out-Null
if ($LASTEXITCODE -ne 0) {
    Write-Host "venv module is not installed. Please install Python with venv support and try again."
    Start-Sleep -Seconds 10
    exit 1
}

# Create virtual environment
Write-Host "Creating virtual environment..."
& python -m venv env 2>&1 | Out-Null
if ($LASTEXITCODE -ne 0) {
    Write-Host "An error occurred while creating the virtual environment."
    Start-Sleep -Seconds 10
    exit 1
}

# Activate virtual environment
Write-Host "Activating virtual environment..."
& .\env\Scripts\Activate.ps1 2>&1 | Out-Null

# pip upgrade
Write-Host "Upgrading pip..."
& python -m pip install --upgrade pip 2>&1 | Out-Null
if ($LASTEXITCODE -ne 0) {
    Write-Host "An error occurred while upgrading pip."
}

# Install dependencies
Write-Host "Installing dependencies..."
& python -m pip install -r requirements.txt 2>&1 | Out-Null
if ($LASTEXITCODE -ne 0) {
    Write-Host "An error occurred while installing dependencies."
    Start-Sleep -Seconds 10
    exit 1
}

# Package the application using pyinstaller
Write-Host "Packaging application using pyinstaller..."
& pyinstaller --noconfirm --onedir --windowed --log-level=ERROR --icon "data\remotron.ico" --name "Remotron" --clean --add-data "data;data/" "main.py"
if ($LASTEXITCODE -ne 0) {
    Write-Host "An error occurred while packaging the application."
    Start-Sleep -Seconds 10
    exit 1
}

# Remove build folder and .spec file
Remove-Item -Recurse -Force "build" 2>&1 | Out-Null
Remove-Item -Force "Remotron.spec" 2>&1 | Out-Null

Write-Host "All dependencies are installed and the application is successfully packaged."
Write-Host "The packaged application is located in the dist folder."
Write-Host "This window will close in 15 seconds..."

Start-Sleep -Seconds 15
exit 0
