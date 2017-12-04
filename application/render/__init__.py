

from cgi import parse_qs, escape
import psycopg2
import numpy as np
import pandas as pd
from wsgiref.simple_server import make_server
import fnmatch
from datetime import date, timedelta
import requests, base64
import json
from flask import Flask
from flask import render_template
from flask import request
from flask import Markup
import pickle
import operator

app = Flask(__name__)


@app.route("/")
def start():
	conn = psycopg2.connect(database = 'ArtistDB', user = 'swagsocks', password = 'Thatphrase22', host = 'artistdb.cfwy21axi65h.us-east-1.rds.amazonaws.com', port = '5432')
	cur = conn.cursor()
	cur.execute("select relname from pg_class where relkind='r' and relname !~ '^(pg_|sql_)';")
	artists1 = cur.fetchall()
	artists = []
	for i in artists1:
		artists.append(i[0].replace('_', '+'))
	artists.sort()
	now = date.today()	
	return render_template('start.html', end_date = now, artists = artists)



@app.route("/not_found")
def not_found():
	return """<html><h1>Page not Found</h1><p>
			   That page is unknown. Return to 
			   the <a href="/">home page</a></p>
			   </html>"""

@app.route("/one")
def one():
	conn = psycopg2.connect(database = 'ArtistDB', user = 'swagsocks', password = 'Thatphrase22', host = 'artistdb.cfwy21axi65h.us-east-1.rds.amazonaws.com', port = '5432')
	cur = conn.cursor()
	call_dictionary = parse_qs(request.query_string)
	artist = str(call_dictionary['artist'][0])

	#if artist not in list
	cur.execute("select relname from pg_class where relkind='r' and relname !~ '^(pg_|sql_)';")
	artistlist1= cur.fetchall()
	conn.commit()
	conn.close()
	artistlist2= []
	for i in artistlist1:
		artistlist2.append(i[0])
	artist2 = artist.replace('+', '_')
	
	
	if artist2 not in artistlist2:
	
		usrPass = "a7670b30dac04cb982b548123f466995:a9e01e681cd345469ddc7502972f6ed3"
		b64Val = base64.b64encode(usrPass)

		cred2 = {'grant_type':'refresh_token', 'refresh_token':'AQA_O9sBbrU_-iJwHOamTbWsMZAgUp1_WD0Wx9dQAXRuQOdASd9pKCdkmi03ija1dSFFR9ox_53JQzB-Tar_djKyVzEF8fjPBNrdgD9c6UPrJS7R7N9wSVN99QOTJq-P62A', 'redirect_uri':'http://the925.io'}
		r2=requests.post('https://accounts.spotify.com/api/token', 
						headers={"Authorization": "Basic %s" % b64Val}, 
						data = cred2)
		r2_1 = r2.json()

		token = r2_1['access_token']
		auth = {"Authorization": "Bearer %s" % token}

		spotURL= 'https://api.spotify.com/v1/search?q='+ artist +'&type=artist'
		conn = psycopg2.connect(database = 'ArtistDB', user = 'swagsocks', password = 'Thatphrase22', host = 'artistdb.cfwy21axi65h.us-east-1.rds.amazonaws.com', port = '5432')
		cur = conn.cursor()
		try:
			data = requests.get(spotURL, headers = auth)
			Spotify = data.json()
			Spotify1 = Spotify['artists']['items'][0]
			Spotify_Popularity_Test = Spotify1['popularity']
			if Spotify_Popularity_Test > 20:
				cur.execute('''CREATE TABLE IF NOT EXISTS %s
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

				);'''  %artist2 )
				output = """<html><h1>ADDED! Try tomorrow after 10:05AM for success!</h1>
<br><a href="/">home page</a>
</html>"""
			else: 
				output = """<html><h1>Yo boi dont make good music</h1><br><a href="/">home page</a></html>"""
		except IndexError:
			output = """<html><h1>Yo boi dont make good music</h1><br><a href="/">home page</a></html>"""	
		conn.commit()
		conn.close()	
		
	else:
		usrPass = "a7670b30dac04cb982b548123f466995:a9e01e681cd345469ddc7502972f6ed3"
		b64Val = base64.b64encode(usrPass)
		cred2 = {'grant_type':'refresh_token', 'refresh_token':'AQA_O9sBbrU_-iJwHOamTbWsMZAgUp1_WD0Wx9dQAXRuQOdASd9pKCdkmi03ija1dSFFR9ox_53JQzB-Tar_djKyVzEF8fjPBNrdgD9c6UPrJS7R7N9wSVN99QOTJq-P62A', 'redirect_uri':'http://the925.io'}
		r2=requests.post('https://accounts.spotify.com/api/token', 
					headers={"Authorization": "Basic %s" % b64Val}, 
					data = cred2)
		r2_1 = r2.json()
		token = r2_1['access_token']
		auth = {"Authorization": "Bearer %s" % token}
		spotURL= 'https://api.spotify.com/v1/search?q='+ artist +'&type=artist'
		data = requests.get(spotURL, headers = auth)
		Spotify = data.json()
		Spot_prof_URL = Spotify['artists']['items'][0]['images'][0]['url']

		#WHERE CLAUSE - USE .get for either KEY or NONE
		start_date1 = call_dictionary.get('start_date')
		if start_date1:
			start_date1 = start_date1[0]
			start_date2 = 'date > \'{start_date}\'::date'
			start_date3 = start_date2.format(start_date = str(start_date1))
		else:
			start_date3 = ''	

		end_date1 = call_dictionary.get('end_date')
		if end_date1:
			end_date1 = end_date1[0]
			end_date2 = 'date < \'{end_date}\'::date'
			end_date3 = end_date2.format(end_date = str(end_date1))	
		else:
			end_date3 = ''
	
		if start_date3 or end_date3:
			conjunction1= ' where '
		else:
			conjunction1= ''
		if start_date3 and end_date3:
			conjunction2 = ' and '
		else:
			conjunction2 = ''
		statement2 ='select * from {artist}' + conjunction1 + start_date3 + conjunction2 + end_date3 
		statement3 = statement2.format(artist = artist2)
		
		
		conn = psycopg2.connect(database = 'ArtistDB', user = 'swagsocks', password = 'Thatphrase22', host = 'artistdb.cfwy21axi65h.us-east-1.rds.amazonaws.com', port = '5432')
		cur = conn.cursor()
		
		cur.execute(statement3)
		data = cur.fetchall()
		colnames = [desc[0] for desc in cur.description]
		
		conn.commit()
		conn.close()
		
		df = pd.DataFrame(data, columns = colnames)		
		diction = dict(zip(colnames, (df[i].tolist() for i in colnames)))				
		import math
		def roundup(x):
			return int(math.ceil(x / 1000.0)) * 1000
		def rounddown(x):
			return int(math.floor(x / 1000.0)) * 1000
			
		def roundup10(x):
			return int(math.ceil(x / 10.0)) * 10
		def rounddown10(x):
			return int(math.floor(x / 10.0)) * 10
		
		dates = diction['date']
		spot_fol = diction['spotify_followers']
		spot_pop = diction['spotify_popularity']
		fb_fan = diction['facebook_fan_count']
		fb_talk = diction ['facebook_talking_about']
		yt_views = diction['youtube_views']
		yt_subs = diction['youtube_subscribers']
		twit_fol = diction['twitter_followers']
		sc_fol = diction['soundcloud_followers']
		fb_post_share = diction['facebook_post_shares']
		fb_post_like = diction['facebook_post_likes']
		fb_post_com = diction['facebook_post_comments']
		twit_retweet = diction['twitter_retweets']
		twit_tweet_fav = diction['twitter_favorites']
		
		aslists = [spot_pop, spot_fol, yt_views, yt_subs, fb_talk, fb_fan, twit_fol, sc_fol]
		aslists2 = [fb_post_share, fb_post_like, fb_post_com, twit_retweet, twit_tweet_fav]
		
		class Stat:
			def __init__(self, data1):
				self.data = data1
				self.graph_max = roundup(max(data1))
				self.graph_max2 = roundup10(max(data1))
				self.graph_min = rounddown(min(data1))
				self.graph_min2 = rounddown10(min(data1))
				self.percent_change = (data1[len(data1)-1]-data1[0])/float(data1[0]) * 100
				
		for x in aslists:
			if x[0] == 0:
				x[0] = 1
				x[len(x)-1] = 1
		objs = [Stat(i) for i in aslists]
		for x in aslists2:
			if x[0] == 0:
				x[0] = 1
				x[len(x)-1] = 1
		objs2 = [Stat(i) for i in aslists2]
		html2 = df.to_html()
		
		conn = psycopg2.connect(database = 'billboarddb', user = 'swagsocks', password = 'Thatphrase22', host = 'artistdb.cfwy21axi65h.us-east-1.rds.amazonaws.com', port = '5432')
		cur = conn.cursor()
		billboard_test = '''select relname from pg_class where relname ='{artist}';'''
		billboard_test2 = billboard_test.format(artist = artist2)
		cur.execute(billboard_test2)
		test_data = cur.fetchall()
		if len(test_data) != 0:
			billboard_statement1 = 'select song, Min(rank) as top_rank, max(weeks) as total_weeks from {artist} group by song order by top_rank;'
			billboard_statement2 = billboard_statement1.format(artist = artist2)
			cur.execute(billboard_statement2)
			billboard_data = cur.fetchall()
			billboard_stats = [desc[0] for desc in cur.description]
			billboard_df = pd.DataFrame(billboard_data, columns = billboard_stats)		
			html3 = billboard_df.to_html()

		else:
			html3 = ''	
		conn.commit()
		conn.close()

		output = render_template('response.html', artist = artist, html3 = html3, html2=html2, picture = Spot_prof_URL, colnames = colnames[1:9], colnames2 = colnames[9:14], objs=objs, objs2=objs2, labels=dates)
	
	return output
	
	
