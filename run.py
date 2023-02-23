import sys
from streamlit.web import cli as stcli
import subprocess

# implement pip as a subprocess:
subprocess.check_call([sys.executable, '-m', 'pip', 'install', '-r'
'requirements.txt'])

if __name__ == '__main__':
    sys.argv = ["streamlit", "run", "streamlit_app.py"]
    sys.exit(stcli.main())