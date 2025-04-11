import requests
import json
import os
import base64
from Crypto.Cipher import AES
import time
import sys
from math import ceil

userId = ''
results = []
playList_ids = []
url = 'http://music.163.com/weapi/v1/resource/comments/R_SO_4_29393669/?csrf_token='

def aesEncrypt(text, secKey):
    pad = 16 - len(text) % 16
    text = text + pad * chr(pad)
    encryptor = AES.new(secKey.encode('utf-8'), AES.MODE_CBC, '0102030405060708'.encode('utf-8'))
    ciphertext = encryptor.encrypt(text.encode('utf-8'))
    ciphertext = base64.b64encode(ciphertext)
    return ciphertext.decode('utf-8')

def rsaEncrypt(text, pubKey, modulus):
    text = text[::-1]
    rs = int(text.encode('utf-8').hex(), 16)**int(pubKey, 16) % int(modulus, 16)
    return format(rs, 'x').zfill(256)

def createSecretKey(size):
    return (''.join(map(lambda xx: (hex(xx)[2:]), os.urandom(size))))[0:16]

def dataGenerator(limit, offset):
    text = {
        'limit': limit,
        'offset': offset
    }
    modulus = '00e0b509f6259df8642dbc35662901477df22677ec152b5ff68ace615bb7b725152b3ab17a876aea8a5aa76d2e417629ec4ee341f56135fccf695280104e0312ecbda92557c93870114af6c9d05c4f7f0c3685b7a46bee255932575cce10b424d813cfe4875d3e82047b97ddef52741d546b8e289dc6935b3ece0462db0a22b8e7'
    nonce = '0CoJUm6Qyw8W8jud'
    pubKey = '010001'
    text = json.dumps(text)
    secKey = createSecretKey(16)
    encText = aesEncrypt(aesEncrypt(text, nonce), secKey)
    encSecKey = rsaEncrypt(secKey, pubKey, modulus)
    data = {
        'params': encText,
        'encSecKey': encSecKey
    }
    return data

def pre_steps(userId):
    global playList_ids
    headers = {
        'Cookie': 'appver=1.5.0.75771;',
        'Referer': 'http://music.163.com/'
    }
    payload = {
        'params': 'params_value',
        'encSecKey': 'encSecKey_value'
    }

    # Fetch user's playlist
    playlist_url = f'http://music.163.com/api/user/playlist/?offset=0&limit=100&uid={userId}'
    response = requests.get(playlist_url, headers=headers)
    playlists = response.json()['playlist']
    # print(playlists[0]['name']) # playlist name

    for playlist in playlists:
        if playlist['userId'] == int(userId):
            playList_ids.append({'id': playlist['id'], 'name': playlist['name']})

def number_of_comments(url):
    headers = {
        'Cookie': 'appver=1.5.0.75771;',  # Required header to mimic the app's behavior
        'Referer': 'http://music.163.com/'  # Required referer header to make the request valid
    }
    data = dataGenerator(1, 0)  # Generate the required data payload for the request with limit 1 and offset 0
    req = requests.post(url, headers=headers, data=data)  # Make a POST request to the API
    print("总评论数: {}".format(req.json()['total']))  # Print the total number of comments from the response
    return req.json()['total']  # Return the total number of comments

def fetch_playlist_songs(playlist_id):
headers = {
    'Cookie': 'appver=1.5.0.75771;',
    'Referer': 'http://music.163.com/'
}
playlist_detail_url = f'http://music.163.com/api/playlist/detail?id={playlist_id}'
response = requests.get(playlist_detail_url, headers=headers)

if response.status_code != 200:
    print(f"Failed to fetch playlist details. Status code: {response.status_code}")
    return []

try:
    tracks = response.json()['result']['tracks']
except KeyError:
    print("Error: Could not find 'tracks' in the response. Full response:")
    print(response.json())
    return []

print(f"Playlist {playlist_id} has {len(tracks)} tracks:")
for track in tracks:
    print(f"Track ID: {track['id']}, Name: {track['name']}, Artist: {track['artists'][0]['name']}")
    
    return tracks

def search_start(limit, offset):
    for song in playList_ids:
        comments_url = f'http://music.163.com/weapi/v1/resource/comments/R_SO_4_{song["id"]}/?csrf_token='
        song_name = song['name']
        _offset = offset
        totalComments = number_of_comments(comments_url)
        while _offset < totalComments:
            time.sleep(2)
            sys.stdout.write(f"\r正在查询歌曲: {song_name}, 进度: {_offset}/{totalComments}, 当前共找到评论: {len(results)}条")
            sys.stdout.flush()
            headers = {
                'Cookie': 'appver=1.5.0.75771;',
                'Referer': 'http://music.163.com/'
            }
            data = dataGenerator(limit, _offset)
            try:
                req = requests.post(comments_url, headers=headers, data=data)
            except requests.exceptions.ConnectionError:
                print('\n网络异常,自动重试..\n')
                continue

            index = 0
            for content in req.json()['comments']:
                index += 1
                if content['user']['userId'] == int(userId):
                    ab_path = os.path.abspath('.')
                    full_path = os.path.join(ab_path, 'results.txt')
                    with open(full_path, 'a+') as fil:
                        fil.write(f'{content["user"]["nickname"]}说: {content["content"]}, 位于歌曲: {song_name}({ceil(float(_offset + index) / 20)}页)\n')
                    results.append(content['content'])
            _offset += limit
        print("\n\n")
    print(f"An~d we are done! Results.length = {len(results)}")

if __name__ == "__main__":
    # userId = input("Please enter user ID: ")
    userId = '528019872'
    pre_steps(userId)
    search_start(20, 0)
