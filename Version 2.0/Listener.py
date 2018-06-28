from tweepy import Stream
from tweepy import OAuthHandler
import tweepy
import json, math, re, csv, random
from tweepy.streaming import StreamListener
import time as t
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

def writecsv(text, name, time, recipient):
    with open('data.csv', 'a') as csvfile:
        writer = csv.writer(csvfile, delimiter=',')
        writer.writerow([text, name, time, recipient])

# adds new Tasks in json file to the task dictioanry
def readTasks():
    # open the json file of tasks
    dictionary = json.load(open('tasks.json'))

    # for every task in the file
    for key in dictionary.keys():
        # if the task doesn't already exist in task_dictionary
        if (not int(key) in task_dictionary.keys()):
            # format the datetime variable
            date_time = dictionary[str(key)]["datetime"]
            timeArray = date_time.split(' ')

            task_date = date(int(timeArray[2]), int(timeArray[0]), int(timeArray[1]))
            task_time = time(int(timeArray[3]), int(timeArray[4]))
            task_datetime = datetime.combine(task_date, task_time)

            # add task to task_dictionary
            task_dictionary[int(key)] = Task(int(key), dictionary[str(key)]["location"], task_datetime, dictionary[str(key)]["compensation"])


class Task:
    def __init__(self, id, location, datetime, compensation):
        self.id = id

        self.location = location
        self.datetime = datetime
        self.compensation = compensation
        self.tweetSent = False
        self.tweetID = 0
        self.tweetSentTime = 0
        self.assignedTo = ''
        self.taskSubmitted = False
        self.submissionPhotoLink = ''
        self.submissionTime = 0

    def toString(self):
        return 'Task ID: ' + str(self.id) + '\t Location: ' + self.location + '\t Due By: ' + self.datetime.strftime(
            "%B %d, %Y %I:%M%p") + '\t Compensation:' + str(self.compensation) + '\n'


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
            recipient = str(status_json['direct_message']['recipient_screen_name'])
            print '----------------------------------------------------------------'
            if(name != 'SnapNGo_2018'):
                print 'Message Received from: ' + name
            else:
                print 'Message Sent: '

            print 'Message Text: ' + text
            print 'Message Time: ' + time
            print '----------------------------------------------------------------'
            BotResponses.getResponse(text, name, time)
            writecsv(text, name, time, recipient)
        return True

    def on_error(self, status):
        print("Error:", status)

class BotResponses:

    @staticmethod
    def getResponse(text, name, time):
        text = text.lower()
        readTasks()
        # If the user is requesting a task, get the task ID and send them a message
        request_taskID = BotResponses.userRequestingTask(text)
        BotResponses.requestTask(text, name, time, request_taskID)

        # If the user is submitting a task, get the task ID and send them a message
        submit_taskID = BotResponses.userSubmittingTask(text)
        BotResponses.submitTask(text, name, time, submit_taskID)

    @staticmethod
    def requestTask(text, name, time, request_taskID):
        # try:
        if (request_taskID is not None): # check if the user gave a task ID
            # check if the task exists using the id
            if (not int(request_taskID) in task_dictionary.keys()):
                message = "Error 01: This Task ID is not valid. Please request an existing task."
            else:
                print 'User ' + name + ' is trying to request task #' + request_taskID
                assignee = task_dictionary[int(request_taskID)].assignedTo
                # If the task does not have an assignee
                if (assignee == ''):
                    task_dictionary[int(request_taskID)].assignedTo = name
                    accept_message = "Thank you, you have been assigned task #" + request_taskID
                    api.send_direct_message(screen_name = name, text = accept_message)
                    # api.destroy_status(id = )

                    message = "Task #" + str(request_taskID) + " details: Photo of " + str(task_dictionary[int(request_taskID)].location) + \
                    " by " + str(task_dictionary[int(request_taskID)].datetime.strftime(
                        "%B %d, %Y %I:%M%p")) + ". Compensation: " + str(task_dictionary[int(request_taskID)].compensation)
                # If the user has already requested the task
                elif (assignee == name):
                    message = "Error 02: You have already been assigned this task."
                # If a user tries to request a task already taken
                else:
                    message = "Error 03: This task is already assigned to someone else."
            api.send_direct_message(screen_name = name, text = message)
        # except:
        #     print "Program caught an error."

    @staticmethod
    def submitTask(text, name, time, submit_taskID):
        # try:
        if (submit_taskID is not None):
            now = datetime.now()
            print 'User ' + name + ' is submitting photo for task #' + submit_taskID
            # check if the task exists
            if (not int(submit_taskID) in task_dictionary.keys()):
                message = "Error 11: This Task ID is not valid. Please submit an existing task."
            # check if the task being submitted is assigned to someone else
            elif(task_dictionary[int(submit_taskID)].assignedTo != name):
                message = "Error 13: You have not been assigned this task."
            # If the task is submitted past the deadline
            elif (task_dictionary[int(submit_taskID)].datetime < now):
                message = "Error 14: You have missed the submission deadline."
            #If the task has already been submitted
            elif (task_dictionary[int(submit_taskID)].taskSubmitted):
                message = "Error 12: You have already submitted this task."
            # elif (not BotResponses.containsImage(text)):
            #     message = "Error 15: Picture is not attached. Please try again."
            else:
                # Mark the task as submitted and the submission time as now
                task_dictionary[int(submit_taskID)].submissionTime = now
                task_dictionary[int(submit_taskID)].taskSubmitted = True
                # Compensation: " + str(task_dictionary[int(submit_taskID)].compensation
                message = "Thank you for submitting Task #" + submit_taskID + ". You will be compensated once your submission is reviewed and accepted."
            print message
            api.send_direct_message(screen_name=name, text=message)
        # except:
        #     print "Program caught an error."

    @staticmethod
    def userRequestingTask(message):
        #print 'searching for regex'
        p = re.compile('request task (\d\d\d\d)')
        m = p.match(message)
        if m is None:
            #print 'did not find regex'
            return m
        else:
            #print 'found regex'
            return m.group(1)

    @staticmethod
    def userSubmittingTask(message):
        # print 'searching for regex'
        p = re.compile('submit task (\d\d\d\d)')
        m = p.match(message)
        if m is None:
            # print 'did not find regex'
            return m
        else:
            # print 'found regex'
            return m.group(1)

    @staticmethod
    def containsImage(message):
        # determine if a DM contains an contains an image
        try:
            url = message.split(' ', 1)[3]
            return True
        except IndexError:
            return False

def main():
    print('Welcome to Snap \'N\' Go!')

    auth = OAuthHandler(consumer_key, consumer_key_secret)
    auth.secure = True
    auth.set_access_token(access_token, access_token_secret)

    dmlistener = Stream(auth, DMListener())
    dmlistener.userstream()


if __name__ == '__main__':
    #when a follow request is received, follow them back and send a message.
    main()
