@echo off
rem Generic gcc wrapper using the bundled toolchain.
rem Usage:  cc.cmd -Wall -Wextra -std=c11 -o myapp.exe src\myapp.c
setlocal
set "PATH=%~dp0_tools\toolchain\w64devkit\bin;%PATH%"
gcc %*
