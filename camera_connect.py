#!/usr/bin/env python
"""
Script that is launched by the OS when a camera is connected.
It launches the dolphin file explorer (of the KDE project) in split view.
The user has to copy the pictures from the camera to the import folder ( in some subfolder depending on the event).
When closing the file explorer the script will launch the import process.
"""
import subprocess
import json
import sys
import datetime
import os
from os.path import expanduser


# Load local settings
script_location = os.path.realpath(os.path.join(os.getcwd(), os.path.dirname(__file__)))
with open(os.path.join(script_location, 'local_settings.json'), 'r') as f:
    settings = json.load(f)

if len(sys.argv) >= 2:
    cameraPath = sys.argv[1]
    print "CameraPath is "+cameraPath
else:
    if 'cameraPath' in settings:
        cameraPath = settings['cameraPath']
    else:
        cameraPath = expanduser("~")

if 'importPath' in settings:
    importPath = settings['importPath']
else:
    print "Error: Could not find import path in settings"
    #TODO refresh settings from seafile settings

importPathThisYear = os.path.join(importPath, str(datetime.datetime.now().year))

if not os.path.isdir(importPathThisYear):
    os.path.makedirs(importPathThisYear)

dcimPath = os.path.join(cameraPath,os.path.join('DCIM','100PHOTO'))

if os.path.isdir(dcimPath):
    cameraPath = dcimPath

subprocess.call(['dolphin', '--split', cameraPath, importPathThisYear])
execfile(os.path.join(script_location, 'photo_import.py'))
