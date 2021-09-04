import os
import re
import tweepy as tp
from dotenv import load_dotenv

load_dotenv()

CONSUMER_API_KEY = os.environ.get("CONSUMER_API_KEY")
CONSUMER_SECRET_API_KEY = os.environ.get("CONSUMER_SECRET_API_KEY")
ACCESS_TOKEN = os.environ.get("ACCESS_TOKEN")
ACCESS_TOKEN_SECRET = os.environ.get("ACCESS_TOKEN_SECRET")

auth = tp.OAuthHandler(CONSUMER_API_KEY, CONSUMER_SECRET_API_KEY)
# auth.set_access_token(ACCESS_TOKEN, ACCESS_TOKEN_SECRET)
api = tp.API(auth)

user_id = "@odmishien"
fav_tweets = api.favorites(user_id, count=50)

print("user:" + user_id)
print("favorite tweets:")


url_pattern = re.compile("https://")
for tweet in fav_tweets:
    if url_pattern.search(tweet.text):
        continue
    print("-------------------")
    print(tweet.text)
