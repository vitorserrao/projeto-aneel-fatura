@echo off
rem =====================================================================
rem  Sobe a interface Streamlit do projeto na porta 8501.
rem  Uso: duplo clique OU rodar no terminal do VS Code:  .\run_streamlit.bat
rem
rem  IMPORTANTE:
rem   - A API FastAPI precisa estar rodando em http://127.0.0.1:8000
rem     (abra run_api.bat ANTES deste).
rem   - Deixe esta janela ABERTA enquanto usar a interface.
rem   - Para parar: pressione Ctrl+C (ou feche a janela do terminal).
rem =====================================================================
cd /d "%~dp0"

echo.
echo Subindo o Streamlit em http://127.0.0.1:8501 ...
echo Para parar depois, pressione Ctrl+C.
echo.

.venv\Scripts\python.exe -m streamlit run app/main.py --server.port 8501

echo.
echo A interface foi encerrada (Ctrl+C ou erro). 
pause
