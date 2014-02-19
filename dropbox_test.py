#!/usr/bin/env python

import requests
import parrot_fs_dropbox
import dropbox

dropbox_authorize_url = 'https://www.dropbox.com/1/oauth2/authorize'
dropbox_login_url = 'https://www.dropbox.com/login'

# Include the Dropbox SDK libraries
# from dropbox import client, rest, session

# Get your app key and secret from the Dropbox developer website
APP_KEY = 'vu3xexqedjpw523'
APP_SECRET = '8fyq6q9qmb0wn6l'

# ACCESS_TYPE should be 'dropbox' or 'app_folder' as configured for your app
ACCESS_TYPE = 'app_folder'
flow = dropbox.client.DropboxOAuth2FlowNoRedirect(APP_KEY, APP_SECRET)

authorize_url = flow.start()
print '1. Go to: ' + authorize_url
print '2. Click "Allow" (you might have to log in first)'
print '3. Copy the authorization code.'
code = raw_input("Enter the authorization code here: ").strip()


# This will fail if the user didn't visit the above URL
# access_token = sess.obtain_access_token(request_token)
access_token, user_id = flow.finish(code)
# Print the token for future reference
print access_token

client = dropbox.client.DropboxClient(access_token)
print 'linked account: ', client.account_info()



