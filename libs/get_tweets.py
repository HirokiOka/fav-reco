import re
import tweepy as tp


"""
 検索したい単語と取ってきたいTweet数(デフォルトは10)を引数に渡すと，
 検索したい単語を含んだtweetをリストにして返す
"""
def getTweetsFromSearchWords(search_word, count=10):
    CONSUMER_API_KEY = "SOciKVMCVQU4ZqucCpLsf5MvS"
    CONSUMER_SECRET_API_KEY = "7vcZ4O3zTQ2yulxxLPhICCaOydWGabSEcsTja10viFCrJLHzhz"
    auth = tp.OAuthHandler(CONSUMER_API_KEY, CONSUMER_SECRET_API_KEY)
    api = tp.API(auth)
    url_pattern = re.compile("https://")
    tweets = tp.Cursor(api.search, q=search_word, lang="ja").items(count)
    results = []
    for tweet in tweets:
        if url_pattern.search(tweet.text):
            continue
        results.append(tweet.text)
    return results

