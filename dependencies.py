import subprocess
import sys

def install_packages()
    required_packages = [pyautogui, keyboard]
    for package in required_packages
        try
            __import__(package)
            print(f{package} ist bereits installiert.)
        except ImportError
            print(f{package} wird installiert...)
            subprocess.check_call([sys.executable, -m, pip, install, package])

if __name__ == __main__
    install_packages()
