@echo off
echo ================================================
echo   KARUI-SEARCH FRONTEND DEV SERVER
echo   Starting React + Vite development server
echo   URL: http://localhost:3000 (or next available port)
echo ================================================
echo.
echo This will start the frontend development server with:
echo   - React 18 + TypeScript
echo   - Material-UI components
echo   - Mock property data from src/frontend/src/data/
echo   - Hot reload enabled
echo.
echo Press Ctrl+C to stop the server
echo.
pause

cd /d "%~dp0\..\src\frontend"
npm run dev