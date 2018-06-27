from tweepy import Stream
from tweepy import OAuthHandler
import tweepy
import json, math, re, csv
from tweepy.streaming import StreamListener
import random
import time as t
from datetime import *
from multiprocessing import Pool
import numpy
import threading

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
vertices = {}
num_vert = 19
graph = numpy.zeros(shape=(num_vert, num_vert))


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
        return 'Task ID: ' + str(self.id) + '\t Location: ' + self.location + '\t Due By: ' + self.datetime.strftime(
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

    def sendTaskTweet(self):
        if (not self.tweetSent):
            api.update_status(self.toString())
            self.tweetSent = True
            self.tweetSentTime = datetime.now()

    def getFileRow(self):
        return [self.id, self.location, self.datetime.strftime("%B %d, %Y %I:%M%p"), self.compensation, self.tweetSent,
                self.tweetSentTime, self.assignedTo, self.taskSubmitted, self.submissionPhotoLink, self.submissionTime]


class SnapNGo:
    def __init__(self):
        self.task_ID = 1000

    # Allows users to select from 4 different actions using the command
    # line. Actions include adding new tasks, tweeting unset tasks, printing
    # all tasks, and writing tasks to a file
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
                elif (enter_tasks == '2'):
                    print('Type the name of the file')
                    file_name = raw_input('>>>')
                    self.addTasksViaFile(file_name)
            elif (action == '2'):
                self.sendUnsentTweets()
            elif (action == '3'):
                self.printTasks()
            elif (action == '4'):
                print('Write the name of the file to write tasks to:')
                file_name = raw_input('>>')
                self.writeTasksToFile(file_name)

            print("Type '1' to add new tasks")
            print("Type '2' to tweet unsent tasks")
            print("Type '3' to print all tasks")
            print("Type '4' to write tasks to a file")
            print("Type 'EXIT' to exit the program")
            action = raw_input('>')


    def addTasksViaCommandLine(self):
        input = raw_input('Please enter a task in the following format: location, month, day, year, hour, minutes, compensation\n>')
        while (input != 'end'):
            # check to see if input has correct length and is otherwise correct format
            input_array = re.sub(r'\s', '', input).split(',')
            task_date = date(int(input_array[3]), int(input_array[1]), int(input_array[2]))
            task_time = time(int(input_array[4]), int(input_array[5]))
            task_datetime = datetime.combine(task_date, task_time)

            # add the task to the dictionary
            task_dictionary[self.task_ID] = Task(self.task_ID, input_array[0], task_datetime, input_array[6])

            print('New task created: ' + task_dictionary[self.task_ID].toString())
            print('Add another task, or type end to finish')
            self.task_ID += 1
            input = raw_input('>')

        print 'All tasks: \n'
        self.printTasks()

    def addTasksViaFile(self, file_name):
        # read from a file
        with open(file_name, "r") as f:
            content = f.readlines()

        # for every line in the file
        for line in content:
            input_array = line.split(',')
            task_date = date(int(input_array[3]), int(input_array[1]), int(input_array[2]))
            task_time = time(int(input_array[4]), int(input_array[5]))
            task_datetime = datetime.combine(task_date, task_time)

            # add the task to the dictionary
            task_dictionary[self.task_ID] = Task(self.task_ID, input_array[0], task_datetime, input_array[6])
            print('New task created: ' + task_dictionary[self.task_ID].toString())
            self.task_ID += 1

        print 'All tasks: \n'
        self.printTasks()

    def sendUnsentTweets(self):
        send_tweet = raw_input(
            'Are you sure you would like to send tweets for tasks not already sent? Type Y for yes and N for no ')
        tweets_sent = 0
        if (send_tweet == 'Y'):
            for i in range(1000, self.task_ID):
                if (not task_dictionary[i].tweetSent):
                    task_dictionary[i].sendTaskTweet()
                    tweets_sent += 1
                    # stagger the tweets by a random number of seconds
                    seconds = random.randint(30,45)
                    print "Wait time: " + str(seconds)
                    t.sleep(seconds)

        print("Finished. " + str(tweets_sent) + "tweets were sent.")

    # randomly create 5 tasks into a file
    def writeTasksToFile(self, file_name):
        file = open(file_name, "w")
        data = {}
        id = 1000
        for i in range(5):
            location_num = random.randint(1,19)
            location = vertices[int(location_num)]
            now = datetime.now().strftime('%m %d %Y %H %M')
            time = []
            for unit in now.split(' '):
                time.append(int(unit))

            hour = time[3]
            offset = 8
            if (hour <= 24 - offset):
                hour = hour + offset
            else:
                hour = offset - (24 - hour)

            # file.write(str(id) + ", " +  str(location) + ", " + str(time[0]) + ", " +
            #     str(time[1]) + ", " + str(time[2]) + ", " + str(hour) + ", " +
            #     str(time[4]) + ", $1\n")


            data[id] = str(id) + ", " +  str(location) + ", " + str(time[0]) + ", " + str(time[1]) + ", " + str(time[2]) + ", " + str(hour) + ", " + str(time[4]) + ", $1"
            id = id + 1

        json.dump(data, file)
        print "Randomly created 5 tasks"

    @staticmethod
    def writecsv(text, name, time, recipient):
        with open('data.csv', 'a') as csvfile:
            writer = csv.writer(csvfile, delimiter=',')
            writer.writerow([text, name, time, recipient])

    @staticmethod
    def readFile(filename):
        with open(filename, "r") as f:
            content = f.readlines()

        edges = False
        for line in content:
            v = line.split(' ', 1)[0]
            if v == "#\n":
                edges = True
                continue
            if edges is False:
                name = line.split(' ', 1)[1]
                name = name.strip('\n')
                vertices[int(v)] = name
            else:
                edge = []
                for num in line.split(' '):
                    num = num.strip('\n')
                    edge.append(int(num))
                graph[edge[0] - 1][edge[1] - 1] = edge[2]

    def printTasks(self):
        s = ''
        print self.task_ID
        for i in range(1000, self.task_ID):
            s += task_dictionary[i].toString()
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
            SnapNGo.writecsv(text, name, time, recipient)
        return True

    def on_error(self, status):
        print("Error:", status)

class BotResponses:

    @staticmethod
    def getResponse(text, name, time):
        text = text.lower()
        #if the user is requesting a task, get the task ID and send them a message
        request_taskID = BotResponses.userRequestingTask(text)
        BotResponses.requestTask(text, name, time, request_taskID)
        #if the user is submitting a task, get the task ID and send them a message
        submit_taskID = BotResponses.userSubmittingTask(text)
        BotResponses.submitTask(text, name, time, submit_taskID)

    @staticmethod
    def requestTask(text, name, time, request_taskID):
        try:
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
        except:
            print "Program caught an error."

    @staticmethod
    def submitTask(text, name, time, submit_taskID):
        try:
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
        except:
            print "Program caught an error."

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
    SnapNGo.readFile("Wellesley_Outdoor_Map.txt")
    print('Welcome to Snap \'N\' Go!')

    auth = OAuthHandler(consumer_key, consumer_key_secret)
    auth.secure = True
    auth.set_access_token(access_token, access_token_secret)

    dmlistener = Stream(auth, DMListener())
    # dmlistener.userstream()

    snap = SnapNGo()
    # snap.selectAction()

    # creating thread
    t1 = threading.Thread(target=snap.selectAction())
    t2 = threading.Thread(target=dmlistener.userstream())

    # starting thread 1
    t1.start()
    # starting thread 2
    t2.start()

    # wait until thread 1 is completely executed
    t1.join()
    # wait until thread 2 is completely executed
    t2.join()


if __name__ == '__main__':
    #when a follow request is received, follow them back and send a message.
    main()
