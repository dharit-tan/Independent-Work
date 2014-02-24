#!/usr/bin/env python

import requests
from parrot_fs_dropbox import pfs_service_dropbox, pfs_file_dropbox

service = pfs_service_dropbox()

f = service.open("chop.py", "wr")
for i in f.readlines():
	print i

service.close("chop.py")