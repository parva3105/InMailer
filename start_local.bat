@echo off
echo 🚀 Starting InMailer Local Development Environment
echo ================================================

echo.
echo 📦 Setting up Backend...
cd Backend

echo Installing Python dependencies...
pip install -r requirements.txt

echo.
echo 🧪 Testing backend setup...
python test_local.py

echo.
echo 🌐 Starting Backend Server...
echo Backend will be available at: http://localhost:5000
echo Press Ctrl+C to stop the backend server
start "InMailer Backend" cmd /k "python start_server_db.py"

echo.
echo 📦 Setting up Frontend...
cd ..\frontend

echo Installing Node.js dependencies...
npm install

echo.
echo 🌐 Starting Frontend Server...
echo Frontend will be available at: http://localhost:3000
echo Press Ctrl+C to stop the frontend server
start "InMailer Frontend" cmd /k "npm start"

echo.
echo ✅ Both servers are starting up!
echo.
echo 📍 Backend:  http://localhost:5000
echo 📍 Frontend: http://localhost:3000
echo 📍 Health:   http://localhost:5000/api/health
echo.
echo Press any key to exit this launcher...
pause > nul
