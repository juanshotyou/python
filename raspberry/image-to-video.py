#!/usr/bin/env python3

import os
import subprocess
from datetime import datetime

def main():
    subprocess.run(["ls", "-l"])

if __name__ == "__main__":
    SCRIPT_RUN_TIME = datetime.now().strftime("%d-%b-%Y-%H-%M-%S")
    main()
    SCRIPT_END_TIME = datetime.now().strftime("%d-%b-%Y-%H-%M-%S")
    print(f"\nScript started - {SCRIPT_RUN_TIME} and ended - {SCRIPT_END_TIME}.")