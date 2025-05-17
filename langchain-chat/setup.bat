@echo off
echo Installing dependencies...
call npm install

echo Installing TypeScript dependencies...
call npm install --save-dev typescript @types/node @types/react @types/react-dom @types/jest @typescript-eslint/eslint-plugin @typescript-eslint/parser eslint-config-prettier prettier

echo Creating .env file...
(
echo REACT_APP_API_URL=http://localhost:8000
echo REACT_APP_MESSAGES_STORAGE_KEY=chat_messages
) > .env

echo Converting JavaScript files to TypeScript...
ren src\*.js *.tsx
ren src\components\*.js *.tsx

echo Building the project...
call npm run build

if %errorlevel% equ 0 (
    echo Setup completed successfully! Starting the development server...
    call npm start
) else (
    echo Build failed. Please check the error messages above.
    pause
) 