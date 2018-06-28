from tweepy import Stream
from tweepy import OAuthHandler
import tweepy
import json, math, re, csv, random
from tweepy.streaming import StreamListener
import time as t
from datetime import *
import numpy
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

# conn = pymysql.connect(host=host, user=user, password=password, db=db)
# curs = conn.cursor()
# curs.execute('')
# results = curs.fetchall()
host='rds-mysql-snapngo.cur5xo5rdve8.us-east-2.rds.amazonaws.com'
user='gpuzzle'
password='gpuzzle_snapngo'
db='snapngo_db'

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
        print("Type '3' to write tasks to a file")
        print("Type '4' to tweet tasks every hour")
        print("Type 'EXIT' to exit the program")
        action = raw_input('>')

        while (action != 'EXIT'):
            if (action == '1'):
                self.sendTweetsConfirm()
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

    def sendTweetsConfirm(self):
        send_tweet = raw_input(
            'Are you sure you would like to send tweets for tasks not already sent? Type Y for yes and N for no ')
        if (send_tweet == 'Y'):
            self.sendTweets()

    def sendTweets(self):
        tweets_sent = 0
        # for every newly created tweet
        for i in range(1000, self.task_ID):
            if (not tasks[i]["tweetSent"]):
                api.update_status(self.toString(i))
                tasks[i]["tweetSent"] = True
                tasks[i]["tweetSentTime"] = datetime.now()
                tweets_sent += 1

                # stagger the tweets by a random number of seconds
                seconds = random.randint(30,45)
                print "Wait time: " + str(seconds)
                t.sleep(seconds)
        print("Finished. " + str(tweets_sent) + "tweets were sent.")

    # Create tasks every hour and tweet them
    def scheduleTweets(self):
        # write tasks to file and then update tasks
        self.writeTasksToFile(file_name)
        self.sendTweetsConfirm() # send new tweets
        print "Sent tasks. Waiting " + str(time_interval) + " seconds."

        t.sleep(time_interval) # Wait before sending again

    # Creates tasks into a json file
    def writeTasksToFile(self, file_name):
        file = open(file_name, "w")
        data = {}
        # self.task_ID2 = self.task_ID # set the new lowest ID num to the current highest ID

        for i in range(num_tasks):
            location = self.createLocation()
            task_datetime = self.createDeadline()

            # adding task to data that will be put into json file
            data[self.task_ID] = {"location": str(location), "datetime": task_datetime, "compensation": '$1', "tweetSent": False,
            "tweetSentTime": 0, "assignedTo": '', "taskSubmitted": False, "submissionPhotoLink": '', "submissionTime": 0}
            tasks[self.task_ID] = data[self.task_ID] # add to dictionary
            self.task_ID = self.task_ID + 1 # increment the highest ID by one

        # add the data to json file, overwriting old data
        json.dump(data, file, indent=4)
        print "Created " + str(num_tasks) + " tasks"

    def createLocation(self):
        location_num = random.randint(1,num_vert) # create a random number
        print "location node: " + str(location_num)
        return vertices[int(location_num)] # get the name of that location

    def createDeadline(self):
        # get the time now and add an offset to make the deadline
        deadline = datetime.now() + timedelta(hours=offset)
        deadline = deadline.strftime('%m %d %Y %H %M')

        # format the deadline into a toString
        timeArray = deadline.split(' ')
        task_datetime = str(timeArray[0]) + " " + str(timeArray[1]) + " " + str(timeArray[2]) + " " + str(timeArray[3]) + " " + str(timeArray[4])
        return task_datetime

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
        s = ''
        print self.task_ID
        for i in range(1000, self.task_ID):
            s += (self.toString(i) + "\n")
        print('All Tasks:\n' + s)

    def toString(self, id):
        # format the datetime variable
        date_time = tasks[id]["datetime"]
        timeArray = date_time.split(' ')

        task_date = date(int(timeArray[2]), int(timeArray[0]), int(timeArray[1]))
        task_time = time(int(timeArray[3]), int(timeArray[4]))
        task_datetime = datetime.combine(task_date, task_time)

        return "Task: " + str(id) + ", Location: " + tasks[id]["location"] + ", Due By: " + task_datetime.strftime(
            "%B %d, %Y %I:%M%p") + ", Compensation: " + tasks[id]["compensation"]

def main():
    SnapNGo.readFile("Sci_Center_Map.txt")
    print('Welcome to Snap \'N\' Go!')

    auth = OAuthHandler(consumer_key, consumer_key_secret)
    auth.secure = True
    auth.set_access_token(access_token, access_token_secret)

    conn = pymysql.connect(host=host, user=user, password=password, db=db)
    curs = conn.cursor()
    curs.execute('select * from users')
    results = curs.fetchall()
    print results

    snap = SnapNGo()
    snap.selectAction()


if __name__ == '__main__':
    #when a follow request is received, follow them back and send a message.
    main()
