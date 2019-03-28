from __future__ import print_function
import os
import flask
from flask import flash, redirect, url_for
import httplib2
from apiclient import discovery
from apiclient.http import MediaIoBaseDownload, MediaFileUpload
from oauth2client import client
from oauth2client import tools
from oauth2client.file import Storage
from . import routes
from routes import *


@routes.route('/drive')
def drive():
	credentials = get_credentials()
	if credentials == False:
		return redirect(url_for('routes.oauth2callback'))
	elif credentials.access_token_expired:
		return redirect(url_for('routes.oauth2callback'))
	else:
		print('now calling fetch')
		all_files = fetch("'root' in parents and mimeType = 'application/vnd.google-apps.folder'", sort='modifiedTime desc')
		s = ""
		for file in all_files:
			s += "%s, %s<br>" % (file['name'],file['id'])
		return s

@routes.route('/oauth2callback')
def oauth2callback():
	flow = client.flow_from_clientsecrets('client_id.json',
			scope='https://www.googleapis.com/auth/drive',
			redirect_uri=url_for('routes.oauth2callback', _external=True)) # access drive api using developer credentials
	flow.params['include_granted_scopes'] = 'true'
	if 'code' not in flask.request.args:
		auth_uri = flow.step1_get_authorize_url()
		return redirect(auth_uri)
	else:
		auth_code = flask.request.args.get('code')
		credentials = flow.step2_exchange(auth_code)
		open('credentials.json','w').write(credentials.to_json()) # write access token to credentials.json locally
		return redirect(flask.url_for('routes.drive'))

def get_credentials():
	credential_path = 'credentials.json'

	store = Storage(credential_path)
	credentials = store.get()
	if not credentials or credentials.invalid:
		print("Credentials not found.")
		return False
	else:
		print("Credentials fetched successfully.")
		return credentials

def fetch(query, sort='modifiedTime desc'):
	credentials = get_credentials()
	http = credentials.authorize(httplib2.Http())
	service = discovery.build('drive', 'v3', http=http)
	results = service.files().list(
		q=query,orderBy=sort,pageSize=10,fields="nextPageToken, files(id, name)").execute()
	items = results.get('files', [])
	return items

def download_file(file_id, output_file):
	credentials = get_credentials()
	http = credentials.authorize(httplib2.Http())
	service = discovery.build('drive', 'v3', http=http)
	#file_id = '0BwwA4oUTeiV1UVNwOHItT0xfa2M'
	request = service.files().export_media(fileId=file_id,mimeType='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet')
	#request = service.files().get_media(fileId=file_id)

	fh = open(output_file,'wb') #io.BytesIO()
	downloader = MediaIoBaseDownload(fh, request)
	done = False
	while done is False:
		status, done = downloader.next_chunk()
		#print ("Download %d%%." % int(status.progress() * 100))
	fh.close()
	#return fh

def update_file(file_id, local_file):
	credentials = get_credentials()
	http = credentials.authorize(httplib2.Http())
	service = discovery.build('drive', 'v3', http=http)
	# First retrieve the file from the API.
	file = service.files().get(fileId=file_id).execute()
	# File's new content.
	media_body = MediaFileUpload(local_file, resumable=True)
	# Send the request to the API.
	updated_file = service.files().update(
		fileId=file_id,
		#body=file,
		#newRevision=True,
		media_body=media_body).execute()
