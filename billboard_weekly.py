#!/usr/bin/env python

import datetime
import billboard
import psycopg2
import re
from psycopg2.extensions import AsIs
import pickle

now = datetime.datetime.now()
now2 = now.strftime("%Y-%m-%d")

con = psycopg2.connect(database = "####", user = '####', password = '####', host = '####', port = '####')
cur = con.cursor()
cur.execute("select relname from pg_class where relkind='r' and relname !~ '^(pg_|sql_)';")
artists1 = cur.fetchall()
artists2 = []
for y in artists1:
	artists2.append(y[0])
con.commit()
con.close()

for_pickle = []

chart = billboard.ChartData('hot-100')
for art in chart:
	art.artist = re.split(' & | feat | feat. | x | Featuring |, ', art.artist)
	for x in art.artist:
		x = str(x.lower().replace(' ', '_').replace('-', '_').replace('.', '').replace('+', 'and'))
		if x not in artists2:		
			for_pickle.append(x)
			print x
		title = art.title
		rank = art.rank
		weeks = art.weeks
		Frame = {'Date':now2, 'Song':title, 'Rank':rank, 'Weeks':weeks}
		columns = Frame.keys()
		values = [Frame[column] for column in columns]
		 
		conn = psycopg2.connect(database = '####', user = '####', password = '####', host = '####', port = '####')
		curs = conn.cursor()
		curs.execute('''CREATE TABLE IF NOT EXISTS "%s"
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
		);'''  %x)	
		
		conn.commit()
		conn.close()
		
		
		con = psycopg2.connect(database = "####", user = '####', password = '####', host = '####', port = '####')
		cur = con.cursor()
			
		cur.execute('''CREATE TABLE IF NOT EXISTS "%s"
			(Date    				Date,   
			Song					text,
			Rank					smallint,
			Weeks					smallint
		);'''  %x)	
		insert_statement = 'insert into' + ' "%s" ' %x + '(%s) values %s'
		cur.execute(insert_statement, (AsIs(','.join(columns)), tuple(values)))
		
		con.commit()
		con.close()
		
with open('####/rookie_artists.pickle', 'wb') as f:
	pickle.dump(for_pickle, f)
