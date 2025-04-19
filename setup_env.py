# setup_env.py

import subprocess
import os
import sys

# Define paths
venv_dir = "venv"
requirements_file = "requirements.txt"

# Create venv if not exists
if not os.path.isdir(venv_dir):
    print("Creating virtual environment...")
    subprocess.check_call([sys.executable, "-m", "venv", venv_dir])
else:
    print("Virtual environment already exists.")

# Install requirements using the venv's pip
pip_path = os.path.join(venv_dir, "Scripts", "pip.exe") if os.name == "nt" else os.path.join(venv_dir, "bin", "pip")
print("Installing dependencies from requirements.txt...")
subprocess.check_call([pip_path, "install", "-r", requirements_file])

print("\n✅ Setup complete. You're good to go!")
