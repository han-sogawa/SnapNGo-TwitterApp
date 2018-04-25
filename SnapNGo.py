from tweepy import Stream
from tweepy import OAuthHandler
import tweepy
import json, math, re, csv
from tweepy.streaming import StreamListener
from datetime import *

keys = json.load(open('keys.json'))
consumer_key = keys['consumer_key']
consumer_key_secret = keys['consumer_key_secret']
access_token = keys['access_token']
access_token_secret = keys['access_token_secret']
auth = OAuthHandler(consumer_key, consumer_key_secret)
auth.secure = True
auth.set_access_token(access_token, access_token_secret)
api = tweepy.API(auth_handler=auth)

class DMListener(StreamListener):

    def on_connect(self):
        print("Stream Connected")


    def on_disconnect(self, notice):
        print("Stream Connection Lost:", notice)


    def on_data(self, status):
        status_json = json.loads(status)
        print(status)
        if 'direct_message' in status_json:
            name = str(status_json['direct_message']['sender']['screen_name'])
            text = str(status_json['direct_message']['text'])
            time = str(status_json['direct_message']['created_at'])
            print '----------------------------------------------------------------'
            if(name != 'SnapNGo_2018'):
                print 'Message Received from: ' + name
            else:
                print 'Message Sent: '

            print 'Message Text: ' + text
            print 'Message Time: ' + time
            print '----------------------------------------------------------------'
            BotResponses.getResponse(text, name, time)
        return True


    def on_error(self, status):
        print("Error:", status)

class BotResponses:

    @staticmethod
    def getResponse(text, name, time):
        request_taskID = BotResponses.userRequestingTask(text)
        submit_taskID = BotResponses.userSubmittingTask(text)
        #print 'detected task ' + request_taskID
        if(request_taskID is not None):
            # check if task is available
            print 'User ' + name + ' is trying to request task #' + request_taskID
            message = "Thank you, you have been assigned task #" + request_taskID
            api.send_direct_message(screen_name = name, text = message)
            details = "Task #1000 details: Photo of Snap 'N' Go Student Poster from 5:30-7:00pm on 04/20/2018. Compensation: $1.00"
            api.send_direct_message(screen_name=name, text=details)
        elif (submit_taskID is not None):
            print 'User ' + name + ' is submitting photo for task #' + submit_taskID
            confirmation = "Task #" + submit_taskID + " submission is successful. Compensation: $1.00"
            api.send_direct_message(screen_name=name, text=confirmation)

    @staticmethod
    def userRequestingTask(message):
        #print 'searching for regex'
        p = re.compile('request task #(\d\d\d\d)')
        m = p.search(message)
        if m is None:
            #print 'did not find regex'
            return m
        else:
            #print 'found regex'
            return m.group(1)

    @staticmethod
    def userSubmittingTask(message):
        # print 'searching for regex'
        p = re.compile('submit task #(\d\d\d\d)')
        m = p.search(message)
        if m is None:
            # print 'did not find regex'
            return m
        else:
            # print 'found regex'
            return m.group(1)
def main():

    auth = OAuthHandler(consumer_key, consumer_key_secret)
    auth.secure = True
    auth.set_access_token(access_token, access_token_secret)

    dmlistener = Stream(auth, DMListener())
    dmlistener.userstream()
    #print 'hello world'


if __name__ == '__main__':
    #when a follow request is received, follow them back and send a message.
    main()