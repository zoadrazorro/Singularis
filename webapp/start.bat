@echo off
echo ================================================================================
echo Singularis Learning Monitor
echo ================================================================================
echo.
echo Installing dependencies...
call npm install
echo.
echo Starting backend server...
start "Singularis Backend" cmd /k npm run server
timeout /t 3 /nobreak > nul
echo.
echo Starting React frontend...
start "Singularis Frontend" cmd /k npm start
echo.
echo ================================================================================
echo Dashboard will open at http://localhost:3000
echo Backend API at http://localhost:5000
echo WebSocket at ws://localhost:5001
echo ================================================================================
echo.
echo Press any key to exit (servers will keep running)...
pause > nul
