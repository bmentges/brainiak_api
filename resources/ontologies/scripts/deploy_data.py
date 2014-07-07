import subprocess
import paramiko

DATABASE_HOST = "qa1.virtuoso.globoi.com"
DATABASE_USER = "dev"
DATABASE_PASSWORD = "dev"
DATABASE_PORT = "1111"
GRAPH = "http://semantica.globo.com/person/"

SSH_USER = 'virtuoso'
SSH_PWD = 'virtuoso'
LOCALFILE = 'data/person.ttl'
#REMOTEFILE = '/tmp/person.ttl'
REMOTEFILE = '/opt/semantica/virtuoso_ops/var/lib/virtuoso/db/person.ttl'


# Setup of connection with remote server
ssh = paramiko.SSHClient()
ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
ssh.connect(DATABASE_HOST, username=SSH_USER, password=SSH_PWD)
sftp = ssh.open_sftp()

# (1) Transfer TTL from local to remote server
sftp.put(LOCALFILE, REMOTEFILE)

# (2) Parse TTL and place its triples in the remote server
# For more info: http://docs.openlinksw.com/virtuoso/fn_ttlp_mt_local_file.html

isql = "isql -U %(user)s -P %(pwd)s -H %(host)s -S %(port)s" %\
		{"user": DATABASE_USER,
		 "pwd": DATABASE_PASSWORD,
		 "host": DATABASE_HOST,
		 "port": DATABASE_PORT}
isql_cmd = "DB.DBA.TTLP_MT_LOCAL_FILE('%s', '', '%s');" % (REMOTEFILE, GRAPH)
cmd = '%s < "%s"' % (isql, isql_cmd)

process = subprocess.Popen(cmd, shell=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
stdout_value, stderr_value = process.communicate()

# (3) Remove TTL from remote server
sftp.remove(REMOTEFILE)

# Close connections
sftp.close()
ssh.close()
