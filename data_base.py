import requests
from dotenv import load_dotenv
import os

load_dotenv()
air_base = os.getenv('air_base')
air_table = os.getenv('air_table')
airtable_token = os.getenv('air_table_token')
notion_api = os.getenv('api')
notion_base_id = os.getenv('notion_base_id')
discord_token = os.getenv('discord_token')



def write_user_data_airtable(token, base_id,table_id,new_data):
    headers = {
        'Authorization': f'Bearer {token}',
        'Content-Type': 'application/json'
    }
    url = f'https://api.airtable.com/v0/{base_id}/{table_id}'
    response = requests.get(url, headers=headers)
    data = response.json()
    row_id = None
    for record in data['records']:
        username = record['fields'].get('username', None)
        if username == new_data['username']:
            row_id = record['id']

    if row_id:
        update_record_data = {
            'records': [
                {'id': row_id,
                    "fields": {
                        'State': new_data['state'],
                        "Date": new_data['date'],
                        "username": new_data['username'],
                        "Post Today": new_data['post today'],
                        "Max Posts": new_data['max post'],
                        'Status': new_data['status']
                    }
                }
            ]
        }
        response = requests.patch(url, headers=headers, json=update_record_data)
    else:
        new_record_data = {
            "records": [
                {
                    "fields": {
                        'State': new_data['state'],
                        "Date": new_data['date'],
                        "username": new_data['username'],
                        "Post Today": new_data['post today'],
                        "Max Posts": new_data['max post'],
                        'Status': new_data['status']
                    }
                }
            ]
        }
        response = requests.post(url, headers=headers, json=new_record_data)

    if response.status_code == 200:
        print('Success add record')
    else:
        print('Error, status code ', response.status_code, "Content: ",response.content)




def write_user_data(NOTION_API_KEY, NOTION_API_VERSION, DATABASE_ID, new_data):
    headers = {
        'Authorization': f'Bearer {NOTION_API_KEY}',
        'Content-Type': 'application/json',
        'Notion-Version': NOTION_API_VERSION
    }

    # The URL to update a specific row in the Notion database
    NOTION_UPDATE_URL = f'https://api.notion.com/v1/pages/{new_data["row id"]}'

    # Create a dictionary with the data you want to update
    update_data = {
        'properties': {
            'post today': {'number': new_data['post today']},
            'max post': {'number': new_data['max post']},
            'status': {'status': {'name': new_data['status']}},
            'date': {'date': {'start': new_data['date']}}
        }
    }

    # Make a PATCH request to update the row
    response = requests.patch(NOTION_UPDATE_URL, headers=headers, json=update_data)

    if response.status_code == 200:
        print(f"User {DATABASE_ID} updated successfully.")
    else:
        print(f'Error updating user {DATABASE_ID}: {response.status_code} - {response.text}')


def get_users_data(NOTION_API_KEY, NOTION_API_VERSION, DATABASE_ID):
    headers = {
        'Authorization': f'Bearer {NOTION_API_KEY}',
        'Notion-Version': NOTION_API_VERSION
    }

    response = requests.post(f'https://api.notion.com/v1/databases/{DATABASE_ID}/query', headers=headers)

    if response.status_code == 200:
        data = response.json()
        rows = data['results']
        all_rows = []
        if rows:
            for row in rows:
                reddit_accs = {}
                reddit_accs['username'] = row['properties']['username:password:email:password']['title'][0]['plain_text'].split(':')[0]
                reddit_accs['state'] = row['properties']['state in shortform']['rich_text'][0]['plain_text']
                reddit_accs['status'] = row['properties']['status']['status']['name']
                all_rows.append(reddit_accs)
        return all_rows


        # if rows:
        #     for row in rows:
        #         reddit_accs = {}
        #         reddit_accs['state'] = row['properties']['state']['title'][0]['plain_text']
        #         try:
        #             reddit_accs['date'] = row['properties']['date']['date']['start']
        #         except:
        #             reddit_accs['date'] = None
        #         reddit_accs['username'] = row['properties']['username']['rich_text'][0]['plain_text']
        #         reddit_accs['post today'] = row['properties']['post today']['number']
        #         reddit_accs['max post'] = row['properties']['max post']['number']
        #         reddit_accs['status'] = row['properties']['status']['status']['name']
        #         reddit_accs['row id'] = row['id']
        #
        #         all_rows.append(reddit_accs)
        #     return all_rows

    else:
        print('Error: ', response.status_code, ' text:', response.text)
