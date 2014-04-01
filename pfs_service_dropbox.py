import os
import subprocess
import dropbox
from splinter import Browser
import time
import string
import random

# dropbox_authorize_url = 'https://www.dropbox.com/1/oauth2/authorize'
DROPBOX_DIR = os.environ['HOME'] + "/parrot_fs_dropbox_dir"

# Get your app key and secret from the Dropbox developer website
APP_KEY = 'vu3xexqedjpw523'
APP_SECRET = '8fyq6q9qmb0wn6l'

# ACCESS_TYPE should be 'dropbox' or 'app_folder' as configured for your app
ACCESS_TYPE = 'app_folder'

"""
Modes:
- 0: Upload after every write()
- 1: Upload only during exit()
- 2: Upload only during close()
"""

MODE_WRITE = 0
MODE_EXIT = 1
MODE_CLOSE = 2

class pfs_file_dropbox:
	def __init__(self, filename, local_name, flags, fp, path):
		self.filename = filename         # file name
		self.local_name = local_name     # file name on local system
		self.flags = flags               # file permission flags
		self.fp = fp                     # file pointer
		self.path = path                 # path to file on dropbox

class pfs_service_dropbox:

	# PRIVATE METHODS ----------------------------------------------------------#

	def __update_current_dir(self):
		self.current_dir = ""
		for i in self.dir_path:
			self.current_dir += i
		if self.current_dir[-1] != "/":
			self.current_dir += "/"

	def __reset_dir_path(self):
		self.dir_path = ["/"]
		self.__update_current_dir()

	def __authorize(self):
		flow = dropbox.client.DropboxOAuth2FlowNoRedirect(APP_KEY, APP_SECRET)

		authorize_url = flow.start()
		b = Browser('chrome')
		b.visit(authorize_url)
		# time.sleep(1)
		if not b.find_by_name('allow_access'):
			b.find_by_name('login_email')[1].fill('dtantivi@princeton.edu')
			b.find_by_name('login_password')[1].fill('dharit1250')
			b.find_by_css('.login-button')[0].click()
		time.sleep(1)
		b.find_by_name('allow_access').first.click()
		code = b.find_by_id('auth-code').first.text
		access_token, user_id = flow.finish(code)

		# Print the token for future reference
		# print access_token

		self.client = dropbox.client.DropboxClient(access_token)
		b.quit()
		# print 'linked account: ' + str(self.client.account_info())

	def __upload(self, path):
		old_current = os.getcwd()
		os.chdir(DROPBOX_DIR)
		f = self.fd_table[path]
		f.fp.seek(0)
		if f.flags == "r": # don't re-upload if file was not supposed to be written to
			print "file is read only; did not upload"
			pass
		else:
			response = self.client.put_file(f.path, f.fp, overwrite=True)
			print "file uploaded successfully"
		os.chdir(old_current)

	def __check_path(self, filename):
		if filename[0] == '/':
			return filename
		else:
			return self.current_dir + filename

	# --------------------------------------------------------------------------#
		
	def __init__(self, mode=MODE_CLOSE):
		self.__authorize()

		# current dir on dropbox
		self.__reset_dir_path()

		# file descriptor table
		self.fd_table = {}

		self.mode = mode
		if self.mode == 1:
			self.to_upload = {}

	def open(self, filepath, flags="r"):
		path = self.__check_path(filepath)
		filename = filepath.split('/')[-1]
		print "filename: " + filename

		print "current_dir: " + self.current_dir
		print "trying to download: " + path

		# chdir to private temp dropbox directory
		old_current = os.getcwd()
		os.chdir(DROPBOX_DIR)
		
		local_name = ''.join(random.choice(string.ascii_letters) for i in range(10))

		if "r" in flags:   # error if file DNE
			try:
				downloaded_copy = self.client.get_file(path)
			except dropbox.rest.ErrorResponse:
				raise IOError("[Errno 2] No such file or directory: " + path)

			# create file and write contents first
			local_copy = open(local_name, "w")
			for i in downloaded_copy.readlines():
				local_copy.write(i)
			local_copy.close()
			local_copy = open(local_name, flags) # re-open with desired flags

		elif "w" in flags: # don't care about file on dropbox, but must overwrite when uploading
			local_copy = open(local_name, flags)

		elif "a" in flags:
			try:
				downloaded_copy = self.client.get_file(path)
			except dropbox.rest.ErrorResponse:
				pass

			# create file and write contents first
			local_copy = open(local_name, "w")
			for i in downloaded_copy.readlines():
				local_copy.write(i)
			local_copy.close()

			local_copy = open(filename, flags) # re-open with desired flags and seek to end
			local_copy.seek(0,2)

		if path in self.fd_table:
			self.close(path)
		self.fd_table[path] = pfs_file_dropbox(filename, local_name, flags, local_copy, path)

		os.chdir(old_current)
		return local_copy

	# no upload on close()
	def close0(self, filename):
		path = self.__check_path(filename)
		if path not in self.fd_table:
			raise IOError("Not an open file: " + path)

		self.fd_table[path].fp.close()

		old_current = os.getcwd()
		os.chdir(DROPBOX_DIR)
		os.remove(self.fd_table[path].local_name)
		os.chdir(old_current)

		del self.fd_table[path]

	# no upload on close()
	def close1(self, filename):
		path = self.__check_path(filename)
		if path not in self.fd_table:
			raise IOError("Not an open file: " + path)

		# add file to list of files to upload later
		pfile = self.fd_table[path]
		pfile.fp.close()
		self.to_upload[pfile.local_name] = pfile.path

		del self.fd_table[path]

	# upload on close()
	def close2(self, filename):
		path = self.__check_path(filename)
		if path not in self.fd_table:
			raise IOError("Not an open file: " + path)

		# upload file first
		self.__upload(path)

		self.fd_table[path].fp.close()

		old_current = os.getcwd()
		os.chdir(DROPBOX_DIR)
		os.remove(self.fd_table[path].local_name)
		os.chdir(old_current)

		del self.fd_table[path]

	def close(self, filename):
		if self.mode == MODE_WRITE:
			self.close0(filename)
		elif self.mode == MODE_EXIT:
			self.close1(filename)
		elif self.mode == MODE_CLOSE:
			self.close2(filename)

	def chdir(self, dirname=None):
		if dirname == "..":
			if self.current_dir == "/":
				pass
			else:
				self.dir_path.pop()
				self.__update_current_dir()
		elif dirname == ".":
			pass
		elif not dirname or dirname == "/":
			self.__reset_dir_path()
			self.__update_current_dir()
		else:
			if dirname[0] == "/" or not dirname:
				path = dirname
			else:
				path = self.current_dir + dirname
			try:
				metadata = self.client.metadata(path)
			except dropbox.rest.ErrorResponse:
				raise IOError("[Errno 2] No such file or directory: " + path)

			if not metadata["is_dir"]:
				raise OSError("[Errno 20] Not a directory: " + path)
			else:
				self.__reset_dir_path()
				for i in path.split("/"):
					self.dir_path.append(i)
				self.__update_current_dir()

	def read(self, filename, size=-1):
		path = self.__check_path(filename)
		if path not in self.fd_table:
			raise IOError("Not an open file: " + path)

		if size == -1:
			return self.fd_table[path].fp.read()
		else:
			return self.fd_table[path].fp.read(size)

	def write(self, filename, string):
		if self.mode == MODE_WRITE:
			self.write0(filename, string)
		if self.mode == MODE_CLOSE or self.mode == MODE_EXIT:
			self.write12(filename, string)

	def write0(self, filename, string):
		path = self.__check_path(filename)
		if path not in self.fd_table:
			raise IOError("Not an open file: " + path)

		self.fd_table[path].fp.write(string)
		self.__upload(path)

	def write12(self, filename, string):
		path = self.__check_path(filename)
		if path not in self.fd_table:
			raise IOError("Not an open file: " + path)

		self.fd_table[path].fp.write(string)

	def seek(self, filename, offset, from_what=0):
		path = self.__check_path(filename)
		if path not in self.fd_table:
			raise IOError("Not an open file: " + path)
		self.fd_table[path].fp.seek(offset, from_what)

	def remove(self, filename):
		path = self.__check_path(filename)

		if path in self.fd_table:
			self.close(path)
		try:
			self.client.file_delete(path)
		except dropbox.rest.ErrorResponse:
			raise IOError("[Errno 2] No such file or directory: " + path)

	def mkdir(self, dirname):
		path = self.__check_path(dirname)
		self.client.file_create_folder(path)

	def rmdir(self, dirname):
		path = self.__check_path(dirname)
		try:
			self.client.file_delete(path)
		except dropbox.rest.ErrorResponse:
			raise IOError("[Errno 2] No such file or directory: " + path)
			
	def getcwd(self):
		return self.current_dir

	def exit02(self):
		keys = self.fd_table.keys()
		for path in keys:
			self.close(path)
		self.client.disable_access_token()

	def exit1(self):
		keys = self.to_upload.keys()
		old_current = os.getcwd()
		os.chdir(DROPBOX_DIR)
		for local_name in keys:
			f = open(local_name, "r")
			response = self.client.put_file(self.to_upload[local_name], f, overwrite=True)
		os.chdir(old_current)

	def exit(self):
		if self.mode == MODE_WRITE or self.mode == MODE_CLOSE:
			self.exit02()
		if self.mode == MODE_EXIT:
			self.exit1()
