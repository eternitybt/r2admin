ERR_CD_PROJDIR=1
ERR_CREATE_VENV=2
ERR_PYTHON_DEP=3
ERR_GIT_UPDATE=4
ERR_BUILD=5

# Change directory to project path.
PROJECT_PATH=$( cd -- "$( dirname -- "${BASH_SOURCE[0]}" )" &> /dev/null && pwd )
cd "$PROJECT_PATH"
if [ $? -gt 0 ]
then
    echo "❌ Failed to change directory to project path \"$PROJECT_PATH\"."
    exit $ERR_CD_PROJDIR
fi

# Activate virtual environment.
if [ -e "venv/bin/activate" ]
then
    . venv/bin/activate
else
    echo "⚠️ Virtual environment does not exist. Creating it now."
    rm -rf venv && python3 -m venv venv
    if [ ! -e "venv/bin/activate" ]
    then
        echo "❌ Failed to create virtual environment."
        exit $ERR_CREATE_VENV
    fi
    . venv/bin/activate

    # Install Python dependencies.
    NE=0
    pip install --upgrade pip                   ; NE=$((NE + $?))
    pip install --upgrade pyinstaller           ; NE=$((NE + $?))
    pip install --upgrade python-telegram-bot   ; NE=$((NE + $?))
    pip install --upgrade telethon              ; NE=$((NE + $?))
    if [ $NE -gt 0 ]
    then
        echo "❌ Failed to install Python dependencies."
        rm -r venv
        exit $ERR_PYTHON_DEP
    fi
fi

# Update repo.
git pull
if [ $? -gt 0 ]
then
    echo "❌ Failed to update repository."
    exit $ERR_GIT_UPDATE
fi

# Build r2bot.
rm -rf dist build *.spec && pyinstaller --onedir r2bot.py && xattr -dr com.apple.quarantine ./dist/r2bot/r2bot
if [ $? -gt 0 ]
then
    echo "❌ Failed to build r2bot."
    exit $ERR_BUILD
fi

# Build c3bot.
pyinstaller --onedir c3bot.py && xattr -dr com.apple.quarantine ./dist/c3bot/c3bot
if [ $? -gt 0 ]
then
    echo "❌ Failed to build c3bot."
    exit $ERR_BUILD
fi

echo "✅ Build successful."
exit 0
