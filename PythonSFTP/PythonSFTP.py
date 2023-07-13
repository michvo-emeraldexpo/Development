import pysftp
import sys
import re
import os
import paramiko
import warnings
import pyodbc
import argparse
import io
import logging
import math
import uuid
import stat
import hashlib as hl
from suds.sudsobject import asdict
from pathlib import Path
from getpass import getpass
from base64 import decodebytes
from datetime import datetime

## Parameter Passing Options
##Option 1 :
##Option 2 :
##Option 3 :
##Option 4 :
##Option 5 :
##Option 6 :
##Option 7 :
##Option 8 :

warnings.filterwarnings("ignore")
# Declare Global Variables
global databaseservername, databasename, databaseusername, databasepassword, databasetrustedconnection
global myHostName, myUserName, myPortNo, myPassword, myCnopts
global myLocalFileFolderPath, myRemoteFileFolderPath, myFileNameLike, myFileExtension, myFileInputName, myLocalFilePath, myRemoteFilePath
global myRequestType, myFileQuantityType
global myPrivateKeyFileFolderPath, myPrivateKeyFileName, myPrivateKeyFilePath, myKeyDataValue, myKeyData, myKey, myTableName
global myFileList, status, mydbDefaults, myFingerPrint
global Phase, PhaseId, ProgramName, ProcessLogId, Status, StatusId, Comment, ErrorComment, Severity, SeverityId 

# Default Values for Global Variables
myHostName = "mchfjxgbj-l4-d163d99tscz72z4.ftp.marketingcloudops.com"
myPortNo = "22"
myUserName = "514006106"
myPassword = ""
myFingerPrint = "ssh-rsa 2048 46:27:cf:11:74:fd:ee:32:a3:d5:25:99:b3:09:51:0b"
myPrivateKeyFileFolderPath = "D:\\Emerald\\Webhook\\SFMCIntegration"
myPrivateKeyFileName = "mcftp_private_key"
myLocalFileFolderPath = "D:\\Import\\TMM"
myRemoteFileFolderPath = "/Triggered_Automations/PaperForm/DailySubscriptions"
myFileInputName = "v2CustomerSearchCDH_Export_01062021_105900.csv"
myFileNameLike = "v2CustomerSearchCDH"
myFileExtension = ".csv"
myKeyDataValue = "AAAAB3NzaC1yc2EAAAABEQAAAQEAv5QrAMTfr6Eg/8U/wRDvTILxQKqRPS18mMcw1rAT6a/OpgUkXJb8nypwO8lA9+4aptESCQ2auez3n1qP10oLWwUfNYQETv/bs8iCsblmqonTmSMBN+qkbiQE2aeYuFDfYokaE+UYz4r4QhOLFgjsE+CwGXwc+honc6X5aXvOeY+Sj29xQBJU3wvFpNQZXy4VFVhhuTJlVoeaaYfpDjwyOtcOpAP5YBPG0p19KHcMt7+VCbUbYTjBO6FTocdfM9SZVCDZPf8jD3dxqmLlAk/p5bWtPoiDFxeZgvebpEk5gjIIVOUBc8VNDzpzDOjpuav4/jtFI4LJm4fmKVIAmyPjDQ=="
myRequestType = "Get"
myFileQuantityType = "Single"
myFileList = []
myTableName = ""
status = ""
myCnopts = ""
Phase = "SFTP"
PhaseId = ""
ProcessLogId = ""
Status = "Success"
StatusId = ""
Comment = ""
ErrorComment = ""
Severity = "High"
SeverityId = ""
myTableName = "dbo.FormSubmissionProduct"
ProgramName = os.path.basename(__file__)

dbDefaults={'databaseservername':'edw-db-dev'}
dbDefaults['databasename']  = 'EDW_DM'
dbDefaults['databaseusername']  = 'EMERALD_API'
dbDefaults['databasepassword']  = 'xxxxxxxx'
dbDefaults['databasetrustedconnection']  = 'Yes'

def condition(x):
    return x!=""

def trim_fingerprint(fingerprint):
    if fingerprint.startswith("ssh-rsa 2048 "):
        return fingerprint[len("ssh-rsa 2048 "):]
    return fingerprint
def clean_fingerprint(fingerprint):
    return trim_fingerprint(fingerprint).replace(":", "")

