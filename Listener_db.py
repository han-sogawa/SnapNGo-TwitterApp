from tweepy import Stream
from tweepy import OAuthHandler
import tweepy
import json, math, re, csv, random
from tweepy.streaming import StreamListener
import time as t
from datetime import *
import functions
import pymysql

keys = json.load(open('keys.json'))
consumer_key = keys['consumer_key']
consumer_key_secret = keys['consumer_key_secret']
access_token = keys['access_token']
access_token_secret = keys['access_token_secret']
auth = OAuthHandler(consumer_key, consumer_key_secret)
auth.secure = True
auth.set_access_token(access_token, access_token_secret)
api = tweepy.API(auth_handler=auth)

auth = json.load(open('auth.json'))
host=auth['host']
user=auth['user']
password=auth['password']
db=auth['db']

def writecsv(text, name, time, recipient):
    with open('data.csv', 'a') as csvfile:
        writer = csv.writer(csvfile, delimiter=',')
        writer.writerow([text, name, time, recipient])

class DMListener(StreamListener):

    def on_connect(self):
        print("Stream Connected")

    def on_disconnect(self, notice):
        print("Stream Connection Lost:", notice)

    def on_data(self, status):
        now = datetime.now()
        status_json = json.loads(status)
        print(status)
        if 'direct_message' in status_json:
            name = str(status_json['direct_message']['sender']['screen_name'])
            id = status_json['direct_message']['sender']['id_str']
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
            BotResponses.getResponse(text, name, now, id)
            writecsv(text, name, time, recipient)
        return True

    def on_error(self, status):
        print("Error:", status)

class BotResponses:

    @staticmethod
    def getResponse(text, name, time, user_id):
        conn = pymysql.connect(host=host, user=user, password=password, db=db)
        person = functions.getUserByID(conn, user_id)
        if (person is None):
            functions.addUser(conn, name, user_id)
        text = text.lower()

        # If the user is requesting a task, get the task ID and send them a message
        request_taskID = BotResponses.userRequestingTask(text)
        BotResponses.requestTask(text, name, time, request_taskID, user_id)

        # If the user is submitting a task, get the task ID and send them a message
        submit_taskID = BotResponses.userSubmittingTask(text)
        BotResponses.submitTask(text, name, time, submit_taskID, user_id)

    @staticmethod
    def requestTask(text, name, time, request_taskID, user_id):
        # try:
        if (request_taskID is not None): # check if the user gave a task ID
            # check if the task exists using the id
            conn = pymysql.connect(host=host, user=user, password=password, db=db)
            task = functions.getTaskByID(conn, request_taskID)
            if (task is None):
                message = "Error 01: This Task ID is not valid. Please request an existing task."
            else:
                assignee = task['assignedTo']
                # If the task does not have an assignee
                if (assignee is None):
                    functions.updateAsignee(conn, user_id, request_taskID)
                    accept_message = "Thank you, you have been assigned task #" + str(request_taskID)
                    api.send_direct_message(screen_name = name, text = accept_message)
                    api.destroy_status(id=int(task['tweetID']))

                    message = "Task #" + str(request_taskID) + " details: Photo of " + str(task['location']) + \
                    " by " + task['deadline'].strftime(
                        "%B %d, %Y %I:%M%p") + ". Compensation: $" + str(task['compensation'])
                # If the user has already requested the task
                elif (assignee == user_id):
                    message = "Error 02: You have already been assigned this task."
                # If a user tries to request a task already taken
                else:
                    message = "Error 03: This task is already assigned to someone else."
            api.send_direct_message(screen_name = name, text = message)
        # except:
        #     print "Program caught an error."
        conn.close()

    @staticmethod
    def submitTask(text, name, time, submit_taskID, user_id):
        # try:
        if (submit_taskID is not None):
            conn = pymysql.connect(host=host, user=user, password=password, db=db)
            task = functions.getTaskByID(conn, submit_taskID)

            print 'User ' + name + ' is submitting photo for task #' + str(submit_taskID)
            # check if the task exists
            if (task is None):
                message = "Error 11: This Task ID is not valid. Please submit an existing task."
            # check if the task being submitted is assigned to someone else
            elif(task['assignedTo'] != user_id):
                message = "Error 13: You have not been assigned this task."
            # If the task is submitted past the deadline
            elif (task['deadline'] < time):
                message = "Error 14: You have missed the submission deadline."
            #If the task has already been submitted
            elif (task['taskSubmitted'] == 0):
                message = "Error 12: You have already submitted this task."
            # elif (not BotResponses.containsImage(text)):
            #     message = "Error 15: Picture is not attached. Please try again."
            else:
                # Mark the task as submitted and the submission time as now
                functions.markAsSubmitted(conn, time, submit_taskID)
                # Compensation: " + str(task_dictionary[int(submit_taskID)].compensation
                message = "Thank you for submitting Task #" + str(submit_taskID) + ". You will be compensated once your submission is reviewed and accepted."
            print message
            api.send_direct_message(screen_name=name, text=message)
        # except:
        #     print "Program caught an error."
        conn.close()

    @staticmethod
    def userRequestingTask(message):
        message = message.split(' ')
        action = message[0]
        isTask = message[1]
        task_ID = message[2]

        if action == "request" and isTask == "task":
            try:
                task_ID = int(task_ID)
            except ValueError:
                pass
            return task_ID
        return None

    @staticmethod
    def userSubmittingTask(message):
        message = message.split(' ')
        action = message[0]
        isTask = message[1]
        task_ID = message[2]

        if action == "submit" and isTask == "task":
            try:
                task_ID = int(task_ID)
            except ValueError:
                pass
            return task_ID
        return None

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
