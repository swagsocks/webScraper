#!/usr/bin/env python

import requests, base64
import json
import simplejson
import ast
import datetime
import csv
import os.path
import psycopg2
from psycopg2.extensions import AsIs
import oauth2

	#Oauth2 Setup
# cred = {'grant_type':'authorization_code', 'code':'########', 'redirect_uri':'#####'}
# usrPass = "########"
# b64Val = base64.b64encode(usrPass)
# ####https://accounts.spotify.com/authorize/?client_id=#######&response_type=code&redirect_uri=#######
# 
# r=requests.post('https://accounts.spotify.com/api/token', 
# 				headers={"Authorization": "Basic %s" % b64Val},
# 				data = cred)
# r1 = r.json()
# refresh_token = r1['refresh_token']
# print refresh_token


conn = psycopg2.connect(database = 'ArtistDB', user = '####', password = '####', host = '####', port = '#####')
cur = conn.cursor()



def WebScraper(artist):
	artist2 = artist.replace('+', '_')
	now = datetime.datetime.now()
	now2 = now.strftime("%Y-%m-%d")	
	#SPOTIFY

	#Call
	try:
		usrPass = "#####"
		b64Val = base64.b64encode(usrPass)
		cred2 = {'grant_type':'refresh_token', 'refresh_token':'####', 'redirect_uri':'####'}
		r2=requests.post('https://accounts.spotify.com/api/token', 
						headers={"Authorization": "Basic %s" % b64Val}, 
						data = cred2)
		r2_1 = r2.json()
		token = r2_1['access_token']
		auth = {"Authorization": "Bearer %s" % token}
		spotURL= 'https://api.spotify.com/v1/search?q='+ artist +'&type=artist'
		data = requests.get(spotURL, headers = auth)
		Spotify = data.json()
		try:
			Spotify1 = Spotify['artists']['items'][0]
			Spotify_Popularity = Spotify1['popularity']
			Spotify_Follower = Spotify1['followers']['total']
		except IndexError:
			Spotify1 = 0
			Spotify_Popularity = 0
			Spotify_Follower = 0
		except KeyError:
			Spotify1 = 0
			Spotify_Popularity = 0
			Spotify_Follower = 0
	except KeyError:
		Spotify1 = 0
		Spotify_Popularity = 0
		Spotify_Follower = 0
	except requests.exceptions.ConnectionError:
		Spotify1 = 0
		Spotify_Popularity = 0
		Spotify_Follower = 0
	except simplejson.scanner.JSONDecodeError:
		Spotify1 = 0
		Spotify_Popularity = 0
		Spotify_Follower = 0
		

	#YOUTUBE - CORRECTION REQUIRED
	#Setup
	"""YouTubeAuth = {'client_id':'####', 'scope':'https://www.googleapis.com/auth/youtube'}
	q = requests.post('https://accounts.google.com/o/oauth2/device/code', data = YouTubeAuth)
	#Go to verification URL, use User code


	YouTubeCred = {'client_id':'####', 'client_secret':'####', 'code':'####', 'grant_type':'http://oauth.net/grant_type/device/1.0'}         

		   
	r=requests.post('https://www.googleapis.com/oauth2/v4/token', data = YouTubeCred)"""
	Refresh = {'client_id':'####', 'client_secret':'####', 'refresh_token': '####', 'grant_type':'refresh_token'}
	s = requests.post('https://www.googleapis.com/oauth2/v4/token', data = Refresh)
	try:
		s1 = s.json()
		YouTubeToken =s1['access_token']
		url = "https://www.googleapis.com/youtube/v3/search?part=id&maxResults=10&q="+ artist
		auth = {"Authorization": "Bearer %s" % YouTubeToken}
		youtube= requests.get(url, headers=auth)
		youtube1 = youtube.json()
		youtube2 = youtube1['items']
		for x in range(0, len(youtube2)):
			if youtube2[x]['id']['kind'] == 'youtube#channel':
				channel_ID=youtube2[x]['id']['channelId']	
		try: 
			url2 = "https://www.googleapis.com/youtube/v3/channels?id="+ str(channel_ID) + "&part=statistics"
			youtube3 = requests.get(url2, headers=auth)
			youtube4 = youtube3.json()
			youtube5 = youtube4['items']
			youtube6 = str(youtube5).strip('[]')
			youtube7 = ast.literal_eval(youtube6)
			YouTube_Views = youtube7['statistics']['viewCount']
			YouTube_Subscribers = youtube7['statistics']['subscriberCount']
		except UnboundLocalError:
			YouTube_Views = 0
			YouTube_Subscribers = 0	
		except KeyError:
			YouTube_Views = 0
			YouTube_Subscribers = 0
	except simplejson.scanner.JSONDecodeError:
		YouTube_Views = 0
		YouTube_Subscribers = 0	
	except KeyError:
		YouTube_Views = 0
		YouTube_Subscribers = 0
	#FACEBOOK
	#Oauth2 Setup
	"""url = 'https://www.facebook.com/v2.9/dialog/oauth?client_id=####&redirect_uri=####' 
	
	url2 = 'https://graph.facebook.com/v2.9/oauth/access_token?'         
	FBparams2 = {'client_id':'####', 'client_secret':'####', 'redirect_uri':'####', 'code':'####'}
	r2 = requests.post(url2, data = FBparams2)

	r3 = {'input_token':'####'}
	requests.get('https://graph.facebook.com/debug_token?input_token=####') """
	#Call
	try:
		FB = requests.get('https://graph.facebook.com/v2.8/search?q=' + artist + '&type=page&access_token=' + '####')
		FB1 = FB.json()
		FB2 = FB1['data']
		FB4 = FB2[0]['id'].encode('utf-8')
		FB3 = FB2[0]['name'].encode('utf-8')
		FB5 = requests.get('https://graph.facebook.com/v2.8/' + FB4  +'/?fields=fan_count,talking_about_count&access_token=' + '####')
		FB6 = FB5.json()
		try:
			Facebook_Talking_About = FB6['talking_about_count']
			Facebook_Fan_Count = FB6['fan_count']
		except KeyError:
			Facebook_Talking_About = 0
			Facebook_Fan_Count = 0
		FB7 = requests.get('https://graph.facebook.com/v2.8/' + FB4  +'/?fields=posts.limit(10)&access_token=' + '####')
		ids = []
		FB8 = FB7.json()
		try:
			FB9 = FB8['posts']['data']
			for x in FB9:
				ids.append(str(x['id']))
			reactions = []
			shares = []
			comments = []
			for x in ids:
				dot = requests.get('https://graph.facebook.com/v2.8/' + x + '?fields=shares,reactions.limit(0).summary(total_count),comments.limit(0).summary(total_count)&access_token='+'####')
				dot1 = dot.json()
				reactions.append(dot1['reactions']['summary']['total_count'])
				comments.append(dot1['comments']['summary']['total_count'])
				try:
					shares.append(dot1['shares']['count'])
				except KeyError:
					shares.append(0)
			reactions2 = sum(reactions)/10
			comments2 = sum(comments)/10
			shares2 = sum(shares)/10
		except KeyError:
			reactions2 = 0
			comments2 = 0
			shares2 = 0
		except requests.exceptions.ConnectionError:
			reactions2 = 0
			comments2 = 0
			shares2 = 0
	except requests.exceptions.ConnectionError:
		reactions2 = 0
		comments2 = 0
		shares2 = 0
		Facebook_Talking_About = 0
		Facebook_Fan_Count = 0
	except IndexError:
		reactions2 = 0
		comments2 = 0
		shares2 = 0
		Facebook_Talking_About = 0
		Facebook_Fan_Count = 0
	#TWITTER	
	consumer_key ='####'
	consumer_secret ='####'
	oauth_token= '####'
	oauth_token_secret = '####'

	def oauth_req(url, key1, secret1, http_method="GET", post_body="", http_headers=None):
		consumer = oauth2.Consumer(key=consumer_key, secret=consumer_secret)
		token = oauth2.Token(key=key1, secret=secret1)
		client = oauth2.Client(consumer, token)
		resp, content = client.request(url, method=http_method, body=post_body, headers=http_headers)
		return content

	data= oauth_req('https://api.twitter.com/1.1/users/search.json?q=' + artist + '&page=1&count=1', key1 = oauth_token, secret1 = oauth_token_secret)

	data1 = json.loads(data)
	try:
		Twitter_Followers= data1[0]['followers_count']
		twit_id = str(data1[0]['id'])
		data3= oauth_req('https://api.twitter.com/1.1/statuses/user_timeline.json?user_id=' + twit_id + '&count=11', key1 = oauth_token, secret1 = oauth_token_secret)
		data4 = json.loads(data3)
		Retweets = []
		Favorites = []
		for x in data4:
			Retweets.append(x['retweet_count'])
			Favorites.append(x['favorite_count'])
		Retweets2 = sum(Retweets)/10
		Favorites2 = sum(Favorites)/10
	except KeyError:
		Twitter_Followers = 0
		Retweets2 = 0
		Favorites2 = 0
	except TypeError:
		Twitter_Followers = 0
		Retweets2 = 0
		Favorites2 = 0
	except IndexError:
		Twitter_Followers = 0
		Retweets2 = 0
		Favorites2 = 0		
			
	#SOUNDCLOUD
	artist3 = artist
	if artist3 == 'drake':
		artist3 = 'octobersveryown'
	try:
		soundcloud = requests.get("https://api.soundcloud.com/users/?q="+ artist3 + "&types=people&client_id=BQiQ6t40b0CG4GgDnZdjyctLNVyMNMlO")
		soundcloud2 = soundcloud.json()
		Soundcloud_Followers = soundcloud2[0]['followers_count']
	except IndexError:
		Soundcloud_Followers = 0
	except simplejson.scanner.JSONDecodeError:
		Soundcloud_Followers = 0
		
	print artist	
			
	Frame = {'Date':now2, 'Spotify_Popularity':Spotify_Popularity, 'Spotify_Followers':Spotify_Follower, 'YouTube_Views':YouTube_Views, 'YouTube_Subscribers':YouTube_Subscribers, 'Facebook_Talking_About':Facebook_Talking_About, 'Facebook_Fan_Count':Facebook_Fan_Count, 'Twitter_Followers':Twitter_Followers, 'Soundcloud_Followers':Soundcloud_Followers, 'Facebook_Post_Shares': shares2, 'Facebook_Post_Likes': reactions2, 'Facebook_Post_Comments':comments2, 'Twitter_Retweets':Retweets2, 'Twitter_Favorites':Favorites2}		
	#EXECUTION 1
	cur.execute('''CREATE TABLE IF NOT EXISTS "%s"
		(Date    DATE			PRIMARY KEY,   
		Spotify_Popularity      BIGSERIAL,    
		Spotify_Followers       BIGSERIAL,    
		YouTube_Views           BIGSERIAL,
		YouTube_Subscribers     BIGSERIAL,
		Facebook_Talking_About  BIGSERIAL,
		Facebook_Fan_Count      BIGSERIAL,
		Twitter_Followers		BIGSERIAL,
		Soundcloud_Followers	BIGSERIAL,
		Facebook_Post_Shares	BIGSERIAL,
		Facebook_Post_Likes		BIGSERIAL,
		Facebook_Post_Comments	BIGSERIAL,
		Twitter_Retweets		BIGSERIAL,
		Twitter_Favorites		BIGSERIAL

	);'''  %artist2)
	#EXECUTION2
	columns = Frame.keys()
	values = [Frame[column] for column in columns]
	for q in range(0,len(values)):
		if values[q]== 'N/A':
			values[q] = 0
	insert_statement = 'insert into' + ' "%s" ' %artist2 + '(%s) values %s'
	cur.execute(insert_statement, (AsIs(','.join(columns)), tuple(values)))
		
cur.execute("select relname from pg_class where relkind='r' and relname !~ '^(pg_|sql_)';")
artistlist1= cur.fetchall()
artistlist2= []
for i in artistlist1:
	artistlist2.append(i[0])

artistlist2.sort()
for j in artistlist2:
	j = j.replace('+', 'and')
	j = j.replace('_', '+')
	WebScraper(j)
conn.commit()
conn.close()
