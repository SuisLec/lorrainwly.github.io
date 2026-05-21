@echo off
title Lorrainwly.com - One-Click Deployer
echo ==========================================
echo   Lorrainwly.com - One-Click Deployer
echo ==========================================
echo.
echo [1/4] Processing signature image...
python process_signature.py
echo.
echo [2/4] Adding files to Git...
git add .
echo.
echo [3/4] Committing changes...
git commit -m "style: add custom signature to navbar and integrate elegant purple lines"
echo.
echo [4/4] Pushing to GitHub (with proxy bypass)...
git -c http.proxy= -c https.proxy= push origin master
echo.
echo ==========================================
echo   Deploy completed successfully!
echo   Vercel is now updating lorrainwly.com...
echo ==========================================
pause
