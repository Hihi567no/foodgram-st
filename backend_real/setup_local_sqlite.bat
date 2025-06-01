@echo off
echo 🍽️ Foodgram Backend Local Setup with SQLite
echo ==================================================

REM Check if virtual environment exists
if not exist "venv" (
    echo 📦 Creating virtual environment...
    python -m venv venv
    if errorlevel 1 (
        echo ❌ Failed to create virtual environment
        pause
        exit /b 1
    )
)

REM Activate virtual environment
echo 🔄 Activating virtual environment...
call venv\Scripts\activate.bat

REM Install requirements
echo 📦 Installing requirements...
pip install -r requirements.txt
if errorlevel 1 (
    echo ❌ Failed to install requirements
    pause
    exit /b 1
)

REM Run setup script
echo 🔄 Running setup script...
python setup_local_sqlite.py
if errorlevel 1 (
    echo ❌ Setup script failed
    pause
    exit /b 1
)

echo.
echo 🎉 Setup completed successfully!
echo.
echo To start the server, run:
echo   venv\Scripts\activate.bat
echo   python manage.py runserver
echo.
pause
