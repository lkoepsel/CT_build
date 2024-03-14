#!/usr/local/bin/python3
# Disconnect CoolTerm from serial port

import sys
from utilities.CoolTerm import CoolTermSocket


def disc():
    s = CoolTermSocket()

    # Check if there are any open windows
    count = s.WindowCount()

    if count > 0:
        # Get the ID of the frontmost open window
        ID = s.GetFrontmostWindow()
    else:
        print("Unable to find a CoolTerm Window, is one open?")
        sys.exit()

    # Open the serial port
    if not s.Disconnect(ID):
        print("Unable to disconnect CoolTerm")
    s.Close()
