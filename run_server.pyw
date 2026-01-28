"""Silent launcher for PC Control Server (no console window)."""
import subprocess
import sys
import os

os.chdir(r"F:\study\Dev_Toolchain\programming\python\apps\pc-control-server")
subprocess.Popen(
    [sys.executable, r"src\server.py"],
    creationflags=subprocess.CREATE_NO_WINDOW,
    cwd=r"F:\study\Dev_Toolchain\programming\python\apps\pc-control-server",
)
