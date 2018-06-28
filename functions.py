import pymysql

def addTask(conn, location, deadline, compensation):
    curs = conn.cursor(pymysql.cursors.DictCursor)
    curs.execute('INSERT into tasks (location, deadline, compensation) values (%s, %s, %s)', [location, deadline, compensation])
    curs.close()
    conn.commit()

def getUnsentTasks(conn):
    curs = conn.cursor(pymysql.cursors.DictCursor)
    curs.execute('SELECT id, location, deadline, compensation from tasks where tweetSent = false')
    tasks = curs.fetchall()
    curs.close()
    return tasks

def getTasks(conn):
    curs = conn.cursor(pymysql.cursors.DictCursor)
    curs.execute('SELECT id, location, deadline, compensation from tasks')
    tasks = curs.fetchall()
    curs.close()
    return tasks

def markAsSent(conn, task_id, now, status_id):
    curs = conn.cursor(pymysql.cursors.DictCursor)
    curs.execute('UPDATE tasks SET tweetSent = 1, tweetSentTime= %s, tweetID = %s WHERE id = %s', [now, status_id, task_id])
    curs.close()
    conn.commit()

def getTaskByID(conn, id):
    curs = conn.cursor(pymysql.cursors.DictCursor)
    curs.execute('SELECT * from tasks WHERE id = %s', [id])
    task = curs.fetchone()
    curs.close()
    return task

def updateAsignee(conn, user_id, task_id):
    curs = conn.cursor(pymysql.cursors.DictCursor)
    curs.execute('UPDATE tasks SET assignedTo = %s WHERE id = %s', [user_id, task_id])
    curs.close()
    conn.commit()

def getUserByID(conn, user_id):
    curs = conn.cursor(pymysql.cursors.DictCursor)
    curs.execute('SELECT * from users WHERE id = %s', [user_id])
    user = curs.fetchone()
    curs.close()
    return user

def addUser(conn, username, user_id):
    curs = conn.cursor(pymysql.cursors.DictCursor)
    curs.execute('INSERT INTO users (id, name) values (%s, %s)', [user_id, username])
    curs.close()
    conn.commit()

def markAsSubmitted(conn, time, id):
    #Add photo link at some point
    curs = conn.cursor(pymysql.cursors.DictCursor)
    curs.execute('UPDATE tasks SET taskSubmitted = 1, submissionTime = %s where id = %s', [time, id])
    curs.close()
    conn.commit()
