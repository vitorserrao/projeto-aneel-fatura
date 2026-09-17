@echo off
rem =====================================================================
rem  Sobe a API FastAPI do projeto na porta 8000 (sempre a mesma porta).
rem  Uso: duplo clique OU rodar no terminal do VS Code:  .\run_api.bat
rem
rem  IMPORTANTE:
rem   - Deixe esta janela/terminal ABERTA enquanto usar a API.
rem   - Para parar: pressione Ctrl+C (ou feche a janela do terminal).
rem   - A porta 8000 deve estar livre para subir (feche APIs antigas antes).
rem =====================================================================
cd /d "%~dp0"

echo.
echo Subindo a API em http://127.0.0.1:8000 ...
echo Para parar depois, pressione Ctrl+C.
echo.

.venv\Scripts\python.exe -m uvicorn api.main:app --host 127.0.0.1 --port 8000 --reload

@echo off
echo.
echo A API foi encerrada (Ctrl+C ou erro). 
pause
