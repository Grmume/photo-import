# photo-import
Collection of scripts for the import and storage of photos

These scripts are used to import photos from a connected camera and organize them in an archive.
There are plenty of solutions for this process, but I could not find one which lets me store my pictures in an archive by date
and still offer a way to browse pictures by event in the file explorer.

The scripts are meant to be used in conjunction with a Seafile server to allow remote storage of the pictures on a NAS (which can also perform backups on a regular basis)

In the future it should be possible for multiple people to collaborate on events and easily share pictures (using the seafile server)

Scripts:
  - camera_connect.py: Executed when the camera is connected to the computer. I use the "device-actions" settings in KDE to launch the script when the camera is connected.  
  It launches the dolphin file explorer (of the KDE project) in split view. The user has to create subfolders depending on which event the pictures belong to and place the pictures in the folder. When the file explorer is closed the script launches photo_import.py
  - photo_import.py: Import pictures from the import directory to the archive(custom directory structure, stored in the settings.json file, by date). Create a json file for each event and save information about each picture into the event json-file.
  

Settings files:
All settings are stored in json format. They are not part of the repository because they contain personal information.
  - local_settings.json: Information about the location of the archive, camera, and import folder
  - settings.json: Information about the directory structure inside the archive and library ids of the different seafile libraries
  - server.json: Information about the seafile server. Address, login information.
  
