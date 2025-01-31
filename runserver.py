import os
import platform
import subprocess
import sys

# A file for a more convenient launch of the project on windows
# or Linux, in local network

os.chdir(os.getcwd())
file = "manage.py"
params = ["runserver", "0.0.0.0:8000"]
if platform.system() == "Windows":
    python_interpreter = r".venv\Scripts\python"
elif platform.system() == "Linux":
    python_interpreter = r".venv\bin\python"

process = subprocess.Popen(
    [python_interpreter, file, *params],
    stdout=sys.stdout,
    stderr=sys.stderr,
    text=True,
    bufsize=1,
    universal_newlines=True,
)
process.wait()

print("Process finished with return code:", process.returncode)
