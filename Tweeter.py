from tweepy import Stream
from tweepy import OAuthHandler
import tweepy
import json, math, re, csv
from tweepy.streaming import StreamListener
import random
import time as t
from datetime import *
import numpy
import threading
import Listener

keys = json.load(open('keys.json'))
consumer_key = keys['consumer_key']
consumer_key_secret = keys['consumer_key_secret']
access_token = keys['access_token']
access_token_secret = keys['access_token_secret']
auth = OAuthHandler(consumer_key, consumer_key_secret)
auth.secure = True
auth.set_access_token(access_token, access_token_secret)
api = tweepy.API(auth_handler=auth)

dictionary = {}
vertices = {}
num_vert = 0
graph = numpy.zeros(shape=(num_vert, num_vert))

class SnapNGo:
    def __init__(self):
        self.task_ID = 1000
        self.task_ID2 = 1000

    # Allows users to select from 4 different actions using the command
    # line. Actions include adding new tasks, tweeting unset tasks, printing
    # all tasks, and writing tasks to a file
    def selectAction(self):
        print("Type '1' to tweet unsent tasks")
        print("Type '2' to print all tasks")
        print("Type '3' to write tasks to a file")
        print("Type '4' to tweet tasks every hour")
        print("Type 'EXIT' to exit the program")
        action = raw_input('>')

        while (action != 'EXIT'):
            if (action == '1'):
                self.sendUnsentTweets()
            elif (action == '2'):
                self.printTasks()
            elif (action == '3'):
                print('Write the name of the file to write tasks to:')
                file_name = raw_input('>>')
                self.writeTasksToFile(file_name)
            elif (action == '4'):
                while (True):
                    self.scheduleTweets()

            print("Type '1' to tweet unsent tasks")
            print("Type '2' to print all tasks")
            print("Type '3' to write tasks to a file")
            print("Type '4' to tweet tasks every hour")
            print("Type 'EXIT' to exit the program")
            action = raw_input('>')

    def sendUnsentTweets(self):
        # dictionary = json.load(open('tasks.json'))
        send_tweet = raw_input(
            'Are you sure you would like to send tweets for tasks not already sent? Type Y for yes and N for no ')
        tweets_sent = 0
        if (send_tweet == 'Y'):
            for i in range(self.task_ID2, self.task_ID):
                if (not dictionary[str(i)]["tweetSent"]):
                    api.update_status(self.toString(i))
                    dictionary[str(i)]["tweetSent"] = True
                    dictionary[str(i)]["tweetSentTime"] = datetime.now()
                    tweets_sent += 1
                    # stagger the tweets by a random number of seconds
                    seconds = random.randint(30,45)
                    print "Wait time: " + str(seconds)
                    t.sleep(seconds)

        print("Finished. " + str(tweets_sent) + "tweets were sent.")

    #Tweet created tasks every hour
    def scheduleTweets(self):
        global dictionary
        self.writeTasksToFile("tasks.json")
        # Listener.readFile()
        dictionary = json.load(open('tasks.json'))

        self.sendUnsentTweets()
        print "Sent tasks. Waiting one hour"
        t.sleep(3600)

    # randomly create 5 tasks into a file
    def writeTasksToFile(self, file_name):
        file = open(file_name, "w")
        self.task_ID2 = self.task_ID
        data = {}
        for i in range(3):
            location_num = random.randint(1,num_vert)
            location = vertices[int(location_num)]
            now = datetime.now().strftime('%m %d %Y %H %M')
            timeArray = now.split(' ')

            hour = int(timeArray[3])
            minute = int(timeArray[4])

            offset = 8
            if (hour < 24 - offset):
                hour = hour + offset
            else:
                hour = 23
                minute = 59

            task_datetime = str(timeArray[0]) + " " + str(timeArray[1]) + " " + str(timeArray[2]) + " " + str(hour) + " " + str(minute)
            # writing to a text file
            # file.write(str(id) + ", " +  str(location) + ", " + str(time[0]) + ", " +
            #     str(time[1]) + ", " + str(time[2]) + ", " + str(hour) + ", " +
            #     str(time[4]) + ", $1\n")

            # adding a string to json
            data[self.task_ID] = {"location": str(location), "datetime": task_datetime, "compensation": '$1', "tweetSent": False,
            "tweetSentTime": 0, "assignedTo": '', "taskSubmitted": False, "submissionPhotoLink": '', "submissionTime": 0}

            self.task_ID = self.task_ID + 1

        json.dump(data, file, indent=4)
        print "Randomly created tasks"

    @staticmethod
    def readFile(filename):
        global graph
        global num_vert

        with open(filename, "r") as f:
            num_vert = int(f.readline())
            content = f.readlines()

        graph = numpy.zeros(shape=(num_vert, num_vert))

        count = 0
        edges = False
        for line in content:
            if (count == 0):
                count = count + 1
                continue
            v = line.split(' ', 1)[0]
            if v == "#\n":
                edges = True
                continue
            if edges is False:
                name = line.split(' ', 1)[1]
                name = name.strip('\n')
                vertices[int(v)] = name
            else:
                edge = line.split(' ')
                graph[int(edge[0]) - 1][int(edge[1]) - 1] = int(edge[2])

    def printTasks(self):
        #  = json.load(open('tasks.json'))
        s = ''
        print self.task_ID
        for i in range(self.task_ID2, self.task_ID):
            s += dictionary[self.toString(i)]
        print('All Tasks:\n' + s)

    def toString(self, id):
        # dictionary = json.load(open('tasks.json'))
        id = str(id)
        date_time = dictionary[id]["datetime"]
        timeArray = date_time.split(' ')

        task_date = date(int(timeArray[2]), int(timeArray[0]), int(timeArray[1]))
        task_time = time(int(timeArray[3]), int(timeArray[4]))
        task_datetime = datetime.combine(task_date, task_time)

        return "Task: " + id + ", Location: " + dictionary[id]["location"] + ", Due By: " + task_datetime.strftime(
            "%B %d, %Y %I:%M%p") + ", Compensation: " + dictionary[id]["compensation"]

def main():
    SnapNGo.readFile("Sci_Center_Map.txt")
    print('Welcome to Snap \'N\' Go!')
    
    auth = OAuthHandler(consumer_key, consumer_key_secret)
    auth.secure = True
    auth.set_access_token(access_token, access_token_secret)

    snap = SnapNGo()
    snap.selectAction()


if __name__ == '__main__':
    #when a follow request is received, follow them back and send a message.
    main()
