@echo off
setlocal enabledelayedexpansion

echo 🚀 Housing API Docker Deployment Script
echo ========================================

if "%1"=="" set "command=deploy"
if "%1"=="deploy" set "command=deploy"
if "%1"=="build" set "command=build"
if "%1"=="run" set "command=run"
if "%1"=="stop" set "command=stop"
if "%1"=="start" set "command=start"
if "%1"=="restart" set "command=restart"
if "%1"=="status" set "command=status"
if "%1"=="logs" set "command=logs"
if "%1"=="test" set "command=test"
if "%1"=="cleanup" set "command=cleanup"

if "%command%"=="deploy" goto deploy
if "%command%"=="build" goto build
if "%command%"=="run" goto run
if "%command%"=="stop" goto stop
if "%command%"=="start" goto start
if "%command%"=="restart" goto restart
if "%command%"=="status" goto status
if "%command%"=="logs" goto logs
if "%command%"=="test" goto test
if "%command%"=="cleanup" goto cleanup

echo Usage: %0 {deploy^|build^|run^|stop^|start^|restart^|status^|logs^|test^|cleanup}
echo.
echo Commands:
echo   deploy   - Build and run the container ^(default^)
echo   build    - Build the Docker image
echo   run      - Run the container
echo   stop     - Stop the container
echo   start    - Start the container
echo   restart  - Restart the container
echo   status   - Show container status
echo   logs     - Show container logs
echo   test     - Test API endpoints
echo   cleanup  - Stop, remove container and image
exit /b 1

:cleanup
echo 🧹 Cleaning up existing containers...
docker stop housing-api-container 2>nul
docker rm housing-api-container 2>nul
if "%command%"=="cleanup" (
    echo 🗑️ Removing Docker image...
    docker rmi housing-api 2>nul
    exit /b 0
)
goto :eof

:build
echo 🔨 Building Docker image...
docker build -t housing-api -f infra/Dockerfile .
if %errorlevel% neq 0 (
    echo ❌ Docker build failed!
    exit /b 1
)
echo ✅ Docker image built successfully!
if "%command%"=="build" exit /b 0
goto :eof

:run
echo 🚀 Starting Docker container...
docker run -d -p 8000:8000 --name housing-api-container housing-api
if %errorlevel% neq 0 (
    echo ❌ Container start failed!
    exit /b 1
)
echo ✅ Container started successfully!
echo 📊 API available at: http://localhost:8000
echo 📚 Documentation at: http://localhost:8000/docs
echo 🏥 Health check at: http://localhost:8000/health
if "%command%"=="run" exit /b 0
goto :eof

:deploy
call :cleanup
call :build
call :run
echo ⏳ Waiting for container to start...
timeout /t 5 /nobreak >nul
call :status
call :test
exit /b 0

:stop
echo 🛑 Stopping container...
docker stop housing-api-container
exit /b 0

:start
echo ▶️ Starting container...
docker start housing-api-container
exit /b 0

:restart
echo 🔄 Restarting container...
docker restart housing-api-container
exit /b 0

:status
echo 📊 Container Status:
docker ps --filter "name=housing-api-container" --format "table {{.Names}}\t{{.Status}}\t{{.Ports}}"
if "%command%"=="status" exit /b 0
goto :eof

:logs
echo 📋 Container Logs:
docker logs housing-api-container
exit /b 0

:test
echo 🧪 Testing API endpoints...
echo.
echo Testing health endpoint...
powershell -Command "Invoke-WebRequest -Uri 'http://localhost:8000/health' -UseBasicParsing | Select-Object -ExpandProperty Content"
echo.
echo Testing prediction endpoint...
powershell -Command "$body = @{ MedInc = 8.3252; HouseAge = 41.0; AveRooms = 6.984; AveBedrms = 1.024; Population = 322.0; AveOccup = 2.556; Latitude = 37.88; Longitude = -122.23 } | ConvertTo-Json; Invoke-WebRequest -Uri 'http://localhost:8000/predict' -Method POST -Body $body -ContentType 'application/json' -UseBasicParsing | Select-Object -ExpandProperty Content"
if "%command%"=="test" exit /b 0
goto :eof 