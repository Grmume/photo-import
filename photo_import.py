#!/usr/bin/env python
"""
Copy files from a import directory to a archive directory
The import directory has to contain folders with the following structure

Year/Month/Event/(User)

Year and month are numerical values.

Event is a string describing the event which these pictures belong to

User describes which user uploaded these pictures. If there is no folder inside the Event
folder describing the user, the value for the user has to be provided to the script

The archive folder has a user specified structure

"""

import os
from shutil import copy2
import json
from time import gmtime, strftime
import hashlib

DEFAULTUSER = 'Steffi&Greg'

RAW_FILEEXTENSIONS = ['3fr', 'ari', 'arw', 'bay', 'crw', 'cap', 'data', 'dcs', 'dcr', 'dng', 'drf', 'eip', 'erf', 'fff', 'gpr', 'iiq', 'k25', 'kdc', 'mdc', 'mef', 'mos', 'mrw', 'nef', 'nrw', 'obm', 'orf', 'pef', 'ptx', 'pxn', 'r3d', 'raf', 'raw', 'rwl', 'rw2', 'rwz', 'sr2', 'srf', 'srw', 'tif', 'x3f' ]
MOVIE_FILEEXTENSIONS = ['webm', 'mkv', 'flv', 'vob', 'ogv', 'ogg', 'drc', 'gif', 'gifv', 'mng', 'avi', 'mov', 'qt', 'wmv', 'yuv', 'rm', 'rmvb', 'asf', 'amv', 'mp4', 'm4p', 'mpg', 'mp2', 'mpeg', 'mpe', 'mpv', 'm2v', 'm4v', 'svi', '3gp', '3g2', 'mxf']

def hash_bytestr_iter(bytesiter, hasher, ashexstr=False):
    """Helper function for md5 checksum generation."""
    for block in bytesiter:
        hasher.update(block)
    return (hasher.hexdigest() if ashexstr else hasher.digest())

def file_as_blockiter(afile, blocksize=65536):
    """Helper function for md5 checksum generation."""
    with afile:
        block = afile.read(blocksize)
        while len(block) > 0:
            yield block
            block = afile.read(blocksize)

def md5(filepath):
    """Return the md5 checksum of the file in a hex number encoded in a string."""
    return hash_bytestr_iter(file_as_blockiter(open(filepath, 'rb')), hashlib.md5(), True)[:32]

def parseImportFolder(importFolder):
    """Search the given folder for year-folders (consisting of a number) and event-folders(all other folders)."""
    print "Parsing importfolder: "+importFolder
    for (dirpath, dirnames, filenames) in os.walk(importFolder):
        for yearFolder in dirnames:
            try:
                int(yearFolder)
                parseYearFolder(os.path.join(dirpath,yearFolder))
            except ValueError:
                parseEventFolder(os.path.join(dirpath,yearFolder))
        break


def parseYearFolder(yearFolder):
    """Search the given folders for month folders or event folders."""
    print "Parsing yearfolder: "+yearFolder
    for (dirpath, dirnames, filenames) in os.walk(yearFolder):
        for monthFolder in dirnames:
            try:
                int(monthFolder)
                parseMonthFolder(os.path.join(dirpath, monthFolder))
            except ValueError:
                parseEventFolder(os.path.join(dirpath, monthFolder))
        break

def parseMonthFolder(monthFolder):
    """Search the given folder event folders."""
    print "Parsing monthfolder: "+monthFolder
    for (dirpath, dirnames, filenames) in os.walk(monthFolder):
        for eventFolder in dirnames:
           parseEventFolder(os.path.join(dirpath,eventFolder))
        break

