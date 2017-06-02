import twatter as tw
import tweepy
import os
import time

## Threshold number of maximum friends, users following more than this number
## will be considered spam accounts and filtered
MAX_FRIENDS = 200

## Retrieves and saves tweets inside search area as returned by Twitter's
## search in area results
## lat: latitude of center of search area
## long: longitude of center of search area  
## radius: size of search area
## num: number of tweets to retrieve at each step
def buildDataSet(lat, lon, radius, num):
    twat = tw.Twatter('user')
    tweets = twat.getTweetsFromCoords(lat, lon, radius, 100)
    i = 0
    users = []
    for (dirpath, dirnames, filenames) in os.walk('./data/friends/'):
        for filename in filenames:
            name, ext = os.path.splitext(filename)
            if ext == '.txt':
                users.append(name)
    for tweet in tweets:
        print tweet.text
        if tweet.user.friends_count <= MAX_FRIENDS: ## filter spamers
            try:
                user_id = tweet.user.id_str
                if user_id not in users:
                    users.append(user_id)
                    friends = twat.getFriends(user_id)
                    for friend in friends:
                        print friend.id_str
                if i > num:
                    return
                i+=1
            except tweepy.error.RateLimitError:
                time.sleep(15*60)

## Example use: mines tweets in search area of 30km around Mexico City
## using 1000 tweets at each step
buildDataSet("19.4326", "-99.1332", "30km", 1000)