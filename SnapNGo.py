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

task_dictionary = {}

import re, json, csv
from datetime import *
import json


class Task:
    def __init__(self, id, location, datetime, compensation):
        self.id = id

        self.location = location
        self.datetime = datetime
        self.compensation = compensation
        self.tweetSent = False
        self.tweetSentTime = 0
        self.assignedTo = ''
        self.taskSubmitted = False
        self.submissionPhotoLink = ''
        self.submissionTime = 0

    def toString(self):
        return 'Task ID: ' + str(self.id) + '\t Location: ' + self.location + '\t Date: ' + self.datetime.strftime(
            "%B %d, %Y %I:%M%p") + '\t Compensation:' + str(self.compensation) + '\n'

    def toString_StrDatetime(self):
        return 'Task ID: ' + str(
            self.id) + '\t Location: ' + self.location + '\t Date: ' + self.datetime + '\t Compensation:' + str(
            self.compensation) + '\n'

    def scheduleTweet(self, tweet_time):
        # TODO: add threading to schedule task (this method doesn't do anything right now)
        now = datetime.now()
        delay = (tweet_time - now).total_seconds()
        print('Delay: ' + delay)

    def sendTaskTweet(self, api):
        if (not self.tweetSent):
            #api.PostUpdate(self.toString())
            self.tweetSent = True
            self.tweetSentTime = datetime.now()

    def getFileRow(self):
        return [self.id, self.location, self.datetime.strftime("%B %d, %Y %I:%M%p"), self.compensation, self.tweetSent,
                self.tweetSentTime, self.assignedTo, self.taskSubmitted, self.submissionPhotoLink, self.submissionTime]


class SnapNGo:
    def __init__(self):
        self.task_ID = 1000
        #self.task_dictionary = {}
        '''
        keys = json.load(open('keys.json'))
        self.consumer_key = keys['consumer_key']
        self.consumer_key_secret = keys['consumer_key_secret']

        self.access_token = keys['access_token']
        self.access_token_secret = keys['access_token_secret']

        self.api = twitter.Api(consumer_key=self.consumer_key,
                               consumer_secret=self.consumer_key_secret,
                               access_token_key=self.access_token,
                               access_token_secret=self.access_token_secret)
        '''

    def selectAction(self):
        print("Type '1' to add new tasks")
        print("Type '2' to tweet unsent tasks")
        print("Type '3' to print all tasks")

        print("Type '4' to write tasks to a file")
        print("Type 'EXIT' to exit the program")
        action = raw_input('>')
        while (action != 'EXIT'):
            if (action == '1'):
                print('Type 1 to enter tasks via command line, Type 2 to input tasks through a file')
                enter_tasks = raw_input('>>')
                if (enter_tasks == '1'):
                    self.addTasksViaCommandLine()
                if (enter_tasks == '2'):
                    print('Type the name of the file')
                    #file_name = raw_input('>>>')
                    #self.addTasksViaFile(file_name)
            if (action == '2'):
                self.sendUnsentTweets()
            if (action == '3'):
                self.printTasks()
            if (action == '4'):
                print('Write the name of the file to write tasks to:')
                #file_name = raw_input('>>')
                #self.writeTasksToFile(file_name)

            print("Type '1' to add new tasks")
            print("Type '2' to tweet unsent tasks")
            print("Type '3' to print all tasks")
            print("Type '4' to write tasks to a file")
            print("Type 'EXIT' to exit the program")
            action = raw_input('>')

    def addTasksViaCommandLine(self):
        input = raw_input('Please enter a task in the following format: location, month, day, year, hour, minutes\n>')
        while (input != 'end'):
            # check to see if input has correct length and is otherwise correct format
            input_array = re.sub(r'\s', '', input).split(',')
            task_date = date(int(input_array[3]), int(input_array[1]), int(input_array[2]))
            task_time = time(int(input_array[4]), int(input_array[5]))
            task_datetime = datetime.combine(task_date, task_time)

            #self.task_dictionary[self.task_ID] = Task(self.task_ID, input_array[0], task_datetime, input_array[6])
            task_dictionary[self.task_ID] = Task(self.task_ID, input_array[0], task_datetime, input_array[6])
            #print('New task created: ' + self.task_dictionary[self.task_ID].toString())
            print('New task created: ' + task_dictionary[self.task_ID].toString())
            self.task_ID += 1

            input = raw_input('>')

        print 'All tasks: \n'
        self.printTasks()

    def printTasks(self):
        s = ''
        print self.task_ID
        for i in range(1000, self.task_ID):
            s += task_dictionary[i].toString()
            #s += self.task_dictionary[i].toString()
        print('All Tasks:\n' + s)


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
    print('Welcome to Snap \'N\' Go!')

    auth = OAuthHandler(consumer_key, consumer_key_secret)
    auth.secure = True
    auth.set_access_token(access_token, access_token_secret)
    '''
    dmlistener = Stream(auth, DMListener())
    dmlistener.userstream()
    '''
    snap = SnapNGo()
    snap.selectAction()


if __name__ == '__main__':
    #when a follow request is received, follow them back and send a message.
    main()