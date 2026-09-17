@echo off
rem Compile and run the POS program (src\pos.c) with the bundled GCC.
setlocal
set "ROOT=%~dp0"
set "PATH=%ROOT%_tools\toolchain\w64devkit\bin;%PATH%"

if not exist "%ROOT%src\pos.c" (
    echo [!] src\pos.c does not exist yet.
    echo     For the hello-world exercise use:
    echo     .\cc.cmd -Wall -o learning\step0_hello\hello.exe learning\step0_hello\hello.c
    exit /b 1
)

gcc -Wall -Wextra -std=c11 -o "%ROOT%pos.exe" "%ROOT%src\pos.c"
if errorlevel 1 (echo BUILD FAILED & exit /b 1)
echo --- running pos.exe ---
"%ROOT%pos.exe"
