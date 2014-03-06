import os
import subprocess
import dropbox

dropbox_authorize_url = 'https://www.dropbox.com/1/oauth2/authorize'
DROPBOX_DIR = os.environ['HOME'] + "/parrot_fs_dropbox_dir"

# Get your app key and secret from the Dropbox developer website
APP_KEY = 'vu3xexqedjpw523'
APP_SECRET = '8fyq6q9qmb0wn6l'

# ACCESS_TYPE should be 'dropbox' or 'app_folder' as configured for your app
ACCESS_TYPE = 'app_folder'


class pfs_file_dropbox:
	def __init__(self, filename, fp, path):
		self.filename = filename    # file name
		self.fp = fp                # file pointer
		self.path = path            # directory that file was downloaded from

class pfs_service_dropbox:
	def __init__(self):

		# current dir on dropbox
		self.dir_path = ["/"]
		self.__update_current_dir()

		# file descriptor table
		self.fd_table = {}

		self.authorize()

	# PRIVATE METHODS ----------------------------------------------------------#
	def __update_current_dir(self):
		self.current_dir = ""
		for i in self.dir_path:
			self.current_dir += i

	def __update_os_pwd(self):
		subprocess.call(["export","PWD=/dropbox" + self.current_dir])

	def __reset_dir_path(self):
		self.dir_path = ["/"]

	# --------------------------------------------------------------------------#

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
		# print 'linked account: ' + str(self.client.account_info())

	def open(self, filename, flags):
		old_current = self.current_dir
		if filename[0] == '/':               # construct directory path list
			temp_dir_path = ['/']
		else:
			temp_dir_path = []
		for i in filename.split('/')[:-1]:
			temp_dir_path.append(i)

		# chdir to the directory where the file is located
		for i in temp_dir_path:
			self.chdir(i)

		# get the file
		filename = filename.split('/')[-1]

		os.chdir(DROPBOX_DIR)
		try:
			downloaded_copy = self.client.get_file(filename)
		except dropbox.rest.ERROR_RESPONSE:
			raise IOError("[Errno 2] No such file or directory: " + filename)

		local_copy = open(filename, "r+")
		
		for i in downloaded_copy.readlines():
			local_copy.write(i)
		local_copy.seek(0)

		path = ""
		for i in temp_dir_path:
			path += i
		self.fd_table[filename] = pfs_file_dropbox(filename, local_copy, path)

		print os.getcwd()
		return local_copy

	def close(self, filename):
		f = self.fd_table[filename]
		response = self.client.put_file(f.path, f.fp)
		f.fp.close()
		del self.fd_table[filename]

	def chdir(self, dirname=None):
		if dirname == "..":
			if self.current_dir == "/":
				os.chdir(os.environ["HOME"])
			else:
				self.dir_path.pop()
				self.__update_current_dir()
				self.__update_os_pwd()
		elif dirname == ".":
			pass
		elif not dirname or dirname == "/":
			self.__reset_dir_path()
			self.__update_current_dir()
			self.__update_os_pwd()
		else:
			current_dir_metadata = self.client.metadata(self.current_dir)
			for i in current_dir_metadata["contents"]:
				if dirname == i["path"][1:]:
					if i["is_dir"]:
						self.dir_path.append(dirname)
						self.__update_current_dir()
						self.__update_os_pwd()
						return
					else:
						raise OSError("[Errno 20] Not a directory: " + dirname)
			raise OSError("[Errno 2] No such file or directory: " + dirname)

						

	# def mkdir(self):

	# def chdir(self, name):
	# 	current_dir = name

	# def getcwd(self):
	# 	return current_dir

