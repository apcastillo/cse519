# Installing Required Packages
#pip install python-dotenv
#!pip install requests
#!pip install pandas

#import colab_env
import numpy as np
import pandas as pd
import os
import base64
#from dotenv import load_dotenv, find_dotenv
from requests import get, post
import json
import time

#loading
#_ = load_dotenv(find_dotenv()) # reading local .env file

#anne
client_id = 'dca1ba4c350249938ce4544158ae8458' #os.environ['CLIENT_ID']
client_secret = '1c27a8f068f44548bb36c61d6247098e'#os.environ['CLIENT_SECRET']

#privthi
#client_id = 'c392d42a11bf414182f69a9e40526bc6' #os.environ['CLIENT_ID']
#client_secret = 'fde1f03252d749319749f55473ee2247'#os.environ['CLIENT_SECRET']

print(client_id, client_secret)

def get_token():
  auth_string = client_id + ":" + client_secret
  auth_bytes = auth_string.encode("utf-8")
  auth_base64 = str(base64.b64encode(auth_bytes), "utf-8")
  url = "https://accounts.spotify.com/api/token"
  headers = {
      "Authorization": "Basic " + auth_base64,
      "Content-Type": "application/x-www-form-urlencoded"
  }
  data = {"grant_type": "client_credentials"}
  result = post(url, headers=headers, data=data)
  json_result = json.loads (result.content)
  token = json_result["access_token"]
  return token

def get_auth_header (token):
  return {"Authorization": "Bearer " + token}

token = get_token()
# print(token)

def get_artist_id(token, artist_name):
  url = "https://api.spotify.com/v1/search"
  headers = get_auth_header(token)
  query = f"?q={artist_name}&type=artist&limit=1"
  query_url = url + query
  result = get(query_url, headers=headers)
  json_result = json.loads(result.content)
  return json_result['artists']['items'][0]['id']


def get_artist_info(token, artist_id):
  query_url = "https://api.spotify.com/v1/artists/" + artist_id
  headers = get_auth_header(token)
  result = get(query_url, headers=headers)
  if result.status_code != 200:
    print(result.status_code)
  if result.status_code == 429:
    print(result.headers)
    raise ZeroDivisionError
    #print("waiting 31 seconds...")
    #time.sleep(31)
  json_result = json.loads(result.content)
  return json_result

def get_artist_Albums(token, artist_id):
  payload={ 'market':'US', "limit": 50, 'include_groups': ['album']}
  query_url = "https://api.spotify.com/v1/artists/" + artist_id + "/albums"
  headers = get_auth_header(token)
  result = get(query_url, headers=headers, params=payload)
  if result.status_code == 429:
    print(result.headers)
    raise ZeroDivisionError
  json_result = json.loads(result.content)
  return json_result

def get_several_artists(token, artist_ids):
  query_url = "https://api.spotify.com/v1/artists?ids=" + ','.join(artist_ids)
  headers = get_auth_header(token)
  result = get(query_url, headers=headers)
  if result.status_code != 200:
    print(result.status_code)
  if result.status_code == 429:
    print(result.headers)
    raise ZeroDivisionError
    #print("waiting 31 seconds...")
    #time.sleep(31)
  json_result = json.loads(result.content)
  return json_result



from pandas.core.frame import DataFrame
artists_columns = [ 'id',
                    #'external_urls',
                    #'href',
                    'followers',
                    'genres',
                    'popularity',
                    #'images',
                    'name',
                    'type',
                    #'uri',
                    'album_names',
                    'release_dates',
                    'total_tracks'
                  ]

raw_data = pd.read_csv('missingartists.csv')
artistdata = dict()

for index, row in raw_data.iterrows():
  print(row['artist'])
  current_artist = row['artist']
  try:
    artist_id = get_artist_id(token, current_artist)
    info = get_artist_info(token, artist_id)
    info['followers'] = info['followers']['total']
    del info["uri"]
    del info["images"]
    del info["href"]
    del info['external_urls']
    info2 = get_artist_Albums(token, artist_id)
    total_tracks = 0
    album_names = []
    release_dates = []
    for i in info2['items']:
      album_names.append(i['name'])
      release_dates.append(i['release_date'])
      total_tracks += i['total_tracks']

    info['album_names'] = album_names
    info['release_dates'] = release_dates
    info['total_tracks'] = total_tracks
    artistdata[artist_id] = info
  except:
    print('failed: ', current_artist)

print('save-file')
df2 = pd.DataFrame.from_dict(artistdata, orient='index', columns=artists_columns)
df2.reset_index(drop=True, inplace=True)
df2.to_csv('artist_data.csv',columns=artists_columns, index=False, header=False, mode='a')

artistdata.clear()