import os
import random
import re
import sys
from htmlentitydefs import name2codepoint as n2c
import tweepy
from local_settings import *

class TwitterAPI:
    def __init__(self):
        consumer_key = os.environ.get('MY_CONSUMER_KEY')
        consumer_secret = os.environ.get('MY_CONSUMER_SECRET')
        auth = tweepy.OAuthHandler(consumer_key, consumer_secret)
        access_token = os.environ.get('MY_ACCESS_TOKEN_KEY')
        access_token_secret = os.environ.get('MY_ACCESS_TOKEN_SECRET')
        auth.set_access_token(access_token, access_token_secret)
        self.api = tweepy.API(auth, wait_on_rate_limit=True)

    def tweet(self, message):
        self.api.update_status(status=message)

def entity(text):
    if text[:2] == '&#':
        try:
            if text[:3] == '&#x':
                return unichr(int(text[3:-1], 16))
            else:
                return unichr(int(text[2:-1]))
        except ValueError:
            pass
    else:
        guess = text[1:-1]
        numero = n2c[guess]
        try:
            text = unichr(numero)
        except KeyError:
            pass
    return text

def filter_tweet(tweet):
    tweet.text = re.sub(r'\b(RT|MT) .+', '', tweet.text) #take out anything after RT or MT
    tweet.text = re.sub(
        r'(\#|@|(h\/t)|(http))\S+',
        '',
        tweet.text
    ) #Take out URLs, hashtags, hts, etc.
    tweet.text = re.sub(r'\n', '', tweet.text) #take out new lines.
    tweet.text = re.sub(r'\"|\(|\)', '', tweet.text) #take out quotes.
    htmlsents = re.findall(r'&\w+;', tweet.text)
    if len(htmlsents) > 0:
        for item in htmlsents:
            tweet.text = re.sub(item, entity(item), tweet.text)
    tweet.text = re.sub(r'\xe9', 'e', tweet.text) #take out accented e
    return tweet.text

def grab_tweets(twitter, max_id=None):
    source_tweets = []
    user_tweets = twitter.api.user_timeline(
        screen_name=user,
        count=200,
        max_id=max_id
    )
    max_id = user_tweets[len(user_tweets)-1].id-1
    for tweet in user_tweets:
        if tweet.text[0][0] != '@':
            tweet.text = filter_tweet(tweet)
            if len(tweet.text) != 0:
                source_tweets.append(tweet.text)
    return source_tweets, max_id

if __name__ == '__main__':
    twitter = TwitterAPI()
    if not DEBUG:
        guess = random.choice(range(ODDS))
    else:
        guess = 0

    if guess == 0:
        # gets tweets
        source_tweets = []
        user = SOURCE_ACCOUNT
        max_id = None
        for x in range(17)[1:]:
            source_tweets_iter, max_id = grab_tweets(twitter, max_id)
            source_tweets += source_tweets_iter
        print '{0} tweets found in {1}'.format(len(source_tweets), SOURCE_ACCOUNT)
        if len(source_tweets) == 0:
            print 'Error fetching tweets from Twitter. Aborting.'
            sys.exit()

        source_tweet = random.choice(source_tweets)
        words = source_tweet.split()

        tweet_length = 0

        if len(words) > 3:
            tweet_length = random.randint(3, len(words))
        else:
            tweet_length = len(words)

        tweet_words = words[:tweet_length]

        print tweet_length
        print tweet_words

        word = list(tweet_words[tweet_length - 1])

        print word

        if len(word) > 5:
            print word
            print ''.join(word[:3])
            print ''.join(word[3:])
            partial = word[3:]
            random.shuffle(partial)
            tweet_words[tweet_length - 1] = ''.join(word[:3]) + ''.join(partial)
        elif len(word) < 4:
            # remove a letter and add fefe
            print 'Shuffled word too short. Aborting.'
            sys.exit()
        else:
            random.shuffle(word)
            tweet_words[tweet_length - 1] = ''.join(word)


        tweet = ' '.join(tweet_words)

        print source_tweet
        print tweet_length
        print tweet

        rando = random.randint(0, 20)
        if rando == 1:
            tweet = tweet.upper()

        if tweet != None and len(tweet) < 140:
            if not DEBUG:
                twitter.tweet(tweet)
            print 'Tweeted \'' + tweet + '\''
        elif tweet is None:
            print 'Tweet is empty, sorry.'
        else:
            print 'TOO LONG: ' + tweet
    else:
        print str(guess) + ' No, sorry, not this time.' # message if the random number fails.
