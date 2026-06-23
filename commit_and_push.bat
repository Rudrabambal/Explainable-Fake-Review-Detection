@echo off
echo Fixing the corrupted OneDrive .git folder and re-syncing with GitHub...
cd /d "%~dp0"
rmdir /s /q .git
git init
git remote add origin https://github.com/Rudrabambal/Explainable-Fake-Review-Detection.git
git fetch
git branch -M main
git reset --mixed origin/main
echo.
echo Git repository successfully repaired and connected to GitHub!
pause
