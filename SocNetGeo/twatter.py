import tweepy as twp
from time import sleep, strftime, time
import csv
import json

TIME = time()

## Class that handles connection to Twitter
class Twatter:
    
	## Initializes the connection to Twitter API
	## mode: user or app
    def __init__(self, mode):
		#Consumer key and secret need to be generated for the application on Twitter's developers page
        cons_key = ""
        cons_sec = ""
        
        if mode == "user":
			# User access token and secret key need to be supplied by Twitter user when in user mode
            accs_tok = ''
            accs_sec = ''

            self.auth = twp.OAuthHandler(cons_key, cons_sec)
            self.auth.set_access_token(accs_tok, accs_sec)

        if mode == "app":
            self.auth = twp.AppAuthHandler(cons_key, cons_sec)

        self.mode = mode
        self.api = twp.API(self.auth)
    
	## Determines the amount of time needed to wait to avoid exceeding Twitter's rate limits
    def sleepyTime(self, requestType, request):
        global TIME
        t = strftime('%H:%M:%S')
        rate_limit = self.api.rate_limit_status()['resources']
        lim = rate_limit[requestType]['/'+requestType+'/'+request]['limit']    
        process_time = time() - TIME
        TIME = time()
        cooldown = float(15 * 60) / float(lim) - process_time
        if cooldown > 0:
            print "Sleeping", cooldown 
        return cooldown if cooldown > 0 else 0
    
	## Retrieves and saves all Twitter friends from requested user
	## name: Twitter name of user
	## numOfTweets: size of Cursor object
    def getFriends(self, name, numOfTweets=100):
        with open("data/friends/"+name+".txt", 'a') as f:
            cursor = twp.Cursor(self.api.friends, id=name, count=numOfTweets)
            for i in cursor.pages():
                sleep(self.sleepyTime('friends', 'list'))
                for user in i:
                    json.dump(user._json, f)
                    f.write('\n')
                    yield user
    
	## Retrieves and saves all Twitter followers from requested user
	## name: Twitter name of user
	## numOfTweets: size of Cursor object
    def getFollowers(self, name, numOfTweets=100):
        with open("data/followers/"+name+".txt", 'a') as f:
            cursor = twp.Cursor(self.api.followers, id=name, count=numOfTweets)
            for i in cursor.pages():
                for user in i:
                    sleep(self.sleepyTime('followers', 'list'))
                    json.dump(user._json, f)
                    f.write('\n')
                    yield user
    
	## Retrieves and saves all tweets from requested user
	## name: Twitter name of user
	## numOfTweets: size of Cursor object
    def getTimeline(self, name, numOfTweets=100):
        cursor = twp.Cursor(self.api.user_timeline, id=name, count=numOfTweets)
        for i in cursor.pages():
            sleep(self.sleepyTime('statuses', 'user_timeline'))
            for tweet in i:
               yield tweet
    
	## Retrieves and saves tweets from users in given area
	## lat: latitude of center of search area
	## long: longitude of center of search area
	## radius: size of search area
	## numOfTweets: size of Cursor object    
    def getTweetsFromCoords(self, lat, long, radius, numOfTweets=100):
        with open("data/search/"+lat+"-"+long+"-"+radius+".txt",'a') as f:
            geo = lat+","+long+","+radius
            cursor = twp.Cursor(self.api.search, q="*", count=numOfTweets, geocode=geo)
            for i in cursor.pages():
                sleep(self.sleepyTime('search', 'tweets'))
                for tweet in i:
                    json.dump(tweet._json, f)
                    f.write('\n')
                    yield tweet
    
	## Retrieves friendship status between two users
	## name1: Twitter name of first user
	## name2: Twitter name of second user
    def checkFriendship(self, name1, name2):
        return self.api.show_friendship(source_id=name1, target_id=name2)[0].following, self.api.show_friendship(source_id=name1, target_id=name2)[0].followed_by
