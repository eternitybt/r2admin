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

# Build bot.
rm -rf dist build *.spec && pyinstaller --onedir tgbot.py && xattr -dr com.apple.quarantine ./dist/tgbot/tgbot
if [ $? -gt 0 ]
then
    echo "❌ Build error."
    exit $ERR_BUILD
fi

echo "✅ Build successful. Start bot: ./dist/tgbot/tgbot"
exit 0
