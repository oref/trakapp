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
import pickle
import os.path
from googleapiclient.discovery import build
from google_auth_oauthlib.flow import InstalledAppFlow
from google.auth.transport.requests import Request
from . import routes
from routes import *

# If modifying these scopes, delete the file token.pickle.
SCOPES = ['https://www.googleapis.com/auth/drive.metadata.readonly']

def main():
    """Shows basic usage of the Drive v3 API.
    Prints the names and ids of the first 10 files the user has access to.
    """
    creds = None
    # The file token.pickle stores the user's access and refresh tokens, and is
    # created automatically when the authorization flow completes for the first
    # time.
    if os.path.exists('token.pickle'):
        with open('token.pickle', 'rb') as token:
            creds = pickle.load(token)
    # If there are no (valid) credentials available, let the user log in.
    if not creds or not creds.valid:
        if creds and creds.expired and creds.refresh_token:
            creds.refresh(Request())
        else:
            flow = InstalledAppFlow.from_client_secrets_file(
                'credentials.json', SCOPES)
            creds = flow.run_local_server()
        # Save the credentials for the next run
        with open('token.pickle', 'wb') as token:
            pickle.dump(creds, token)

    service = build('drive', 'v3', credentials=creds)

    # Call the Drive v3 API
    results = service.files().list(
        pageSize=10, fields="nextPageToken, files(id, name)").execute()
    items = results.get('files', [])

    if not items:
        print('No files found.')
    else:
        print('Files:')
        for item in items:
            print(u'{0} ({1})'.format(item['name'], item['id']))

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
		return render_template('drive.html', s=s)

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

@routes.route('/upload')
def submit(file_id, local_file, methods=['POST']):
    credentials = get_credentials()
    http = credentials.authorize(httplib2.Http())
    service = discovery.build('drive', 'v3', http=http)
    file_metadata = {'name':'test'}
    media = MediaFileUpload('test',
                            mimetype='application/pdf')
    file = service.files().create(body=file_metadata,
                                  media_body=media,
                                  fields='id').execute()
    print("File ID: {0}".format(file.get('id')))
