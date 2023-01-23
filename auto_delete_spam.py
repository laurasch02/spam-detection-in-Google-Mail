import os
from googleapiclient.discovery import build
from httplib2 import Http
from oauth2client import file, client, tools
from apiclient import errors
import logging


### log what is happening in the inbox on a daily basis ###
logger = logging.getLogger(__name__)
logger.setLevel(logging.DEBUG)
formatter = logging.Formatter('%(asctime)s:%(name)s:%(message)s')
file_handler = logging.FileHandler('auto_delete.log')
file_handler.setFormatter(formatter)
logger.addHandler(file_handler)

### get read and write privileges to delete emails ###

SCOPES = 'https://mail.google.com/'

### create custom exception ###

class AutoDeleteException(Exception):
    pass

### service to acces the mailbox ###

SERVICE = None

def init(user_id='me', token_file='token.json', credentials_file='credentials.json'):
    global SERVICE

    if not os.path.exists(credentials_file):
        raise AutoDeleteException('Can\'t find credentials file at %s. You can download this file from https://developers.google.com/gmail/api/quickstart/python and clicking "Enable the Gmail API"' % (os.path.abspath(credentials_file)))

    store = file.Storage(token_file)
    creds = store.get()
    if not creds or creds.invalid:
        flow = client.flow_from_clientsecrets(credentials_file, SCOPES)
        creds = tools.run_flow(flow, store)
    SERVICE = build('gmail', 'v1', http=creds.authorize(Http()))

### search function to match query for spam mails ###

def search(query, user_id='me'):
    if SERVICE is None:
        init()
    
    try:
        response = SERVICE.users().messages().list(userId=user_id,
                                                   q=query).execute()
        messages = []
        if 'messages' in response:
            messages.extend(response['messages'])

        while 'nextPageToken' in response:
            page_token = response['nextPageToken']
            response = SERVICE.users().messages().list(userId=user_id, q=query,
                                                       pageToken=page_token).execute()
            messages.extend(response['messages'])

        return messages

    except errors.HttpError as e:
        logger.exception(f'An error occurred:{e}')

### delete the messages that fit the query ###

def delete_messages(query, user_id='me'):
    messages = search(query)

    if messages:
        for message in messages:
            SERVICE.users().messages().delete(userId=user_id, id=message['id']).execute()
            logger.info(f'Message with id: {message["id"]} deleted successfully.')
    else:
        logger.info("There was no message matching the query.")

if __name__ == "__main__":
    init()
    logger.info('Deleting Messages from info@i.drop.com')
    delete_messages('from: some@email.com\
        subject: "some subject"\
        older_than:1d')