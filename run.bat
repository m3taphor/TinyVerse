@echo off

set firstRun=true

if not exist venv (
    echo Creating virtual environment...
    python -m venv venv
)

echo Activating virtual environment...
call venv\Scripts\activate

if not exist venv\Lib\site-packages\installed (
    if exist requirements.txt (
		echo installing wheel for faster installing
		pip install wheel
        echo Installing dependencies...
        pip install -r requirements.txt
        echo. > venv\Lib\site-packages\installed
    ) else (
        echo requirements.txt not found, skipping dependency installation.
    )
) else (
    echo Dependencies already installed, skipping installation.
)

if not exist .env (
	echo Copying configuration file
	copy .env-example .env
) else (
	echo Skipping .env copying
)

echo Starting the bot...
:loop
git fetch
git pull
if "%firstRun%"=="true" (
    python main.py
    set firstRun=false
) else (
    python main.py -a 1
)
echo Restarting the program in 10 seconds...
timeout /t 10 /nobreak >nul
goto :loop