class FingerprintKey:
    def __init__(self, fingerprint):
        self.fingerprint = clean_fingerprint(fingerprint)
    def compare(self, other):
        if callable(getattr(other, "get_fingerprint", None)):
            return other.get_fingerprint() == self.fingerprint
        elif clean_fingerprint(other) == self.get_fingerprint():
            return True
        #elif md5(other).digest().encode("hex") == self.fingerprint:
        elif hl.md5(other).hexdigest() == self.fingerprint:
            return True
        else:
            return False
    def __cmp__(self, other):
        return self.compare(other)
    def __contains__(self, other):
        return self.compare(other)
    def __eq__(self, other):
        return self.compare(other)
    def __ne__(self, other):
        return not self.compare(other)
    def get_fingerprint(self):
        return self.fingerprint
    def get_name(self):
        return u"ssh-rsa"
    def asbytes(self):
         # Note: This returns itself.
         #   That way when comparisons are done to asbytes return value,
         #   this class can handle the comparison.
        return self
    
# Definition for Python SFTP
def PythonSFTP(*args):
    try:   
        args = args[0]
        # Collect command line arguments and assign
        # Database Arguments
        if "-DatabaseServerName" in args:
            databaseservername = args[args.index("-DatabaseServerName") + 1]
        else:
            databaseservername= dbDefaults["databaseservername"]
            
        if "-Databasename" in args:
            databasename = args[args.index("-Databasename") + 1]
        else:
            databasename = dbDefaults["databasename"]        
    
        if "-DatabaseUserName" in args:
            databaseusername = args[args.index("-DatabaseUserName") + 1]
        else: 
            databaseusername = dbDefaults["databaseusername"]
    
        if "-DatabasePassword" in args:
            databasepassword = args[args.index("-DatabasePassword") + 1]
        else:
            databasepassword = dbDefaults["databasepassword"]
            
        if "-DatabaseTrustedConnection" in args:
            databasetrustedconnection = args[args.index("-DatabaseTrustedConnection") + 1]
        else:
            databasetrustedconnection = dbDefaults["databasetrustedconnection"]
            
        # Database Connection Opening and Initiating Cursor
        conn_string = "DRIVER={ODBC Driver 17 for SQL Server};SERVER=" + databaseservername + ";DATABASE=" + databasename + ";Trusted_Connection=" + databasetrustedconnection + ";"
        conn = pyodbc.connect(conn_string)
        cursor = conn.cursor()

        # FTP Arguments    
        if "-FTPHostName" in args:
            myHostName = args[args.index("-FTPHostName") + 1]
        else:
            raise Exception("FTP Host Name was not provided")
        
        if "-FTPPortNo" in args:
            myPortNo = args[args.index("-FTPPortNo") + 1]
        else:
            raise Exception("FTP Port Number was not provided")
        
        if "-FTPUserName" in args:
            myUserName = args[args.index("-FTPUserName") + 1]
        else:
            raise Exception("FTP Login UserName was not provided")
            
        if "-FTPPassword" in args:
            myPassword = args[args.index("-FTPPassword") + 1]
        else:
            myPassword = ""
            
        if "-FTPFingerPrint" in args:
            myFingerPrint = args[args.index("-FTPFingerPrint") + 1]
        else:
            myFingerPrint = ""    
    
        if "-LocalFileFolderPath" in args:
            myLocalFileFolderPath = args[args.index("-LocalFileFolderPath") + 1]
        else:
            raise Exception("Local File Folder Path was not provided")
            
        if "-RemoteFileFolderPath" in args:
            myRemoteFileFolderPath = args[args.index("-RemoteFileFolderPath") + 1]
        else:
            raise Exception("Remote File Folder Path was not provided")
    
        if "-PrivateKeyFileFolderPath" in args:
            myPrivateKeyFileFolderPath = args[args.index("-PrivateKeyFileFolderPath") + 1]
        else:
            myPrivateKeyFileFolderPath = ""

        if "-PrivateKeyFileName" in args:
            myPrivateKeyFileName = args[args.index("-PrivateKeyFileName") + 1]
        else:
            myPrivateKeyFileName= ""

        if ((myPassword == "" or myFingerPrint == "") and (myPrivateKeyFileFolderPath == "" or myPrivateKeyFileFolderPath == "")):
            raise Exception("FTP Login Password with FTP Finger Print or  Private Key File Folder Path with Private Key File Name should be provided")

        if "-RequestType" in args:
            myRequestType = args[args.index("-RequestType") + 1]
        else:
            raise Exception("Request Type (Put/Get) was not provided")

        if "-FileQuantityType" in args:
            myFileQuantityType = args[args.index("-FileQuantityType") + 1]
        else:
            raise Exception("File Quantity Type (Single/Multiple) was not provided")
        
        if "-FileNameLike" in args:
            myFileNameLike = args[args.index("-FileNameLike") + 1]

        if "-FileExtension" in args:
            myFileExtension = args[args.index("-FileExtension") + 1]
        else:
            raise Exception("File Extension was not provided")

        if "-FileInputName" in args:
            myFileInputName = args[args.index("-FileInputName") + 1]

        if (myFileInputName == "" and myFileNameLike == ""):
            raise Exception("File Input Name or  File Name Like has to be provided")
        
        if "-TableName" in args:
            myTableName = args[args.index("-TableName") + 1]
        else:
            raise Exception("Table Name was not provided")

        try:
            # Get Phase Id
            print("Start : Getting PhaseId from dbo.Phase Table")
            getsql = """
                          DECLARE @PhaseId INT;
                          EXEC dbo.usp_GetPhase @Phase = ?, @PhaseID = @PhaseId OUTPUT;
                          SELECT @PhaseId AS PhaseId;
                     """
            cursor.execute(getsql, str(Phase))
            row = cursor.fetchone()
            PhaseId = row[0]
            print("Phase Id :" + str(row[0]))
            print("End : Getting PhaseId from dbo.Phase Table")

            # Create a Record in Process Log Table
            print("Start : Create a Record in dbo.ProcessLog Table")
            insertsql = """
                            DECLARE @ProcessLogId INT;
                            EXEC dbo.usp_CreateProcessLog @TableName = ?, @Program = ?, @SourceTable = ?, @PhaseId = ?, @ProcessLogId = @ProcessLogId OUTPUT;
                            SELECT @ProcessLogId AS ProcessLogId;
                        """
            cursor.execute(insertsql, str(myRemoteFileFolderPath), str(ProgramName), str(myLocalFileFolderPath), PhaseId)
            row = cursor.fetchone()
            ProcessLogId = row[0]
            print("Process Log Id :" + str(row[0]))
            print("End : Create a Record in dbo.ProcessLog Table")
            
            myPrivateKeyFilePath = os.path.join(myPrivateKeyFileFolderPath, myPrivateKeyFileName)
            print("Private Key File Path :" + str(myPrivateKeyFilePath))

            if (myPassword != ""):
                myCnopts = pysftp.CnOpts()
                myCnopts.hostkeys.clear()
                myCnopts.hostkeys.add(myHostName, "ssh-rsa", FingerprintKey(myFingerPrint))
                print(FingerprintKey(myFingerPrint))
                print("Host Key Succesfully Added ... ")
            else:    
                if (myKeyDataValue != ""):
                    myKeyData = myKeyDataValue.encode("utf-8") 
                    myKey = paramiko.RSAKey(data=decodebytes(myKeyData))
                    myCnopts = pysftp.CnOpts()
                    myCnopts.hostkeys.add(myHostName, "ssh-rsa", myKey)
                    print("Host Key Succesfully Added ... ")
                else:
                   myCnopts = pysftp.CnOpts()    
                   myCnopts.hostkeys = None
                   print("Host Key Not Succesfully Added ... ")

            warnings.filterwarnings('default')
            # Connecting SFTP using Password
            if (myPassword != ""):
                print("Connecting SFTP using Password")
                with pysftp.Connection(host=myHostName, port=int(myPortNo), username=myUserName, password=myPassword, cnopts=myCnopts) as sftp:
                    print("Connection Succesfully Established ... ")
                    # FilePut Method (Upload)
                    if (myRequestType == "Put"):
                        if (myFileQuantityType == "Multiple"):
                            # Get List of Files to be Uploaded from Local Working Folder
                            for entry in os.scandir(myLocalFileFolderPath):
                                if ((entry.path.find(myFileNameLike) != -1) and entry.path.endswith(myFileExtension)) and entry.is_file():
                                    myLocalFilePath = entry.path
                                    myRemoteFilePath = os.path.join(myRemoteFileFolderPath , os.path.basename(entry.path))
                                    print("File " + myLocalFilePath + "  Uploaded Started to Remote Server... ")
                                    # Uploading the File to Remote Server using Put Method
                                    sftp.put(myLocalFilePath, myRemoteFilePath,preserve_mtime=True)
                                    # Adding Elements to List
                                    myFileList.append(os.path.basename(entry.path))   
                                    sftp.chmod(myRemoteFilePath, 777)
                                    print("File " + myLocalFilePath + "  Uploaded Succesfully to Remote Server... ")
                        else:
                                    # Passed File Name from the Calling Program
                                    myLocalFilePath = os.path.join(myLocalFileFolderPath, myFileInputName)
                                    myRemoteFilePath = os.path.join(myRemoteFileFolderPath , myFileInputName)
                                    print("File " + myLocalFilePath + "  Uploaded Started to Remote Server... ")
                                    # Uploading the File to Remote Server using Put Method
                                    sftp.put(myLocalFilePath, myRemoteFilePath,preserve_mtime=True)
                                    # Adding Elements to List
                                    myFileList.append(myFileInputName)   
                                    sftp.chmod(myRemoteFilePath, 777)
                                    print("File " + myLocalFilePath + "  Uploaded Succesfully to Remote Server... ")
                    # File Get Method (Download)            
                    else:
                        if (myFileQuantityType == "Multiple"):
                            # Get List of Files to be Downloaded from Remote Working Folder
                            for entry in sftp.listdir(myRemoteFileFolderPath):
                                if ((entry.find(myFileNameLike) != -1) and entry.endswith(myFileExtension)) and stat.S_ISREG(sftp.stat(os.path.join(myRemoteFileFolderPath, entry)).st_mode): 
                                    myLocalFilePath = os.path.join(myLocalFileFolderPath, entry)
                                    myRemoteFilePath = os.path.join(myRemoteFileFolderPath, entry)
                                    print("File " + myRemoteFilePath + "  Downloaded Started to Local Server... ")
                                    # Downloading the File to Local Server using Get Method
                                    sftp.get(myRemoteFilePath, myLocalFilePath, preserve_mtime=True)
                                    # Adding Elements to List
                                    myFileList.append(entry)   
                                    sftp.chmod(myLocalFilePath, 777)
                                    print("File " + myRemoteFilePath + "  Downloaded Succesfully to Local Server... ")
                        else:
                                    # Passed File Name from the Calling Program
                                    myLocalFilePath = os.path.join(myLocalFileFolderPath, myFileInputName)
                                    myRemoteFilePath = os.path.join(myRemoteFileFolderPath , myFileInputName)
                                    print("File " + myRemoteFilePath + "  Downloaded Started to Local Server... ")
                                    # Downloading the File to Local Server using Get Method
                                    sftp.get(myRemoteFilePath, myLocalFilePath, preserve_mtime=True)
                                    # Adding Elements to List
                                    myFileList.append(myFileInputName)   
                                    sftp.chmod(myLocalFilePath, 777)
                                    print("File " + myRemoteFilePath + "  Downloaded Succesfully to Local Server... ")
                                    
                                
                    # File Validation (Remote Server)            
                    if (myRequestType == "Put"):
                        # Use Change Working Directory to Remote
                        sftp.cwd(myRemoteFileFolderPath)
                        # Obtain structure of the remote directory '/var/www/vhosts'
                        directory_structure = sftp.listdir_attr()
                        # Print data
                        for attr in directory_structure:
                            if (sftp.exists(attr.filename) == True and attr.filename in myFileList):
                                print("File " + attr.filename + " Existence Validated Successfully on Remote Server... ")
                    #File Validation (Local Server)            
                    else:
                        # Print data
                        for entry in os.scandir(myLocalFileFolderPath):
                            if (os.path.isfile(entry.path) == True and os.path.basename(entry.path) in myFileList):
                                print("File " + os.path.basename(entry.path) + " Existence Validated Successfully on Local Server... ")                    
            else:
                # Connecting SFTP using Private Key
                print("Connecting SFTP using Private Key")
                with pysftp.Connection(host=myHostName, port=int(myPortNo), username=myUserName, private_key=myPrivateKeyFilePath,  cnopts=myCnopts) as sftp:
                    print("Connection Succesfully Established ... ")
                    # FilePut Method (Upload)
                    if (myRequestType == "Put"):
                        if (myFileQuantityType == "Multiple"):
                            # Get List of Files to be Uploaded from Local Working Folder
                            for entry in os.scandir(myLocalFileFolderPath):
                                if ((entry.path.find(myFileNameLike) != -1) and entry.path.endswith(myFileExtension)) and entry.is_file():
                                    myLocalFilePath = entry.path
                                    myRemoteFilePath = os.path.join(myRemoteFileFolderPath , os.path.basename(entry.path))
                                    print("File " + myLocalFilePath + "  Uploaded Started to Remote Server... ")
                                    # Uploading the File to Remote Server using Put Method
                                    sftp.put(myLocalFilePath, myRemoteFilePath,preserve_mtime=True)
                                    # Adding Elements to List
                                    myFileList.append(os.path.basename(entry.path))   
                                    sftp.chmod(myRemoteFilePath, 777)
                                    print("File " + myLocalFilePath + "  Uploaded Succesfully to Remote Server... ")
                        else:
                                    # Passed File Name from the Calling Program
                                    myLocalFilePath = os.path.join(myLocalFileFolderPath, myFileInputName)
                                    myRemoteFilePath = os.path.join(myRemoteFileFolderPath , myFileInputName)
                                    print("File " + myLocalFilePath + "  Uploaded Started to Remote Server... ")
                                    # Uploading the File to Remote Server using Put Method
                                    sftp.put(myLocalFilePath, myRemoteFilePath,preserve_mtime=True)
                                    # Adding Elements to List
                                    myFileList.append(myFileInputName)   
                                    sftp.chmod(myRemoteFilePath, 777)
                                    print("File " + myLocalFilePath + "  Uploaded Succesfully to Remote Server... ")
                    # File Get Method (Download)            
                    else:
                        if (myFileQuantityType == "Multiple"):
                            # Get List of Files to be Downloaded from Remote Working Folder
                            for entry in sftp.listdir(myRemoteFileFolderPath):
                                if ((entry.find(myFileNameLike) != -1) and entry.endswith(myFileExtension)) and stat.S_ISREG(sftp.stat(os.path.join(myRemoteFileFolderPath, entry)).st_mode): 
                                    myLocalFilePath = os.path.join(myLocalFileFolderPath, entry)
                                    myRemoteFilePath = os.path.join(myRemoteFileFolderPath, entry)
                                    print("File " + myRemoteFilePath + "  Downloaded Started to Local Server... ")
                                    # Downloading the File to Local Server using Get Method
                                    sftp.get(myRemoteFilePath, myLocalFilePath, preserve_mtime=True)
                                    # Adding Elements to List
                                    myFileList.append(entry)   
                                    sftp.chmod(myLocalFilePath, 777)
                                    print("File " + myRemoteFilePath + "  Downloaded Succesfully to Local Server... ")
                        else:
                                    # Passed File Name from the Calling Program
                                    myLocalFilePath = os.path.join(myLocalFileFolderPath, myFileInputName)
                                    myRemoteFilePath = os.path.join(myRemoteFileFolderPath , myFileInputName)
                                    print("File " + myRemoteFilePath + "  Downloaded Started to Local Server... ")
                                    # Downloading the File to Local Server using Get Method
                                    sftp.get(myRemoteFilePath, myLocalFilePath, preserve_mtime=True)
                                    # Adding Elements to List
                                    myFileList.append(myFileInputName)   
                                    sftp.chmod(myLocalFilePath, 777)
                                    print("File " + myRemoteFilePath + "  Downloaded Succesfully to Local Server... ")
                                    
                                
                    # File Validation (Remote Server)            
                    if (myRequestType == "Put"):
                        # Use Change Working Directory to Remote
                        sftp.cwd(myRemoteFileFolderPath)
                        # Obtain structure of the remote directory '/var/www/vhosts'
                        directory_structure = sftp.listdir_attr()
                        # Print data
                        for attr in directory_structure:
                            if (sftp.exists(attr.filename) == True and attr.filename in myFileList):
                                print("File " + attr.filename + " Existence Validated Successfully on Remote Server... ")
                    #File Validation (Local Server)            
                    else:
                        # Print data
                        for entry in os.scandir(myLocalFileFolderPath):
                            if (os.path.isfile(entry.path) == True and os.path.basename(entry.path) in myFileList):
                                print("File " + os.path.basename(entry.path) + " Existence Validated Successfully on Local Server... ")
                    
            # Get Status Id
            print("Start : Getting StatusId from dbo.Status Table")
            Status = "Success"
            getsql = """
                          DECLARE @StatusId INT;
                          EXEC dbo.usp_GetStatusID @Name = ?, @StatusId = @StatusId OUTPUT;
                          SELECT @StatusId AS StatusId;
                     """
            cursor.execute(getsql, Status)
            row = cursor.fetchone()
            StatusId = row[0]
            print("Status Id :" + str(row[0]))
            print("End : Getting StatusId from dbo.Status Table")
            
            Comment = "File(s) " + str(",".join(myFileList)) + " Uploaded Successfully to Remote Server"

            # Update Record in Process Log Table
            print("Start : Update a Record in dbo.ProcessLog Table")
            updatesql = "EXEC dbo.usp_UpdateProcessLog @ProcessLogId = ?, @EndTime = ?, @StatusId = ?, @RecordProcessed = ?, @RecordWithError = 0, @Comment = ?"
            cursor.execute(updatesql, ProcessLogId, datetime.now(), StatusId, len(myFileList), str(Comment))
            print("End : Update a Record in dbo.ProcessLog Table")
            #cursor.execute(updatesql, int(ProcessLogId), int(StatusId), sum(condition(x) for x in myFileList) , str(Comment))
            
            conn.commit()
           
            return 0
        
        except pyodbc.Error as ex1:
                    print("Error Message (ex1):", str(ex1))
                    raise ex1
                    return 1
        except pyodbc.DatabaseError as ex2:
                    print("Database Error Message (ex2):",str(ex2))
                    cursor.rollback()
                    raise ex2
                    return 1
    except Exception as e:
        print("Error Message (e):",str(e))
        
        # Get Severity Id
        print("Start: Getting SeverityId from dbo.Severity Table")
        Severity = "High"
        getsql = """
                      SELECT dbo.udf_GetSeverityId(?) AS SeverityId;
                 """
        cursor.execute(getsql, Severity)
        row = cursor.fetchone()
        SeverityId = row[0]
        print("Severity Id :" + str(row[0]))
        print("End: Getting SeverityId from dbo.Severity Table")
        
        ErrorComment = "SFTP Failed with one or more data exception"

        # Create a Record in Error Log Table
        print("Start: Create a Record in dbo.ErrorLog Table")
        insertql = "EXEC dbo.usp_LogError @Program  = ?, @TableName = ?, @ProcessLogId = ?, @Severity = ?, @Comment = ?, @ExceptionMessage = ?"
        cursor.execute(insertql, str(ProgramName), str(myTableName), ProcessLogId, SeverityId, str(ErrorComment), str(e))
        print("End: Create a Record in dbo.ErrorLog Table")
        
        # Get Status Id
        print("Start: Getting StatusId from dbo.Status Table")
        Status = "Failed"
        getsql = """
                      DECLARE @StatusId INT;
                      EXEC dbo.usp_GetStatusID @Name = ?, @StatusId = @StatusId OUTPUT;
                      SELECT @StatusId AS StatusId;
                 """
        cursor.execute(getsql, Status)
        row = cursor.fetchone()
        StatusId = row[0]
        print("Status Id :" + str(row[0]))
        print("End: Getting StatusId from dbo.Status Table")
        
        # Update Record in Process Log Table
        print("Start: Update a Record in dbo.ProcessLog Table")
        updatesql = "EXEC dbo.usp_UpdateProcessLog @ProcessLogId = ?, @EndTime = ?, @StatusId = ?, @RecordProcessed = ?, @RecordWithError = ?, @Comment = ?"
        cursor.execute(updatesql, ProcessLogId, datetime.now(), StatusId, len(myFileList), 0, str(ErrorComment))
        print("End: Update a Record in dbo.ProcessLog Table")
        
        if (conn):
            conn.commit()
            print("Database Commit Issued")

        return 1
    finally:
        if (cursor):
                cursor.close()
                print("Database Cursor Closed")       
        if (cursor):        
            del cursor
            print("Database Cursor Deleted/Deallocated")
        if (conn):
                conn.close()
                print("Database Connection Closed")

def main(*args):         
        status = PythonSFTP(sys.argv)
        print("Return/Execution Status : ", str(status))
        return status
       
if (__name__ == "__main__"):
      status = main(sys.argv)
      if (status == 1):
        sys.exit(1)
      else:
        sys.exit(0)    
