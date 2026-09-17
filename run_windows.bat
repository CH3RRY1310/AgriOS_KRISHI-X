@echo off
echo ==========================================
echo AGRI-OS Hackathon Launcher
echo ==========================================
if not exist .venv (
  echo Creating Python virtual environment...
  python -m venv .venv
)
call .venv\Scripts\activate
python -m pip install --upgrade pip
pip install -r requirements.txt
streamlit run app.py
pause
