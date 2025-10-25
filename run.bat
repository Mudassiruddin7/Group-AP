@echo off
REM F2 Portfolio Recommender - Windows Launcher
REM Quick launch script for Windows users

echo ================================================
echo F2 PORTFOLIO RECOMMENDER
echo Autonomous AI-Powered Portfolio Optimization
echo ================================================
echo.

REM Check if in correct directory
if not exist "app.py" (
    echo ERROR: app.py not found!
    echo Please run this script from the project directory.
    pause
    exit /b 1
)

REM Menu
:menu
echo.
echo What would you like to do?
echo.
echo [1] Install Dependencies
echo [2] Verify System
echo [3] Run Streamlit App
echo [4] Test Data Loader
echo [5] Test Optimizer
echo [6] Test Cerebras Agent
echo [7] Exit
echo.
set /p choice="Enter your choice (1-7): "

if "%choice%"=="1" goto install
if "%choice%"=="2" goto verify
if "%choice%"=="3" goto run_app
if "%choice%"=="4" goto test_data
if "%choice%"=="5" goto test_optimizer
if "%choice%"=="6" goto test_agent
if "%choice%"=="7" goto end

echo Invalid choice. Please try again.
goto menu

:install
echo.
echo ================================================
echo Installing Dependencies...
echo ================================================
pip install -r requirements.txt
echo.
echo Installation complete!
pause
goto menu

:verify
echo.
echo ================================================
echo Verifying System...
echo ================================================
python verify_system.py
echo.
pause
goto menu

:run_app
echo.
echo ================================================
echo Starting Streamlit App...
echo ================================================
echo.
echo The app will open in your browser at:
echo http://localhost:8501
echo.
echo Press Ctrl+C to stop the server
echo.
streamlit run app.py
goto menu

:test_data
echo.
echo ================================================
echo Testing Data Loader...
echo ================================================
python data_loader.py
echo.
pause
goto menu

:test_optimizer
echo.
echo ================================================
echo Testing Portfolio Optimizer...
echo ================================================
python portfolio_optimizer_csv.py
echo.
pause
goto menu

:test_agent
echo.
echo ================================================
echo Testing Cerebras Agent...
echo ================================================
python agent_cerebras.py
echo.
pause
goto menu

:end
echo.
echo Thank you for using F2 Portfolio Recommender!
echo.
pause
