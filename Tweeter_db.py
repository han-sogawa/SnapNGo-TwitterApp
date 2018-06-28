from tweepy import Stream
from tweepy import OAuthHandler
import tweepy
import json, math, re, csv, random
from tweepy.streaming import StreamListener
import time as t
from datetime import *
import numpy
import pymysql
import functions

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

tasks = {}
file_name = "tasks.json"
num_tasks = 3 # num of tasks bot tweets at a time
offset = 8 # num of hours to complete task
time_interval = 60 # num of secs before bot tweets again

vertices = {}
num_vert = 0
graph = numpy.zeros(shape=(num_vert, num_vert))

class SnapNGo:
    def __init__(self):
        self.task_ID = 1000 # Highest ID in the batch of new tasks
        # self.task_ID2 = 1000 # Lowest ID in the batch of new tasks

    # Allows users to select from 4 different actions using the command
    # line. Actions include adding new tasks, tweeting unset tasks, printing
    # all tasks, and writing tasks to a file
    def selectAction(self):
        print("Type '1' to tweet unsent tasks")
        print("Type '2' to print all tasks")
        print("Type '3' to create tasks")
        print("Type '4' to tweet tasks every hour")
        print("Type 'EXIT' to exit the program")
        action = raw_input('>')

        while (action != 'EXIT'):
            if (action == '1'):
                self.sendTweetsConfirm()
            elif (action == '2'):
                self.printTasks()
            elif (action == '3'):
                self.createTasks()
            elif (action == '4'):
                while (True):
                    self.scheduleTweets()

            print("Type '1' to tweet unsent tasks")
            print("Type '2' to print all tasks")
            print("Type '3' to write tasks to a file")
            print("Type '4' to tweet tasks every hour")
            print("Type 'EXIT' to exit the program")
            action = raw_input('>')

    def sendTweetsConfirm(self):
        send_tweet = raw_input(
            'Are you sure you would like to send tweets for tasks not already sent? Type Y for yes and N for no ')
        if (send_tweet == 'Y'):
            self.sendTweets()

    def sendTweets(self):
        conn = pymysql.connect(host=host, user=user, password=password, db=db)
        tasks = functions.getUnsentTasks(conn)
        tweets_sent = len(tasks)

        # for every newly created tweet
        for task in tasks:
            status = api.update_status("Task: " + str(task['id']) + ", Location: " + str(task['location']) + ", Due By: " + str(task['deadline']) + ", Compensation: $" + str(task['compensation']))
            functions.markAsSent(conn, task["id"], datetime.now(), status.id)
            # stagger the tweets by a random number of seconds
            seconds = random.randint(30,45)
            print "Wait time: " + str(seconds)
            t.sleep(seconds)
        print("Finished. " + str(tweets_sent) + "tweets were sent.")
        conn.close()


    # Create tasks every hour and tweet them
    def scheduleTweets(self):
        # write tasks to file and then update tasks
        self.createTasks()
        self.sendTweetsConfirm() # send new tweets
        print "Sent tasks. Waiting " + str(time_interval) + " seconds."

        t.sleep(time_interval) # Wait before sending again

    # Creates tasks into a json file
    def createTasks(self):
        conn = pymysql.connect(host=host, user=user, password=password, db=db)
        for i in range(num_tasks):
            location = self.createLocation()
            deadline = datetime.now() + timedelta(hours=offset)
            compensation = 1.00
            functions.addTask(conn, location, deadline, compensation)
        print "Created " + str(num_tasks) + " tasks"
        conn.close()

    def createLocation(self):
        location_num = random.randint(1,num_vert) # create a random number
        print "location node: " + str(location_num)
        return vertices[int(location_num)] # get the name of that location

    @staticmethod
    def readFile(filename):
        global graph
        global num_vert
        with open(filename, "r") as f:
            num_vert = int(f.readline()) # the first line has the # of nodes
            content = f.readlines()

        graph = numpy.zeros(shape=(num_vert, num_vert)) # create the adjacency matrix
        count = 0 # temp variable used to skip over the first line in the file
        edges = False # variable to check if the "#" sign has been reached

        # for every line in the file
        for line in content:
            if (count == 0):
                count = count + 1
                continue # skip the first line

            v = line.split(' ', 1)[0]
            if v == "#\n": # check if we've reached the "#" sign
                edges = True
                continue
            if edges is False: # if we haven't reached the "#" sign
                name = line.split(' ', 1)[1]
                name = name.strip('\n')
                vertices[int(v)] = name # add the node
            else:
                edge = line.split(' ')
                # add the edge
                graph[int(edge[0]) - 1][int(edge[1]) - 1] = int(edge[2])

    def printTasks(self):
        conn = pymysql.connect(host=host, user=user, password=password, db=db)
        tasks = functions.getTasks(conn)
        for task in tasks:
            print "Task: " + str(task['id']) + ", Location: " + str(task['location']) + ", Due By: " + str(task['deadline']) + ", Compensation: $" + str(task['compensation'])
        conn.close()

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