@app.route('/rookies')
def rookies():
	new = open('/var/www/scrape_application/rookie_artists.pickle', 'rb')
	rookie_artists = pickle.load(new)
	html_list = []

	for artist in rookie_artists:
		artist = artist.replace('_', '+')
		usrPass = "a7670b30dac04cb982b548123f466995:a9e01e681cd345469ddc7502972f6ed3"
		b64Val = base64.b64encode(usrPass)
		cred2 = {'grant_type':'refresh_token', 'refresh_token':'AQA_O9sBbrU_-iJwHOamTbWsMZAgUp1_WD0Wx9dQAXRuQOdASd9pKCdkmi03ija1dSFFR9ox_53JQzB-Tar_djKyVzEF8fjPBNrdgD9c6UPrJS7R7N9wSVN99QOTJq-P62A', 'redirect_uri':'http://the925.io'}
		r2=requests.post('https://accounts.spotify.com/api/token', 
					headers={"Authorization": "Basic %s" % b64Val}, 
					data = cred2)
		r2_1 = r2.json()
		token = r2_1['access_token']
		auth = {"Authorization": "Bearer %s" % token}
		spotURL= 'https://api.spotify.com/v1/search?q='+ artist +'&type=track'

		data = requests.get(spotURL, headers = auth)
		Spotify = data.json()
		URI = Spotify['tracks']['items'][0]['album']['uri']

		spot_html = """<iframe src="https://open.spotify.com/embed?uri={URI}&theme=white" width="300" height="380" frameborder="0" allowtransparency="true"></iframe>"""
		spot_html = spot_html.format(URI = URI)
		html_list.append(spot_html)
	html_embed = '<br><br>'.join(html_list)
	return render_template('rookies.html', artists = rookie_artists, tracks = html_embed)
	


	
