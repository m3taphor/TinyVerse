#!/bin/bash-low-unrelated-histories

firstRun=true

# Проверка на наличие папки venv
if [ ! -d "venv" ]; then
    echo "Creating virtual environment..."
    python3 -m venv venv
fi

echo "Activating virtual environment..."
source venv/bin/activate

# Проверка на наличие установленного флага в виртуальном окружении
if [ ! -f "venv/installed" ]; then
    if [ -f "requirements.txt" ]; then
		echo "Installing wheel for faster installing"
		pip3 install wheel
        echo "Installing dependencies..."
        pip3 install -r requirements.txt
        touch venv/installed
    else
        echo "requirements.txt not found, skipping dependency installation."
    fi
else
    echo "Dependencies already installed, skipping installation."
fi

if [ ! -f ".env" ]; then
	echo "Copying configuration file"
	cp .env-example .env
else
	echo "Skipping .env copying"
fi

while true
do
    git fetch
    git pull
    if [ "$firstRun" = true ]; then
        python3 main.py
        firstRun=false
    else
        python3 main.py -a 1
    fi

    echo "Restarting the program in 10 seconds..."
    sleep 10
done
