## Intro ##
The script runs a few steps in order to backup and upload the backup to dropbox and the BRCK.

* Create a backup for all the database and saves it on /backups . This uses mysqldump --single-transaction so it is lock safe;
* Zips the '.sql' file created by the mysqldump and also deletes the .sql file to save storage;
* Checks for internet connection. If connection is found, send files to Dropbox. Store the name of the file sent in uploaded_to_dropbox.txt
* Check for connection to the BRCK. If connection is found, send files to the BRCK. Store the name of the file sent int uploaded_to_brck.txt
* Cleans old files on the BRCK and also locally

## Usage ##

This script requires python as well as Dropbox, Paramiko and !(https://github.com/jbardin/scp.py)[SCP] libraries.

Some information is needed for using this script: MySQL Credentials, BRCK credentials and Dropbox Auth Token.

**WARNING: Right now it is using the root user on the BRCK**