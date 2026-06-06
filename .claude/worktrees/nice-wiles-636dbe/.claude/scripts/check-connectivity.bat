@echo off
REM Claude Code Connectivity & Login Check Script (Windows)
REM Diagnoses connection issues and authentication problems for Claude Code CLI

setlocal enabledelayedexpansion

echo.
echo ================================================================
echo    Claude Code - Connectivity ^& Login Diagnostics
echo ================================================================
echo.

set ERRORS=0
set WARNINGS=0

REM ── 1. Check internet connectivity ──────────────────────────────────
echo -- Step 1: Internet Connectivity --------------------------------
curl -s --max-time 5 --head "https://google.com" >nul 2>&1
if %errorlevel% equ 0 (
    echo [PASS] Internet connection is working
) else (
    echo [FAIL] No internet connection detected
    echo        Check your network, proxy, or firewall settings.
    set /a ERRORS+=1
)

REM ── 2. Check Anthropic API reachability ─────────────────────────────
echo.
echo -- Step 2: Anthropic API Reachability ---------------------------
for /f %%i in ('curl -s --max-time 10 -o nul -w "%%{http_code}" "https://api.anthropic.com" 2^>nul') do set HTTP_STATUS=%%i

if "%HTTP_STATUS%"=="000" (
    echo [FAIL] Cannot reach api.anthropic.com
    echo        Possible causes:
    echo          - Firewall blocking outbound HTTPS port 443
    echo          - Corporate proxy requiring configuration
    echo          - DNS resolution failure
    set /a ERRORS+=1
) else (
    echo [PASS] api.anthropic.com is reachable (HTTP %HTTP_STATUS%)
)

REM ── 3. Check Claude CLI installation ────────────────────────────────
echo.
echo -- Step 3: Claude CLI Installation ------------------------------
where claude >nul 2>&1
if %errorlevel% equ 0 (
    for /f "tokens=*" %%v in ('claude --version 2^>nul') do set CLAUDE_VER=%%v
    echo [PASS] Claude CLI is installed: !CLAUDE_VER!
) else (
    echo [FAIL] claude command not found
    echo        Install Claude Code CLI:
    echo          npm install -g @anthropic-ai/claude-code
    set /a ERRORS+=1
)

REM ── 4. Check ANTHROPIC_API_KEY environment variable ─────────────────
echo.
echo -- Step 4: API Key Configuration --------------------------------
if defined ANTHROPIC_API_KEY (
    set KEY_PREVIEW=!ANTHROPIC_API_KEY:~0,8!...
    echo [PASS] ANTHROPIC_API_KEY is set (!KEY_PREVIEW!)

    echo !ANTHROPIC_API_KEY! | findstr /b "sk-ant-" >nul 2>&1
    if !errorlevel! equ 0 (
        echo [PASS] API key format looks valid
    ) else (
        echo [WARN] API key does not start with 'sk-ant-' -- may be invalid
        set /a WARNINGS+=1
    )
) else (
    echo [WARN] ANTHROPIC_API_KEY environment variable is not set
    echo        This is OK if you logged in with 'claude auth login'.
    echo        To set it for this session:
    echo          set ANTHROPIC_API_KEY=sk-ant-...
    set /a WARNINGS+=1
)

REM ── 5. Check Claude config directory ────────────────────────────────
echo.
echo -- Step 5: Claude Auth ^& Config Files ---------------------------
set CLAUDE_CONFIG=%USERPROFILE%\.claude

if exist "%CLAUDE_CONFIG%" (
    echo [PASS] Config directory exists: %CLAUDE_CONFIG%
) else (
    echo [WARN] Config directory not found: %CLAUDE_CONFIG%
    echo        Run 'claude' once to initialize it.
    set /a WARNINGS+=1
)

if exist "%CLAUDE_CONFIG%\.credentials.json" (
    echo [PASS] Credentials file exists
) else if exist "%CLAUDE_CONFIG%\auth.json" (
    echo [PASS] Auth file exists ^(auth.json^)
) else (
    echo [WARN] No credentials file found in %CLAUDE_CONFIG%
    echo        Run: claude auth login
    set /a WARNINGS+=1
)

REM ── 6. Live API authentication test ─────────────────────────────────
echo.
echo -- Step 6: Live Authentication Test -----------------------------
if defined ANTHROPIC_API_KEY (
    curl -s --max-time 10 ^
        -H "x-api-key: %ANTHROPIC_API_KEY%" ^
        -H "anthropic-version: 2023-06-01" ^
        -H "content-type: application/json" ^
        -d "{\"model\":\"claude-haiku-4-5\",\"max_tokens\":5,\"messages\":[{\"role\":\"user\",\"content\":\"Hi\"}]}" ^
        "https://api.anthropic.com/v1/messages" > "%TEMP%\claude_auth_test.json" 2>nul

    findstr /c:"\"type\":\"message\"" "%TEMP%\claude_auth_test.json" >nul 2>&1
    if !errorlevel! equ 0 (
        echo [PASS] API key is valid and authentication works
    ) else (
        findstr /c:"authentication_error" "%TEMP%\claude_auth_test.json" >nul 2>&1
        if !errorlevel! equ 0 (
            echo [FAIL] API key is invalid or expired
            echo        Go to https://console.anthropic.com/keys to create a new key
            set /a ERRORS+=1
        ) else (
            echo [WARN] Could not verify API key ^(unexpected response^)
            set /a WARNINGS+=1
        )
    )
    if exist "%TEMP%\claude_auth_test.json" del "%TEMP%\claude_auth_test.json"
) else (
    echo [INFO] Skipping live auth test ^(no ANTHROPIC_API_KEY set^)
    echo        To test: set ANTHROPIC_API_KEY=sk-ant-... then re-run this script
)

REM ── 7. Proxy detection ──────────────────────────────────────────────
echo.
echo -- Step 7: Proxy Configuration ----------------------------------
set PROXY_FOUND=0
if defined HTTPS_PROXY (
    echo [INFO] HTTPS_PROXY is set: %HTTPS_PROXY%
    set PROXY_FOUND=1
)
if defined HTTP_PROXY (
    echo [INFO] HTTP_PROXY is set: %HTTP_PROXY%
    set PROXY_FOUND=1
)
if %PROXY_FOUND%==0 (
    echo [INFO] No proxy environment variables set
)

REM ── Summary ─────────────────────────────────────────────────────────
echo.
echo ================================================================
echo    Summary
echo ================================================================
if %ERRORS%==0 if %WARNINGS%==0 (
    echo All checks passed -- Claude Code should work correctly!
) else if %ERRORS%==0 (
    echo %WARNINGS% warning^(s^) found -- review above for details.
) else (
    echo %ERRORS% error^(s^) and %WARNINGS% warning^(s^) found.
    echo.
    echo   Quick fix steps:
    echo   1. Check internet:   curl https://api.anthropic.com
    echo   2. Install Claude:   npm install -g @anthropic-ai/claude-code
    echo   3. Login:            claude auth login
    echo   4. Or set API key:   set ANTHROPIC_API_KEY=sk-ant-...
    echo.
    echo   Full guide: 04-reference\cheatsheets\CLI_LOGIN_TROUBLESHOOTING.md
)
echo.

pause
