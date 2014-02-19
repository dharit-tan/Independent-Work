import os

dropbox_authorize_url = 'https://www.dropbox.com/1/oauth2/authorize'
DROPBOX_DIR = "~/parrot_fs_dropbox_private/"

# Get your app key and secret from the Dropbox developer website
APP_KEY = 'vu3xexqedjpw523'
APP_SECRET = '8fyq6q9qmb0wn6l'

# ACCESS_TYPE should be 'dropbox' or 'app_folder' as configured for your app
ACCESS_TYPE = 'app_folder'

RD_ONLY = 0
WR_ONLY = 1
RD_WR = 2

fd_table = [0 for x in range(10)]

class pfs_file_dropbox:
	def __init__(self, name, f):
		self.name = name
		self.f = f

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
		print 'linked account: ' + client.account_info()

	def open(self, name, flags):
		filename = name.split('/')[-1]

		current = os.getcwd()
		os.chdir(DROPBOX_DIR)
		self.client.getfile(name)

		if flags & RD_ONLY:
			fo = open(name, "r")
		elif flags & WR_ONLY:
			fo = open(name, "w")
		elif flags & RD_WR:
			fo = open(name, "w+")

		os.chdir(current)


	def close(self, name):
		