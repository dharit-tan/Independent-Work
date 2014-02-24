import os
import dropbox

dropbox_authorize_url = 'https://www.dropbox.com/1/oauth2/authorize'
DROPBOX_DIR = os.environ['HOME'] + "/parrot_fs_dropbox_dir"

# Get your app key and secret from the Dropbox developer website
APP_KEY = 'vu3xexqedjpw523'
APP_SECRET = '8fyq6q9qmb0wn6l'

# ACCESS_TYPE should be 'dropbox' or 'app_folder' as configured for your app
ACCESS_TYPE = 'app_folder'

# Name of current working directory
current_dir = '/'
fd_table = {}

class pfs_file_dropbox:
	def __init__(self, name, fp, path):
		self.name = name    # file name
		self.fp = fp        # file pointer
		self.path = path    # directory that file was downloaded from

class pfs_service_dropbox:
	def __init__(self):
		self.authorize()

	def authorize(self):
		flow = dropbox.client.DropboxOAuth2FlowNoRedirect(APP_KEY, APP_SECRET)

		authorize_url = flow.start()
		print '1. Go to: ' + authorize_url
		print '2. Click "Allow" (you might have to log in first)'
		print '3. Copy the authorization code.'
		code = raw_input("Enter the authorization code here: ").strip()

		# This will fail if the user didn't visit the above URL
		access_token, user_id = flow.finish(code)

		# Print the token for future reference
		print access_token

		self.client = dropbox.client.DropboxClient(access_token)
		print 'linked account: ' + str(self.client.account_info())

	def open(self, name, flags):
		filename = name.split('/')[-1]
		path = name.split('/')[:-1]
		pathstring = ''
		for i in path:
			pathstring += i + '/'
		print pathstring

		current = os.getcwd()
		os.chdir(DROPBOX_DIR)
		self.client.get_file(name)

		print os.getcwd()
		print name
		print os.listdir(os.getcwd())
		
		fo = open(name, flags)

		for i in fo.readlines():
			print i

		print "---------------------------------------------------"
		print
		print

		fd_table[name] = pfs_file_dropbox(name, fo, pathstring)
		os.chdir(current)

		return fo

	def close(self, name):
		fc = fd_table[name]
		fc.fp.close()

	# def mkdir(self):

	# def chdir(self, name):
	# 	current_dir = name

	# def getcwd(self):
	# 	return current_dir

