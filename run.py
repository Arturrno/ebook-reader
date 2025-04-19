import subprocess
import os
import sys

# Path to Python inside the venv
python_path = os.path.join("venv", "Scripts", "python.exe") if os.name == "nt" else os.path.join("venv", "bin", "python")

# Path to the main script inside the app folder
main_script = os.path.join("app", "main.py")

# Run main.py inside the app folder
subprocess.run([python_path, main_script])
