import os
import datetime
import tweepy
from tweepy import Stream
from tweepy.streaming import StreamListener
from tweepy import OAuthHandler
import config

# Authenticate to Twitter API
auth = OAuthHandler(config.consumer_key, config.consumer_secret)
auth.set_access_token(config.access_token, config.access_secret)
api = tweepy.API(auth)

# Script Global Variables
cwd = os.getcwd()
os_system = os.name
if os_system == 'nt':
    in_prog_out_dir = cwd + '\\batch_extracts\\in_progress\\'
    complete_out_dir = cwd + '\\batch_extracts\\complete\\'
else:
    in_prog_out_dir = cwd + '/batch_extracts/in_progress/'
    complete_out_dir = cwd + '/batch_extracts/complete/'


# Function to create the tweet tracker hash list from the configuration file's hash object
def hash_list():
    hash_list = []
    for hash_key in list(config.hash_obj.keys()):
        for hash_val in config.hash_obj[hash_key]:
            hash_list.append(hash_val)
    return hash_list


# Twitter Batch Listener
class BatchListener(StreamListener):

    # Initializer
    def __init__(self):
        super(StreamListener, self).__init__()
        self.i = 0
        self.dt = datetime.datetime.today()
        self.dt_str = str(self.dt).replace(':', '-').replace(' ', '_').split('.')[0]
        self.out_file = self.dt_str + '_batch.json'

    # Twitter Data Retrieval Function
    def on_data(self, raw_tweet):
        try:
            with open(in_prog_out_dir + self.out_file, 'a') as op_file:
                op_file.write(raw_tweet)
                self.i += 1
                if self.i == config.batch_size:
                    op_file.close()
                    os.rename(in_prog_out_dir + self.out_file, complete_out_dir + self.out_file)
                    self.dt = datetime.datetime.today()
                    print('New Tweet Batch Created at ' + str(self.dt) + '!\nContinuing Process...')
                    self.i = 0
                    self.dt_str = str(self.dt).replace(':', '-').replace(' ', '_').split('.')[0]
                    self.out_file = self.dt_str + '_batch.json'
                return True
        except BaseException as e:
            print("Error on_data: %s" % str(e))
        return True

    # Error Handler
    def on_error(self, status):
        print(status)
        return True


print('Twitter Batch Process running!')
tweet_batch_stream = Stream(auth, BatchListener())
tweet_batch_stream.filter(track=hash_list())