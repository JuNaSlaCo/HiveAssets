import os
import shutil
import sys
import subprocess
import platform

SCRIPTNAME = "server.py"
OUTNAME = "HASRV"
DIST = "dist"

STATIC_PATHS = ["views", "static"]

def run():
    system = platform.system().lower()
    if system == "windows":
        ext = ".exe"
    else:
        ext = ""

    output_dir = os.path.join(DIST, system)
    os.makedirs(output_dir, exist_ok=True)

    print(f"Build {system}...")

    cmd = [
        "pyinstaller",
        "--onefile",
        *[f"--add-data={path}{os.pathsep}{path}" for path in STATIC_PATHS],
        SCRIPTNAME,
    ]

    subprocess.run(cmd, check=True)

    finalname = f"{OUTNAME}{ext}"
    builtfile = os.path.join("dist", f"server{ext}")
    targetpath = os.path.join(output_dir, finalname)

    if os.path.exists(targetpath):
        os.remove(targetpath)

    shutil.move(builtfile, targetpath)
    print(f"Move build to {targetpath}")

if __name__ == "__main__":
    run()
