@echo off
REM One-click start for RescueTwin AI (Windows).
REM Needs Python 3.11+ and Node.js 20.19+ (or 22+) on PATH. See README "Windows setup".
cd /d "%~dp0"

where python >nul 2>&1 || (echo Python was not found. Install Python 3.12 from python.org and tick "Add python.exe to PATH". & pause & exit /b 1)
where node   >nul 2>&1 || (echo Node.js was not found. Install the LTS version from nodejs.org. & pause & exit /b 1)

REM If something is already using port 8000 or 5173 it may be an OLD copy of this app.
REM Show what it is and ask before stopping it - nothing is closed without your consent.
for %%P in (8000 5173) do (
  for /f "tokens=5" %%A in ('netstat -ano ^| findstr ":%%P " ^| findstr LISTENING') do (
    echo.
    echo Port %%P is in use by:
    tasklist /FI "PID eq %%A" /NH
    choice /C YN /M "Stop it so the fixed build can start"
    if not errorlevel 2 taskkill /F /PID %%A >nul 2>&1
  )
)

echo Installing backend dependencies...
python -m pip install -r backend\requirements-dev.txt || goto :error

if not exist backend\artifacts\flood_severity_xgb.json (
  echo Training the model ^(first run only^)...
  python ai\train_flood_model.py || goto :error
)

start "RescueTwin API" cmd /k "cd /d %~dp0backend && python -m uvicorn app.main:app --reload"

echo Installing frontend dependencies...
cd frontend
call npm.cmd ci || goto :error
start "RescueTwin UI" cmd /k "npm.cmd run dev"

timeout /t 8 >nul
start http://127.0.0.1:5173
echo.
echo If the page looks out of date, hard-refresh with Ctrl+Shift+R.
exit /b 0

:error
echo Something failed - see the message above.
pause
exit /b 1
