#!/usr/bin/env python

import requests

dropbox_authorize_url = 'https://www.dropbox.com/1/oauth2/authorize'
dropbox_login_url = 'https://www.dropbox.com/login'

# Include the Dropbox SDK libraries
from dropbox import client, rest, session

# Get your app key and secret from the Dropbox developer website
APP_KEY = 'vu3xexqedjpw523'
APP_SECRET = '8fyq6q9qmb0wn6l'

# ACCESS_TYPE should be 'dropbox' or 'app_folder' as configured for your app
ACCESS_TYPE = 'app_folder'

sess = session.DropboxSession(APP_KEY, APP_SECRET, ACCESS_TYPE)
request_token = sess.obtain_request_token()
url = sess.build_authorize_url(request_token)

# r = requests.get(url)

# print r.text
# print r.url

# payload = {'login_email':'dtantivi@princeton.edu','login_password':'dharit1250','cont':'https://www.dropbox.com/1/oauth2/authorize?response_type=code&client_id=vu3xexqedjpw523'}
# payload = {'t':'t:_JNQtDOKSqcTa5PGYzaBc05W','login_email':'dtantivi@princeton.edu','login_password':'dharit1250','cont':'https://www.dropbox.com/1/oauth2/authorize?response_type=code&client_id=vu3xexqedjpw523','signup_tag':'oauth','signup_data':'534819','display':'desktop','login_submit':'1','remember_me':'off','login_submit_dummy':'Sign in'}
# payload = {'login_email':'dtantivi@princeton.edu','login_password':'dharit1250','remember_me':'off'}
# r = requests.post(r.url, data=payload)

# print r.text

# print r.text
# print r.data

# Make the user sign in and authorize this token
print "url:", url
print "Please visit this website and press the 'Allow' button, then hit 'Enter' here."
raw_input()

# This will fail if the user didn't visit the above URL
access_token = sess.obtain_access_token(request_token)

# Print the token for future reference
print access_token



