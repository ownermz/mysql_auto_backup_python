# Include the Dropbox SDK
import dropbox
import glob
import urllib2
import os
import time
import zlib
import zipfile



import datetime

import paramiko
from scp import SCPClient


def init ():

    tries = 3
    backupDatabase()
    while tries > 0:
        checkDropbox = uploadDropbox()
        checkBrck = uploadBrck()

        if checkBrck and checkDropbox:
            break
        tries -= 1
        if tries > 0:
            if not checkBrck:
                print "Error when uploading to the BRCK"
            if not checkDropbox:
                print "Error when uploading to dropbox"
				
            print "Waiting 30 seconds to retry. Trying more " + str(tries) + " times"
            time.sleep(30)

    cleanBackups()

    return


def cleanBackups():
    print "Checking files to be cleaned"
    with open('uploaded_to_brck.txt') as logFile:
        lines = logFile.read().splitlines()

    try:
        ssh = createSSHClient()
        scp = SCPClient(ssh.get_transport())

        ##
        #Checks for last modified date on file and remove if it is older than 30 days
        dir_to_search = 'backups/'
        for dirpath, dirnames, filenames in os.walk(dir_to_search):
           for file in filenames:
              curpath = os.path.join(dirpath, file)
              file_modified = datetime.datetime.fromtimestamp(os.path.getmtime(curpath))
              if len(filenames) > 30 and datetime.datetime.now() - file_modified > datetime.timedelta(days=30):
                  if 'backups/'+file in lines:
                      print 'Removing '+file+' from the BRCK'
                      ssh.exec_command('rm /home/openmrs/backups/'+file)

                      f = open("uploaded_to_brck.txt","w")
                      for line in lines:
                          if line!="backups/"+file:
                            f.write(line +"\n")
                      f.close()
                  os.remove(curpath)

        ssh.close()
    except:
        print 'Failed connecting to the BRCK'


    return


def backupDatabase ():
    user = 'dbbackup'
    password = 'backupopenmrs'
    host ='localhost'
    file_name = 'backup-'+time.strftime("%d-%m-%Y")+time.strftime("%H%M")

    print 'Dumping database to backups/'+file_name+'.sql'


    os.system('mysqldump --single-transaction --user='+user+' --password='+password+' --host='+host+' openmrs > "backups/'+file_name+'.sql"')


    print 'Zipping MySQL dump'
    zf = zipfile.ZipFile('backups/'+file_name+'.zip', "w", zipfile.ZIP_DEFLATED)
    try:
        zf.write('backups/'+file_name+'.sql')
    finally:
        zf.close()
        os.remove('backups/'+file_name+'.sql')

    return


def uploadDropbox ():

    if internet_on():
        # Get your app key and secret from the Dropbox developer website

        try:
            print 'Connecting to Dropbox'
            client = dropbox.client.DropboxClient('YF9nIzoNBSAAAAAAAAAABvso-pNu0CgnHnbe-lTNVEu-m0d0nShJJh5Mq8LrRz7A')

            with open('uploaded_to_dropbox.txt') as logFile:
                lines = logFile.read().splitlines()

            # Writing log file
            log = open('uploaded_to_dropbox.txt', 'a')
            #Checks for files to be uploaded
            for file in glob.glob("backups/*.zip"):
                if file not in lines:
                    print 'Uploading ' + file
                    f = open(file, 'rb')
                    fileName = file.replace("\\", "/")
                    #Uploads to dropbox
                    response = client.put_file(fileName, f)
                    #If file is uploaded, add filename to log
                    if response:
                        print 'Uploaded with Success'
                        log.write( file +'\n' )
        except:
            print "Error uploading to dropbox"
            return False
    else:
        print 'No internet connection'
        return False

    return True


def createSSHClient():
    server, username, password = ('192.168.69.1', 'root', '$c@mpTurkaNa!')
    ssh = paramiko.SSHClient()
    ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
    #Loads the user's local known host file.
    ssh.connect(server, username=username, password=password)

    return ssh


def uploadBrck ():
    #####
    # Upload files to BRCK
    try:
        print 'Connecting to the BRCK'
        ssh = createSSHClient()
        scp = SCPClient(ssh.get_transport())

        with open('uploaded_to_brck.txt') as logFile:
            lines = logFile.read().splitlines()

        log = open('uploaded_to_brck.txt', 'a')
        #Checks for files to be uploaded
        for file in glob.glob("backups/*.zip"):
            if file not in lines:
                print 'Uploading ' + file
                f = open(file, 'rb')
                scp.put(file, '/home/openmrs/backups');
                log.write(file + '\n')
        log.close();

        ssh.close()
        return True
    except:
        print "Failed connecting to the BRCK. Check if PC is connected to the BRCK WiFi"
        return False

    return False


def internet_on():
    try:
        response=urllib2.urlopen('http://www.google.com',timeout=1)
        return True
    except urllib2.URLError as err: pass
    return False


init()