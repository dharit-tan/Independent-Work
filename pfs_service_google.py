import os
import subprocess
from splinter import Browser
import time
import string
import random

# required by google drive
import httplib2
import pprint

from apiclient.discovery import build
from apiclient.http import MediaFileUpload
from oauth2client.client import OAuth2WebServerFlow

# dropbox_authorize_url = 'https://www.dropbox.com/1/oauth2/authorize'
GOOGLEDRIVE_DIR = os.environ['HOME'] + "/parrot_fs_googledrive_dir"

# Copy your credentials from the console
CLIENT_ID = '944870957971-iieour9tqie3pg55ki7s0vg8sjqdou1f.apps.googleusercontent.com'
CLIENT_SECRET = 'QlFi0KPe8bs4kwrOJIWy_oWm'

# Check https://developers.google.com/drive/scopes for all available scopes
OAUTH_SCOPE = 'https://www.googleapis.com/auth/drive'

# Redirect URI for installed apps
REDIRECT_URI = 'urn:ietf:wg:oauth:2.0:oob'

""
Modes:
- 0: Upload after every write()
- 1: Upload only during exit()
- 2: Upload only during close()
"""

MODE_WRITE = 0
MODE_EXIT = 1
MODE_CLOSE = 2

ANALYSIS = True

class pfs_file_googledrive:
	def __init__(self, filename, local_name, flags, fp, path):
		self.filename = filename         # file name
		self.local_name = local_name     # file name on local system
		self.flags = flags               # file permission flags
		self.fp = fp                     # file pointer
		self.path = path                 # path to file on dropbox

class pfs_service_googledrive:

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
		# Path to the file to upload
		FILENAME = 'asdf'

		# Run through the OAuth flow and retrieve credentials
		flow = OAuth2WebServerFlow(CLIENT_ID, CLIENT_SECRET, OAUTH_SCOPE, REDIRECT_URI)
		authorize_url = flow.step1_get_authorize_url()
		print 'Go to the following link in your browser: ' + authorize_url
		code = raw_input('Enter verification code: ').strip()
		credentials = flow.step2_exchange(code)

		b = Browser('chrome')
		b.visit(authorize_url)

		if not b.find_by_name('allow_access'):
			b.find_by_name('login_email')[1].fill('dtantivi@princeton.edu')
			b.find_by_name('login_password')[1].fill('dharit1250')
			b.find_by_css('.login-button')[0].click()
		time.sleep(2)
		b.find_by_name('allow_access').first.click()
		code = b.find_by_id('auth-code').first.text
		access_token, user_id = flow.finish(code)


		# Create an httplib2.Http object and authorize it with our credentials
		http = httplib2.Http()
		http = credentials.authorize(http)

		drive_service = build('drive', 'v2', http=http)

		# Insert a file
		media_body = MediaFileUpload(FILENAME, mimetype='text/plain', resumable=True)
		body = {
		  'title': 'My document',
		  'description': 'A test document',
		  'mimeType': 'text/plain'
		}

		file = drive_service.files().insert(body=body, media_body=media_body).execute()
		pprint.pprint(file)

	def __upload(self, path):
		old_current = os.getcwd()
		os.chdir(GOOGLEDRIVE_DIR)
		f = self.fd_table[path]
		f.fp.seek(0)
		if f.flags == "r": # don't re-upload if file was not supposed to be written to
			# print "file is read only; did not upload"
			pass
		else:
			response = self.client.put_file(f.path, f.fp, overwrite=True)
			# print "file uploaded successfully"
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
		if self.mode == MODE_EXIT:
			self.to_upload = {}

	def open(self, filepath, flags="r"):
		path = self.__check_path(filepath)
		filename = filepath.split('/')[-1]
		# print "filename: " + filename

		# print "current_dir: " + self.current_dir
		# print "trying to download: " + path

		# chdir to private temp dropbox directory
		old_current = os.getcwd()
		os.chdir(GOOGLEDRIVE_DIR)
		
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
		os.chdir(GOOGLEDRIVE_DIR)
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
		os.chdir(GOOGLEDRIVE_DIR)
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

	def exit1(self):
		keys = self.to_upload.keys()
		old_current = os.getcwd()
		os.chdir(GOOGLEDRIVE_DIR)
		for local_name in keys:
			f = open(local_name, "r")
			response = self.client.put_file(self.to_upload[local_name], f, overwrite=True)
		os.chdir(old_current)
		self.to_upload = {}

	def exit(self):
		if self.mode == MODE_WRITE or self.mode == MODE_CLOSE:
			self.exit02()
		if self.mode == MODE_EXIT:
			self.exit1()
			
		if not ANALYSIS:
			self.client.disable_access_token()
