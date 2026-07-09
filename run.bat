@echo off
echo ============================================
echo Lotofacil Optimizer PRO
echo ============================================
echo.

REM Verifica se o Python está instalado
python --version >nul 2>&1
if errorlevel 1 (
    echo ERRO: Python nao encontrado!
    echo Instale o Python 3.12 ou superior.
    pause
    exit /b 1
)

REM Verifica se as dependências estão instaladas
python -c "import PySide6" >nul 2>&1
if errorlevel 1 (
    echo Dependencias nao encontradas!
    echo Executando instalacao...
    call install.bat
)

REM Executa o sistema
echo.
echo Iniciando o sistema...
python main.py

pause