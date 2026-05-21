@echo off
title Lorrainwly.com - One-Click Deployer
echo ==========================================
echo   Lorrainwly.com - One-Click Deployer
echo ==========================================
echo.
echo [1/3] Adding files to Git...
git add .
echo.
echo [2/3] Committing changes...
git commit -m "style: optimize assets and website layout"
echo.
echo [3/3] Pushing to GitHub (with proxy bypass)...
git -c http.proxy= -c https.proxy= push origin master
echo.
echo ==========================================
echo   Deploy completed successfully!
echo   Vercel is now updating lorrainwly.com...
echo ==========================================
pause
