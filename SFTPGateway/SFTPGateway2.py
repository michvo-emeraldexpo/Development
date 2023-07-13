import pysftp
import paramiko
import sys
import warnings


warnings.filterwarnings("ignore")

remote_path = '/' + sys.argv[1]    #hard-coded
localpath = sys.argv[1]


host = "mchfjxgbj-l4-d163d99tscz72z4.ftp.marketingcloudops.com"                    #hard-coded
username = "514006106"                #hard-coded
cnopts = pysftp.CnOpts()
cnopts = pysftp.CnOpts(knownhosts='known_hosts')
with pysftp.Connection(host, username=username, private_key="mcftp_public_client_key", cnopts=cnopts) as sftp:
    sftp.put(localpath, remote_path)
    print('Upload done.')
    sftp.get('/import/MarketingCloudDe1_20201114.csv','./testmarketing.csv')
    print('download done.')

