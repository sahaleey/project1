Write-Host "Cleaning up node_modules and package-lock.json..." -ForegroundColor Yellow
Remove-Item -Path "node_modules" -Recurse -Force -ErrorAction SilentlyContinue
Remove-Item -Path "package-lock.json" -Force -ErrorAction SilentlyContinue

Write-Host "Installing dependencies..." -ForegroundColor Green
npm install

Write-Host "Installing TypeScript dependencies..." -ForegroundColor Green
npm install --save-dev typescript @types/node @types/react @types/react-dom @types/jest @typescript-eslint/eslint-plugin @typescript-eslint/parser eslint-config-prettier prettier

Write-Host "Installing additional dependencies..." -ForegroundColor Green
npm install --save zustand @types/zustand axios @types/axios react-error-boundary framer-motion @types/framer-motion

Write-Host "Creating .env file..." -ForegroundColor Green
@"
REACT_APP_API_URL=http://localhost:8000
REACT_APP_MESSAGES_STORAGE_KEY=chat_messages
"@ | Out-File -FilePath ".env" -Encoding UTF8

Write-Host "Creating ESLint configuration..." -ForegroundColor Green
@"
{
  "extends": [
    "react-app",
    "react-app/jest",
    "plugin:@typescript-eslint/recommended",
    "prettier"
  ],
  "plugins": ["@typescript-eslint"],
  "rules": {
    "@typescript-eslint/explicit-function-return-type": "off",
    "@typescript-eslint/explicit-module-boundary-types": "off",
    "@typescript-eslint/no-explicit-any": "warn",
    "react/react-in-jsx-scope": "off"
  }
}
"@ | Out-File -FilePath ".eslintrc.json" -Encoding UTF8

Write-Host "Creating Prettier configuration..." -ForegroundColor Green
@"
{
  "semi": true,
  "trailingComma": "es5",
  "singleQuote": true,
  "printWidth": 100,
  "tabWidth": 2,
  "useTabs": false
}
"@ | Out-File -FilePath ".prettierrc" -Encoding UTF8

Write-Host "Ensuring all files are TypeScript..." -ForegroundColor Green
Get-ChildItem -Path "src" -Filter "*.js" -Recurse | ForEach-Object {
    $newName = $_.FullName -replace '\.js$', '.tsx'
    if (!(Test-Path $newName)) {
        Move-Item -Path $_.FullName -Destination $newName
    }
}

Write-Host "Running type check..." -ForegroundColor Green
npx tsc --noEmit

if ($LASTEXITCODE -eq 0) {
    Write-Host "TypeScript check passed!" -ForegroundColor Green
    Write-Host "Running ESLint..." -ForegroundColor Green
    npm run lint

    if ($LASTEXITCODE -eq 0) {
        Write-Host "ESLint check passed!" -ForegroundColor Green
        Write-Host "Formatting code..." -ForegroundColor Green
        npm run format

        Write-Host "Setup completed successfully! Starting the development server..." -ForegroundColor Green
        npm start
    } else {
        Write-Host "ESLint check failed. Please fix the errors above." -ForegroundColor Red
        Read-Host "Press Enter to exit"
    }
} else {
    Write-Host "TypeScript check failed. Please fix the type errors above." -ForegroundColor Red
    Read-Host "Press Enter to exit"
} 