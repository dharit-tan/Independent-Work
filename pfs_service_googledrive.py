import os
import subprocess
from splinter import Browser
import time
import string
import random
import shutil

from pydrive.auth import *

# required by google drive
import httplib2
import pprint

from apiclient.discovery import build
from apiclient.http import MediaFileUpload
from oauth2client.client import OAuth2WebServerFlow

# dropbox_authorize_url = 'https://www.dropbox.com/1/oauth2/authorize'
GOOGLEDRIVE_DIR = os.environ['HOME'] + "/pfs_googledrive_dir"

# Copy your credentials from the console
CLIENT_ID = '944870957971-qlhr323prli2tjis2nbup5ncl7i1ck23.apps.googleusercontent.com'
CLIENT_SECRET = 'rn97GZkWVwTZC935EUIQ_qWv'

# Check https://developers.google.com/drive/scopes for all available scopes
OAUTH_SCOPE = 'https://www.googleapis.com/auth/drive'

# Redirect URI for installed apps
REDIRECT_URI = 'urn:ietf:wg:oauth:2.0:oob'

"""
Modes:
- 0: Upload after every write()
- 1: Upload only during exit()
- 2: Upload only during close()
"""

MODE_WRITE = 0
MODE_EXIT = 1
MODE_CLOSE = 2

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
		# Run through the OAuth flow and retrieve credentials
		flow = OAuth2WebServerFlow(CLIENT_ID, CLIENT_SECRET, OAUTH_SCOPE, REDIRECT_URI)
		authorize_url = flow.step1_get_authorize_url()

		b = Browser('chrome')
		b.visit(authorize_url)

		if not b.find_by_name('allow_access'):
			b.find_by_id('Email').first.fill('tortorareed@gmail.com')
			b.find_by_id('Passwd').first.fill('dharit1250')
			b.find_by_id('signIn').first.click()
		time.sleep(2)
		b.find_by_id('submit_approve_access').first.click()
		print b.find_by_id('code').first.value
		code = b.find_by_id('code').first.value
		credentials = flow.step2_exchange(code)
		b.quit()

		# Create an httplib2.Http object and authorize it with our credentials
		http = httplib2.Http()
		http = credentials.authorize(http)
		self.drive_service = build('drive', 'v2', http=http)

	def __upload(self, path):
		old_current = os.getcwd()
		os.chdir(GOOGLEDRIVE_DIR)
		f = self.fd_table[path]

		# Insert a file

		media_body = MediaFileUpload(f.filename, mimetype='text/plain', resumable=True)
		body = {
		  'title': f.filename,
		  'description': 'A test document',
		  'mimeType': 'text/plain'
		}
		file = self.drive_service.files().update(fileId=f.filename, body=body, media_body=media_body).execute()

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

		# chdir to private temp dropbox directory
		old_current = os.getcwd()
		os.chdir(GOOGLEDRIVE_DIR)
		
		if path in self.fd_table:
			self.close(path)
		local_copy = open(filename, flags) # re-open with desired flags
		self.fd_table[path] = pfs_file_googledrive(filename, filename, flags, local_copy, path)

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
			self.__upload(local_name)
		os.chdir(old_current)
		self.to_upload = {}

	def exit(self):
		if self.mode == MODE_WRITE or self.mode == MODE_CLOSE:
			self.exit02()
		if self.mode == MODE_EXIT:
			self.exit1()
