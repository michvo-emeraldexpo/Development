import pysftp
import sys
import re
import os
from base64 import decodebytes
import paramiko
import warnings
import stat

warnings.filterwarnings("ignore")

myHostName = "mchfjxgbj-l4-d163d99tscz72z4.ftp.marketingcloudops.com"
myUserName = "514006106"
myPrivateKeyPath = "D:\\Emerald\\Webhook\\SFMCIntegration\\mcftp_private_key"
myLocalFileFolder = "D:\\Import\\TMM"
myRemoteFileFolder = "/Triggered_Automations/PaperForm/DailySubscriptions"
myFileName = "v2CustomerSearchCDH"
myFileExtension = ".csv"
myLocalFilePath = "\\\\edw-db-dev\\Import\\TMM" + "\\" + myFileName + myFileExtension
myRemoteFilePath = "Triggered_Automations/PaperForm/DailySubscriptions" + "/" + myFileName + myFileExtension
keydatavalue = "AAAAB3NzaC1yc2EAAAABEQAAAQEAv5QrAMTfr6Eg/8U/wRDvTILxQKqRPS18mMcw1rAT6a/OpgUkXJb8nypwO8lA9+4aptESCQ2auez3n1qP10oLWwUfNYQETv/bs8iCsblmqonTmSMBN+qkbiQE2aeYuFDfYokaE+UYz4r4QhOLFgjsE+CwGXwc+honc6X5aXvOeY+Sj29xQBJU3wvFpNQZXy4VFVhhuTJlVoeaaYfpDjwyOtcOpAP5YBPG0p19KHcMt7+VCbUbYTjBO6FTocdfM9SZVCDZPf8jD3dxqmLlAk/p5bWtPoiDFxeZgvebpEk5gjIIVOUBc8VNDzpzDOjpuav4/jtFI4LJm4fmKVIAmyPjDQ=="
myFileList = [] ## Start as the empty list

if (keydatavalue != ""):
    keydata = keydatavalue.encode('utf-8') 
    key = paramiko.RSAKey(data=decodebytes(keydata))
    cnopts = pysftp.CnOpts()
    cnopts.hostkeys.add(myHostName, "ssh-rsa", key)
else:
   cnopts = pysftp.CnOpts()    
   cnopts.hostkeys = None
   
warnings.filterwarnings('default')
print(os.path.basename(__file__))
with pysftp.Connection(host=myHostName, username=myUserName, private_key = myPrivateKeyPath, cnopts=cnopts) as sftp:
#with pysftp.Connection(host=myHostName, username=myUserName, cnopts=cnopts) as sftp:
    print("Connection Succesfully Established ... ")
    
    #Get List of Files to be Uploaded from Local Working FOlder
    for entry in os.scandir(myLocalFileFolder):
        #print(os.path.basename(entry.path))
        #print(entry.path[0:entry.path.find(".")])
        #if (entry.path.startswith(myLocalFileFolder + "" + myFileName) and entry.path.endswith(".csv")) and entry.is_file():
        if ((entry.path.find(myFileName) != -1) and entry.path.endswith(myFileExtension)) and entry.is_file():
            # Use put method to upload a file
            
            sftp.put(entry.path, myRemoteFileFolder + "/" + os.path.basename(entry.path),preserve_mtime=True)
            sftp.chmod(myRemoteFileFolder + "/" + os.path.basename(entry.path), 777)
            ## Adding Elements to List
            myFileList.append(os.path.basename(entry.path))   
            print("File " + entry.path + "  Uploaded Succesfully to Remote Server... ")
     
    # Use change working directory to remote
    sftp.cwd(myRemoteFileFolder)

    # Obtain structure of the remote directory '/var/www/vhosts'
    directory_structure = sftp.listdir_attr()
    
    # Print data
    for attr in directory_structure:
        print (attr)
        if (sftp.exists(attr.filename) == True and attr.filename in myFileList):
            print("File " + attr.filename + " Existence Validated Successfully on Remote Server... ")

    for entry in sftp.listdir():
        print(entry)
        print(entry.find(myFileName))
        print(entry.endswith(myFileExtension))
        print(stat.S_ISREG(sftp.stat(os.path.join('/Triggered_Automations/PaperForm/DailySubscriptions', entry)).st_mode))
        #if ((entry.path.find(myFileName) != -1) and entry.path.endswith(myFileExtension)) and stat.S_ISREG(sftp.stat(os.path.join(remotePath, file)).st_mode):
