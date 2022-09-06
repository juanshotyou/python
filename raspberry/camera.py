#!/usr/bin/env python3

import os
from typing import Tuple
from picamera import PiCamera
from datetime import datetime
from time import sleep

def getDiskStats(path) -> Tuple:
    """Returns tuple with disk usage statistics about the given path in GB.
    """
    st = os.statvfs(path)
    free = (st.f_bavail * st.f_frsize) / 2**30
    total = (st.f_blocks * st.f_frsize) / 2**30
    used = (st.f_blocks - st.f_bfree) * st.f_frsize / 2**30
    return total, free, used

def checkDiskSpace() -> bool:
    """Return True if free disk space exceeds used disk space and False if
        otherwise.
    """
    d_total, d_free, d_used = getDiskStats("/")
    if d_used < d_free:
        return True
    else:
        return False

def main():
    # Initialize camera and picture settings
    camera = PiCamera()
    camera.resolution = (2592, 1944)
    camera.framerate = 15

    # Hardcode to take max 12500 pics beforeq quitting
    total = 0
    stage = 0
    while total < 12500:
        stage+=1
        # Retrieve current system stats and print
        d_total, d_free, d_used = getDiskStats("/")
        print(f"Stage {stage} started...\nCurrent disk statistics: "
            f"{d_total} GB total, {d_used} GB used, {d_free} GB free.")

        # Take 2500 pictures, one every 2 seconds
        index = 0
        while index < 2500:
            timestamp = datetime.now().strftime("%d-%b-%Y-%H-%M-%S")
            camera.capture(f"/home/vlad/pi-camera/{timestamp}.jpg")
            index+=1
            total+=1
            sleep(2)

        # Print current disk usage stats
        d_total, d_free, d_used = getDiskStats("/")
        print(f"Stage {stage} completed...\nCurrent disk statistics: "
            f"{d_total} GB total, {d_used} GB used, {d_free} GB free.")

        # Copy pictures to PI451 external HDD then delete from disk
        print(f"{index} pictures taken. Copying pictures to PI451.")
        scp_local = "/home/vlad/pi-camera/* "
        scp_remote = "vlad@192.168.0.51:/srv/dev-disk-by-uuid-94BA918FBA916F0C/_PIZERO/pi-camera/"
        os.system("scp " + scp_local + scp_remote)
        os.system("rm -rf /home/vlad/pi-camera/*")


if __name__ == "__main__":
    SCRIPT_RUN_TIME = datetime.now().strftime("%d-%b-%Y-%H-%M-%S")
    main()
    SCRIPT_END_TIME = datetime.now().strftime("%d-%b-%Y-%H-%M-%S")
    print(f"\nScript started - {SCRIPT_RUN_TIME} and ended - {SCRIPT_END_TIME}.")