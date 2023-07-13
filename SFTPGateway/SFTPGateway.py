import pysftp
import paramiko
import sys
import warnings
import argparse
import io
import os
from base64 import decodebytes

warnings.filterwarnings("ignore")

# Declare Global Variables
global myHostName, myUserName, myPortNo, myPassword, myCnOpts
global myLocalFileFolderPath, myRemoteFileFolderPath, myFileExtension, myFileFullName
global myActionType, myLocalFilePath, myRemoteFilePath, myKnownHostFilePath
global myPrivateKeyFilePath, myPrivateKeyFilePassPhrase, myKeyDataValue, myKeyData, myKey, myTableName
global myFileList, status

# Initializing Global Variable and Setting Default Values
myHostName = ""
myPortNo = ""
myUserName = ""
myPassword = ""
myPrivateKeyFilePath = ""
myLocalFileFolderPath = ""
myRemoteFileFolderPath = ""
myFileFullName = ""
myFileExtension = ""
myKeyDataValue = ""
myKnownHostFilePath = ""
myActionType = ""
myFileList = []
status = ""
myCnOpts = ""
ProgramName = os.path.basename(__file__)

# Definition for Python SFTP
def PythonSFTP(*args):
    try:   
        args = args[0]
        # Collect command line arguments and assign
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
            
        if "-LocalFileFolderPath" in args:
            myLocalFileFolderPath = args[args.index("-LocalFileFolderPath") + 1]
        else:
            raise Exception("Local File Folder Path was not provided")
            
        if "-RemoteFileFolderPath" in args:
            myRemoteFileFolderPath = args[args.index("-RemoteFileFolderPath") + 1]
        else:
            raise Exception("Remote File Folder Path was not provided")
        
        if "-KnownHostFilePath" in args:
            myKnownHostFilePath = args[args.index("-KnownHostFilePath") + 1]
        else:
            myKnownHostFilePath = ""

        if "-KeyDataValue" in args:
            myKeyDataValue = args[args.index("-KeyDataValue") + 1]
        else:
            myKeyDataValue = ""

        if (myKnownHostFilePath == "" and myKeyDataValue == ""):
            raise Exception("Known Host File Path or Key Data Value was not provided")
        
        if "-FTPPassword" in args:
            myPassword = args[args.index("-FTPPassword") + 1]
        else:
            myPassword = ""      
    
        if "-PrivateKeyFilePath" in args:
            myPrivateKeyFilePath = args[args.index("-PrivateKeyFilePath") + 1]
        else:
            myPrivateKeyFilePath = ""

        if "-PrivateKeyFilePassPhrase" in args:
            myPrivateKeyFilePassPhrase = args[args.index("-PrivateKeyFilePassPhrase") + 1]
        else:
            myPrivateKeyFilePassPhrase = ""    

        if (myPassword == "" and  myPrivateKeyFilePath == ""):
            raise Exception("FTP Login Password or  Private Key File Path should be provided")

        if "-ActionType" in args:
            myActionType = args[args.index("-ActionType") + 1]
        else:
            raise Exception("Action Type (Put/Get) was not provided")

        if "-FileExtension" in args:
            myFileExtension = args[args.index("-FileExtension") + 1]
        else:
            raise Exception("File Extension was not provided")

        if "-FileFullName" in args:
            myFileFullName = args[args.index("-FileFullName") + 1]
        else:
            raise Exception("File Input Name was not provided")
        
        if (myKeyDataValue != ""):
            print("Host Key Data Value : " + str(myKeyDataValue))
            myKeyData = myKeyDataValue.encode("utf-8") 
            myKey = paramiko.RSAKey(data=decodebytes(myKeyData))
            myCnOpts = pysftp.CnOpts()
            myCnOpts.hostkeys.add(myHostName, "ssh-rsa", myKey)
            print("Host Key Data Value Succesfully Added to SFTP Connection ... ")
        else:
           print("Known Host File Path : " + str(myKnownHostFilePath))
           myCnOpts = pysftp.CnOpts()    
           myCnOpts = pysftp.CnOpts(knownhosts=myKnownHostFilePath)
           print("Known Host File Path Succesfully Added to SFTP Connection ... ")

        warnings.filterwarnings('default')
        print("FTP Host Name : " + str(myHostName))
        print("FTP Port No : " + str(myPortNo))
        print("FTP User Name : " + str(myUserName))
        if (myPassword != ""):
            print("FTP Password (Not Visible) : " + str('XXXXXXXXXX'))
            
        print("Private Key File Path : " + str(myPrivateKeyFilePath))
        print("Local File Folder Path : " + str(myLocalFileFolderPath))
        print("Remote File Folder Path : " + str(myRemoteFileFolderPath))
        print("Full File Name : " + str(myFileFullName))
        print("File Extension : " + str(myFileExtension))
        print("FTP Host Key Data Value : " + str(myKeyDataValue))
        print("Action Type : " + str(myActionType))
        with pysftp.Connection(host=myHostName, port=int(myPortNo), username=myUserName, private_key=myPrivateKeyFilePath,  cnopts=myCnOpts) as sftp:
            print("SFTP Connection Successfully Established ... ")

            # File Put Method (Upload)            
            if (myActionType == "Put"):    
                # Passed File Name from the Calling Program
                myLocalFilePath = os.path.join(myLocalFileFolderPath, myFileFullName)
                myRemoteFilePath = os.path.join(myRemoteFileFolderPath , myFileFullName)
                print("File " + myLocalFilePath + "  Upload Started to Remote Server... ")
                # Adding Elements to List
                myFileList.append(myFileFullName)   
                # Uploading the File to Remote Server using Put Method
                sftp.chmod(myRemoteFilePath, 766)
                sftp.put(myLocalFilePath, myRemoteFilePath,preserve_mtime=True)
                # Use Change Working Directory to Remote
                sftp.cwd(myRemoteFileFolderPath)
                # Obtain structure of the remote directory
                directory_structure = sftp.listdir_attr()
                # Print data
                for attr in directory_structure:
                    if (sftp.exists(attr.filename) == False and attr.filename in myFileList):
                        raise Exception("File " + attr.filename + " has not been Uploaded Successfully to Remote Server... ")
                    if (sftp.exists(attr.filename) == True and attr.filename in myFileList):
                        print("File " + myLocalFilePath + " has been Uploaded Succesfully to Remote Server... ")                       
            # File Get Method (Upload)             
            else:
                # Passed File Name from the Calling Program
                myLocalFilePath = os.path.join(myLocalFileFolderPath, myFileFullName)
                myRemoteFilePath = os.path.join(myRemoteFileFolderPath , myFileFullName)
                print("File " + myRemoteFilePath + "  Download Started to Local Server... ")
                # Adding Elements to List
                myFileList.append(myFileFullName) 
                # Downloading the File to Local Server using Get Method
                sftp.chmod(myLocalFilePath, 766)
                sftp.get(myRemoteFilePath, myLocalFilePath, preserve_mtime=True)
                # Print data
                for entry in os.scandir(myLocalFileFolderPath):
                    if (os.path.isfile(entry.path) == False and os.path.basename(entry.path) in myFileList):
                        raise Exception("File " + os.path.basename(entry.path) + " has not been Downloaded Successfully on Local Server... ")
                    if (os.path.isfile(entry.path) == True and os.path.basename(entry.path) in myFileList):
                        print("File " + os.path.basename(entry.path) + "has been Downloaded Successfully on Local Server... ")  
                          
        return 0
    except Exception as e:
        print("Error Message (e):",str(e))
        return 1
    finally:
        if (sftp):
            sftp.close()
            
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

