@echo off
setlocal enabledelayedexpansion
:: Define LF (Line Feed) at the start of your script
set ^"LF=^

^" The empty line above is critical - do not remove

:: Function to load .env file
call :load_env_file || exit /b

endlocal

:: Function to activate the virtual environment if it exists
call :activate_virtual_environment
call :set_env_vars

exit /b


:load_env_file
    if not exist .env (
        echo Error: .env file not found.
        echo Please create a .env file with VAR_NAME=value pairs.
        exit /b 1
    )
    set "env_vars="
    > "%TEMP%\set_env_vars.cmd" (
        for /f "usebackq delims== tokens=1,*" %%a in (".env") do (
            set "key=%%a"
            set "value=%%b"
            set "value=!value:"=!"
            set "value=!value:'=!"
            echo set "%%a=!value!"
            set "env_vars=!env_vars! %%a"
            @REM echo Setting %%a=!value!
        )
    )
    echo Environment variables from .env have been set.
    exit /b 0

:activate_virtual_environment
    if exist .venv\Scripts\activate.bat (
        echo Activated virtual environment found at .venv\Scripts\activate.bat
        call .venv\Scripts\activate.bat
    )
    exit /b 0

:set_env_vars
    echo.
    echo Contents of temporary command file:
    echo -----------------------------------
    type "%TEMP%\set_env_vars.cmd"
    echo -----------------------------------
    echo.
    echo Executing temporary command file...
    endlocal
    call "%TEMP%\set_env_vars.cmd"
    del "%TEMP%\set_env_vars.cmd"
    exit /b 0
