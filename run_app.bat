@echo off
echo 🚀 Iniciando aplicación ORC - Rotary Cutter Optimizer
echo.
echo Activando entorno virtual...
call env\Scripts\activate.bat
echo.
echo Ejecutando Streamlit...
streamlit run streamlit_app.py
pause