def parseEventFolder(eventFolder):
    """Search the given folder for pictures or movies or user folders."""
    print "Parsing eventFolder: "+eventFolder

    # Create a dictionary which contains all information about this event
    start_date = {'year':9999, 'month':99, 'day': 99}
    event = { 'name':os.path.basename(eventFolder), 'files':[], 'start_date':start_date}

    # Parse subdirectories
    for (dirpath, dirnames, filenames) in os.walk(eventFolder):
        for userFolder in dirnames:
            files = parseUserFolder(os.path.join(dirpath,userFolder), event['name'])
            for f in files:
                if firstDateIsEarlier(f['time_of_creation'], event['start_date']):
                    event['start_date']['year'] = f['time_of_creation']['year']
                    event['start_date']['month'] = f['time_of_creation']['month']
                    event['start_date']['day'] = f['time_of_creation']['day']

                # if f['year'] < event['year_start']:
                #     event['year_start'] = f['year']
                #     event['month_start'] = f['month']
                #     event['day_start'] = f['day']
                # elif f['year'] == event['year_start']:
                #     if f['month'] < event['month_start']:
                #         event['month_start'] = f['month']
                #         event['day_start'] = f['day']
                #     elif f['month'] == event['month_start']:
                #         if f['day'] < event['day_start']:
                #             event['day_start'] = f['day']

            event['files'].extend()
        for filename in filenames:
            f = parseFile(os.path.join(dirpath, filename), event['name'], DEFAULTUSER)
            if firstDateIsEarlier(f['time_of_creation'], event['start_date']):
                event['start_date']['year'] = f['time_of_creation']['year']
                event['start_date']['month'] = f['time_of_creation']['month']
                event['start_date']['day'] = f['time_of_creation']['day']

            # if f['year'] < event['year_start']:
            #     event['year_start'] = f['year']
            #     event['month_start'] = f['month']
            #     event['day_start'] = f['day']
            # elif f['year'] == event['year_start']:
            #     if f['month'] < event['month_start']:
            #         event['month_start'] = f['month']
            #         event['day_start'] = f['day']
            #     elif f['month'] == event['month_start']:
            #         if f['day'] < event['day_start']:
            #             event['day_start'] = f['day']

            event['files'].append(f)
        break

    # Verify event
    verifyEvent(event, deleteImportedFiles = True)

    # Delete the eventFolder
    os.rmdir(eventFolder)

    # Write event to file
    targetEventFolderPath = os.path.join(eventDir, os.path.join(str(event['year_start']), str(event['month_start'])))

    # Check if the targetFolder already exists
    if os.path.isdir(targetEventFolderPath):
        targetFilePath = os.path.join(targetEventFolderPath, event['name']+".json")
        # Check if the target file already exists
        if os.path.isfile(targetFilePath):
            mergeEvent(event, targetFilePath)
        else:
            with open(targetFilePath, 'w') as f:
                json.dump(event, f)
    else:
        # Create the folders
        os.makedirs(targetEventFolderPath)
        # Write data
        with open(targetFilePath, 'w') as f:
            json.dump(event, f)



def parseUserFolder(userFolder, event):
    """Search the given folder for pictures or movies."""
    print "Parsing userFolder: "+userFolder
    files = []
    for (dirpath, dirnames, filenames) in os.walk(userFolder):
        for filename in filenames:
            files.append(parseFile(os.path.join(dirpath, filename), event, os.path.basename(userFolder)))
        break
    return files

def parseFile(filepath, event, user):
    """Copy the given file to the target folder. The target folder is derived from the provided event and user."""
    targetFolder = getTargetFolder(archiveDir, archiveStructure, filepath, user)

    # Check if target folder exists
    if not os.path.isdir(targetFolder):
            # Create the folder
            os.makedirs(targetFolder)

    print "Copied file "+filepath+" to " + targetFolder

    copy2(filepath, targetFolder)
    editTime = gmtime(os.path.getmtime(filepath))
    time_of_creation = {'year':editTime.tm_year, 'month':editTime.tm_mon, 'day':editTime.tm_mday, 'hour':editTime.tm_hour, 'minute':editTime.tm_min, 'second': editTime.tm_sec }
    return {'filepath':os.path.join(targetFolder,os.path.basename(filepath)), 'importpath':filepath, 'user':user, 'filetype':getFileType(filepath), 'time_of_creation':time_of_creation , 'md5':md5(filepath) }

def getFileType(filepath):
    """Return the filetype for the given file based on the extension. Possible values are:jpg, movie, raw."""
    # Determine the file type of the file
    isRaw = False
    for rawExt in RAW_FILEEXTENSIONS:
        if filepath.lower().endswith('.'+rawExt):
            isRaw = True
            break
    if isRaw:
        return 'raw'
    else:
        isMovie = False
        for movieExt in MOVIE_FILEEXTENSIONS:
            if filepath.lower().endswith('.'+movieExt):
                isMovie = True
                break
        if isMovie:
            return 'movie'
        else:
            return 'jpg'

