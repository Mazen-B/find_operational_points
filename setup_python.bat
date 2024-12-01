@echo off
SETLOCAL

:: var to track if any errors occur
SET "ERROR_OCCURRED=0"

:: check if Python3 is installed
python3 --version >nul 2>&1
IF ERRORLEVEL 1 (
    echo Python3 is not installed or not recognized.
    echo Checking for 'python' command instead...

    python --version >nul 2>&1
    IF ERRORLEVEL 1 (
        echo Python is not installed. Attempting to install Python...
        curl -o python_installer.exe https://www.python.org/ftp/python/3.10.0/python-3.10.0-amd64.exe
        IF ERRORLEVEL 1 (
            echo Failed to download Python installer. Please check your internet connection.
            SET ERROR_OCCURRED=1
        ) ELSE (
            echo Installing Python...
            start /wait python_installer.exe /quiet InstallAllUsers=1 PrependPath=1
            IF ERRORLEVEL 1 (
                echo Python installation failed. Please install Python manually.
                del python_installer.exe
                SET ERROR_OCCURRED=1
            ) ELSE (
                del python_installer.exe
                python --version >nul 2>&1
                IF ERRORLEVEL 1 (
                    echo Python is still not recognized. You might need to restart the computer or add it to PATH manually.
                    SET ERROR_OCCURRED=1
                )
            )
        )
    ) ELSE (
        echo 'python' is installed but not necessarily Python 3.
        python --version | findstr /R "^Python 3.*" >nul
        IF ERRORLEVEL 1 (
            echo Python 3 is not installed. Please install Python 3 manually.
            SET ERROR_OCCURRED=1
        ) ELSE (
            echo Python 3 is already installed as 'python'.
        )
    )
) ELSE (
    echo Python3 is already installed.
)

:: install dependencies from requirements.txt
IF %ERROR_OCCURRED%==0 (
    echo Installing dependencies from requirements.txt...
    python -m pip install --upgrade pip
    IF ERRORLEVEL 1 (
        echo Failed to upgrade pip. Please check your Python installation.
        SET ERROR_OCCURRED=1
    )
)

IF %ERROR_OCCURRED%==0 (
    python -m pip install -r requirements.txt
    IF ERRORLEVEL 1 (
        echo Failed to install dependencies. Please check requirements.txt or pip installation.
        SET ERROR_OCCURRED=1
    )
)

:: final check
IF %ERROR_OCCURRED%==1 (
    echo An error occurred during the setup. Please review the above messages.
    pause
    exit /b 1
) ELSE (
    echo Setup complete.
    pause
    exit /b 0
)