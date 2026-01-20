@echo off
REM List Available Commands
REM Quick reference for all slash commands

setlocal enabledelayedexpansion

cd /d "%~dp0..\.."

cls
echo.
echo ================================================================
echo          Available Slash Commands
echo ================================================================
echo.

REM List Claude Code Skills
if exist ".claude\skills" (
    echo Claude Code Skills:
    echo ----------------------------------------------------------------
    for /d %%d in (.claude\skills\*) do (
        if exist "%%d\SKILL.md" (
            for /f "tokens=2 delims=:" %%n in ('findstr /b "name:" "%%d\SKILL.md"') do (
                echo   %%n
            )
        )
    )
    echo.
)

REM List Cursor Commands
if exist ".cursor\commands" (
    echo Cursor IDE Commands:
    echo ----------------------------------------------------------------
    for %%f in (.cursor\commands\*.md) do (
        set "filename=%%~nf"
        echo   /!filename!
    )
    echo.
)

echo ================================================================
echo   Quick Usage Tips
echo ================================================================
echo.
echo   Natural Language (Claude Code):
echo     - "explore the authentication system"
echo     - "create a plan for the new feature"
echo     - "review my recent changes"
echo.
echo   Direct Commands (Cursor):
echo     - Type / to see all commands
echo     - /create-issue
echo     - /exploration-phase
echo.
echo   Full Details:
echo     - type .claude\COMMAND_REGISTRY.md
echo     - type SLASH_COMMANDS_GUIDE.md
echo.

pause