def getTargetFolder(archiveFolder, archiveFormat, filepath, user):
    """Get the TargetFolder based on the format, filepath and user."""
    editTime = gmtime(os.path.getmtime(filepath))

    formatTimePlaced = strftime(archiveFormat, editTime)

    formatUserPlaced = formatTimePlaced.replace('%u', user)

    # Determine the file type of the file
    isRaw = False
    for rawExt in RAW_FILEEXTENSIONS:
        if filepath.lower().endswith('.'+rawExt):
            isRaw = True
            break

    if isRaw:
        formatTypePlaced = formatUserPlaced.replace('%t', 'raw')

        if user == DEFAULTUSER:
            return os.path.join(archiveFolder, formatTypePlaced.replace('%Q', 'raw'))
        else:
            return os.path.join(archiveFolder, formatTypePlaced.replace('%Q', user))
    else:
        isMovie = False
        for movieExt in MOVIE_FILEEXTENSIONS:
            if filepath.lower().endswith('.'+movieExt):
                isMovie = True
                break

        if isMovie:
            formatTypePlaced = formatUserPlaced.replace('%t', 'movie')
            if user == DEFAULTUSER:
                return os.path.join(archiveFolder, formatTypePlaced.replace('%Q', 'movie'))
            else:
                return os.path.join(archiveFolder, formatTypePlaced.replace('%Q', user))
        else:
            formatTypePlaced = formatUserPlaced.replace('%t', 'jpg')

            if user == DEFAULTUSER:
                return os.path.join(archiveFolder, formatTypePlaced.replace('%Q', 'jpg'))
            else:
                return os.path.join(archiveFolder, formatTypePlaced.replace('%Q', user))

def verifyEvent(event, deleteImportedFiles = False):
    """Check if all files in the event were copied to the archive and if their checksum match."""
    for f in event['files']:
        if os.path.isfile(f['filepath']):
            md5Source = f['md5']
            md5Target = md5(f['importPath'])
            if md5Source != md5Target:
                print "Error while verifying. MD5 of file "+f['filepath']+ " does not match "+f['importPath']
            else:
                print "File "+f['importPath']+ " successfully verfied"

                if deleteImportedFiles:
                    os.remove(f['importPath'])
        else:
            print "Error while verifying. File " + f['filepath'] + " could not be found"

def firstDateIsEarlier(firstDate, secondDate):
    """Check if the first parameter is earlier than the second. Parameters have to be dictionaries containing year, month and day entries."""
    if firstDate['year'] < secondDate['year']:
        return True
    elif firstDate['year'] == secondDate['year']:
        if firstDate['month'] < secondDate['month']:
            return True
        elif firstDate['month'] == secondDate['moth']:
            if firstDay['day'] < secondDate['day']:
                return True
            else:
                return False
        else:
            return False
    else:
        return False

def mergeEvent(event, pathToJson):
    """Merge the event given as first parameter with the event stored in the filepath in the second parameter. Add new pictures, adjust start_date of event."""
    # Load the old event
    with open(pathToJson, 'r') as f:
        oldEvent = json.load(f)

    # Iterate over new event
    for newfile in event['files']:
        # Check if the new file is present in the event
        # Check if there is a file with the same path and md5 sum
        fileAlreadyImported = False
        for oldfile in oldEvent['files']:
            if newFile['filepath'] == oldFile['filepath']:
                if newFile['md5'] == oldFile['md5']:
                fileAlreadyImported = True
                #TODO Raise error if not!

        if not fileAlreadyImported:
            oldEvent['files'].append(newFile)
            if firstDateIsEarlier(newFile['time_of_creation'], oldEvent['start_date']):
                oldEvent['start_date']['year'] = newFile['time_of_creation']['year']
                oldEvent['start_date']['month'] = newFile['time_of_creation']['month']
                oldEvent['start_date']['day'] = newFile['time_of_creation']['day']

    with open(pathToJson, 'w') as f:
        json.dump(oldEvent, f)



def main():
    """Main function of the script. Create globals. TODO: Parse localSettings for directories."""
    global archiveStructure
    global archiveDir
    global eventDir
    global importedFiles

    script_location = os.path.realpath(os.path.join(os.getcwd(), os.path.dirname(__file__)))

    # Load the settings
    with open(os.path.join(script_location, 'settings.json'), 'r') as f:
        settings = json.load(f)

    # Load the localsettings
    with open(os.path.join(script_location, 'local_settings.json'), 'r') as f:
        local_settings = json.load(f)

    archiveStructure = settings['photoArchive']['structure']

    archiveDir = local_settings['archiveDir']

    eventDir = local_settings['eventDir']

    parseImportFolder(local_settings['importPath'])



if __name__ == '__main__':
    main()
