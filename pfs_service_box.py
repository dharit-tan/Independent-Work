import os
import box
from splinter import Browser
import time
import string
import random

BOX_DIR = os.environ['HOME'] + "/pfs_box_dir"

"""
Modes:
- 0: Upload after every write()
- 1: Upload only during close()
- 2: Upload only during exit()
"""

MODE_WRITE = 0
MODE_CLOSE = 1
MODE_EXIT = 2

class pfs_file_box:
	def __init__(self, filename, local_name, flags, fp, path):
		self.filename = filename         # file name
		self.local_name = local_name     # file name on local system
		self.flags = flags               # file permission flags
		self.fp = fp                     # file pointer
		self.path = path                 # path to file on dropbox

class pfs_service_box:

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
		b = Browser('chrome')
		b.visit("http://box-token-generator.herokuapp.com/")

		if b.find_link_by_href('set_client_credentials'):
			b.visit('http://box-token-generator.herokuapp.com/set_client_credentials')
			time.sleep(2)
		
			b.find_by_id('login').first.fill('dtantivi@princeton.edu')
			b.find_by_id('password').first.fill('dharit1250')
			b.find_by_name('login_submit').first.click()

			b.find_by_id('consent_accept_button').first.click()
	
		code = b.find_by_tag('h4')[1].text
		self.client = box.BoxClient(code)
		b.quit()

	def __upload(self, path):
		f = self.fd_table[path]
		if f.flags == "r": # don't re-upload if file was not supposed to be written to
			return

		old_current = os.getcwd()
		os.chdir(BOX_DIR)

		oldpos = f.fp.tell()
		f.fp.seek(0)
		response = self.client.upload_file(f.filename+"".join(random.choice(string.ascii_letters) for i in range(10)), f.fp)
		
		f.fp.seek(oldpos)
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

		# chdir to private box directory
		old_current = os.getcwd()
		os.chdir(BOX_DIR)

		local_copy = open(filename, flags) # re-open with desired flags
		if path in self.fd_table:
			self.close(path)
		self.fd_table[path] = pfs_file_box(filename, filename, flags, local_copy, path)

		os.chdir(old_current)
		return local_copy

	# no upload on close()
	def close0(self, filename):
		path = self.__check_path(filename)
		if path not in self.fd_table:
			raise IOError("Not an open file: " + path)

		self.fd_table[path].fp.close()
		del self.fd_table[path]

	# upload on close()
	def close1(self, filename):
		path = self.__check_path(filename)
		if path not in self.fd_table:
			raise IOError("Not an open file: " + path)

		# upload file first
		self.__upload(path)

		self.fd_table[path].fp.close()

		# old_current = os.getcwd()
		# os.chdir(BOX_DIR)
		# os.chdir(old_current)

		del self.fd_table[path]

	# no upload on close()
	def close2(self, filename):
		path = self.__check_path(filename)
		if path not in self.fd_table:
			raise IOError("Not an open file: " + path)

		# add file to list of files to upload later
		pfile = self.fd_table[path]
		pfile.fp.close()
		self.to_upload[pfile.local_name] = pfile.path

		del self.fd_table[path]

	def close(self, filename):
		if self.mode == MODE_WRITE:
			self.close0(filename)
		elif self.mode == MODE_CLOSE:
			self.close1(filename)
		elif self.mode == MODE_EXIT:
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
			except box.client.ItemDoesNotExist:
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
			self.client.delete_file(filename)
		except box.client.ItemDoesNotExist:
			raise IOError("[Errno 2] No such file or directory: " + filename)
			
	def getcwd(self):
		return self.current_dir

	def exit01(self):
		keys = self.fd_table.keys()
		for path in keys:
			self.close(path)

	def exit2(self):
		keys = self.to_upload.keys()
		old_current = os.getcwd()
		os.chdir(BOX_DIR)
		for local_name in keys:
			f = open(local_name, "r")
			self.client.upload_file(self.to_upload[local_name]+"".join(random.choice(string.ascii_letters) for i in range(10)), f)
			f.close()
		os.chdir(old_current)
		self.to_upload = {}

	def exit(self):
		if self.mode == MODE_WRITE or self.mode == MODE_CLOSE:
			self.exit01()
		if self.mode == MODE_EXIT:
			self.exit2()