@app.route('/privacy_policy')
def privacy():
	return render_template('privacy_policy.css')

ADMINS = ['minusme5@yahoo.com']
if not app.debug:
    import logging
    from logging.handlers import SMTPHandler
    mail_handler = SMTPHandler('http://34.195.159.78/',
                               'server-error@the925.io',
                               ADMINS, 'YourApplication Failed')
    mail_handler.setLevel(logging.ERROR)
    app.logger.addHandler(mail_handler)
 
 
 
@app.route('/top_ten')
def top_ten():
	stats = ['spotify_followers', 'spotify_popularity', 'facebook_fan_count', 'facebook_talking_about', 'youtube_views', 'youtube_subscribers', 'twitter_followers', 'soundcloud_followers', 'facebook_post_shares', 'facebook_post_likes', 'facebook_post_comments', 'twitter_retweets', 'twitter_favorites']
	yesterday = date.today()- timedelta(1)
	return render_template('top_ten.html', stats = stats, end_date = yesterday)

@app.route('/top_ten_results')
def top_ten_results():
	conn = psycopg2.connect(database = 'ArtistDB', user = 'swagsocks', password = 'Thatphrase22', host = 'artistdb.cfwy21axi65h.us-east-1.rds.amazonaws.com', port = '5432')
	cur = conn.cursor()
	cur.execute("select relname from pg_class where relkind='r' and relname !~ '^(pg_|sql_)';")
	artists= cur.fetchall()
	call_dictionary = parse_qs(request.query_string)
	start_date = call_dictionary.get('start_date')[0]
	end_date = call_dictionary.get('end_date')[0]
	stat = call_dictionary.get('stat')[0]
	growth_dict = {}
	for x in artists:
		statement1 ='select {stat} from "{artist}" where Date = \'{start_date}\'::date'
		statement_11 = statement1.format(stat =stat, artist = str(x[0]), start_date = start_date)
		statement2 ='select {stat} from "{artist}" where Date = \'{end_date}\'::date'
		statement_22 = statement2.format(stat =stat, artist = str(x[0]), end_date = end_date)
		cur.execute(statement_11)
		start_data = cur.fetchall()
		cur.execute(statement_22)
		end_data = cur.fetchall()
		if start_data and end_data:
			if start_data[0][0] != 0:
				growth = (end_data[0][0] - start_data[0][0])/float(start_data[0][0])
				growth_dict[x[0]] = growth
	ordered_growth = sorted(growth_dict.items(), key=operator.itemgetter(1), reverse = True)
	top_ten = ordered_growth[:10]
	top_artists = []
	growth_factor = []
	for x in top_ten:
		top_artists.append(x[0])
		growth_factor.append(str(float("{0:.2f}".format(x[1]*100))) + '%')
	top_dict = {}
	top_dict['Artist'] = top_artists
	top_dict['Growth'] = growth_factor
	top_ten_table= pd.DataFrame(top_dict)
	top_ten_html = top_ten_table.to_html()
	return render_template('top_ten_results.html', stat = stat, top_ten = top_ten_html)
