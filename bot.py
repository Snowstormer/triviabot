#!/usr/bin/python
# -*- coding: utf-8 -*-

import socket, sys, time, random, json, re, operator, os
reload(sys)
sys.setdefaultencoding("utf-8")

def privmsg(to, msg):
    irc.send("PRIVMSG %s :%s\r\n" % (to, msg))

#settings
server = None
port = None
botnick = None
password = None
account = None
channel = None
admins = None
prefix = None
topics = None
realname = "Triviabot"

if os.path.isfile("config.json"):
    settingsfile = open("config.json")
    settingsjson = json.load(settingsfile)
    settingsfile.close()

    try:
        server = settingsjson["server"]
        port = settingsjson["port"]
        botnick = settingsjson["nickname"]
        password = settingsjson["password"]
        if settingsjson["account"] != "":
            account = settingsjson["account"]
        else:
            account = botnick
        channel = settingsjson["channel"]
        admins = settingsjson["admins"]    
        channel = settingsjson["channel"]
        admins = settingsjson["admins"]
        prefix = settingsjson["prefix"]

        topics = settingsjson["enabledtopics"]
        topics.sort()
    except Exception:
        print "Error: There is something wrong with your config, check it."
        sys.exit()
else:
    print "Error: Config file does not exist, did you rename config.json.example to config.json?"
    sys.exit()

##Basic global variables
points = {}
started = False
answer = ""
triviatopic = None
number = 1
start = None
end = None
old_question = None

#connect
irc = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
print "Connecting to: %s:%s" % (server, str(port))
irc.connect((server, port))
irc.send("USER %s %s %s :%s\n" % (botnick, botnick, botnick, realname))
irc.send("NICK %s\n" % botnick)
if password != "":
    irc.send("PRIVMSG NickServ :id %s %s\r\n" % (account, password))
irc.send("JOIN %s\n" % channel)

#body
readbuffer = ''
while 1:
    text = irc.recv(2040)
    print text
    sender = text.split(" ")[0].split("!")[0].strip(":")
    sendchan = text.split(" ")
    try:
        sendchannel = sendchan[2]
    except Exception:
        pass
    sendto = sendchannel

    if text.find('PING') != -1:
        irc.send('PONG\r\n')

    if text.find("PRIVMSG") != -1:
        message = text.split(":", 2)[2].strip()
        if message.lower().startswith(prefix+"start"):
            try:
                triviatopic = message.split(" ", 1)[1].strip()
                if triviatopic in topics:
                    topicmsg = "Topic chosen: %s." % triviatopic
                else:
                    triviatopic = random.choice(topics)
                    topicmsg = "Topic chosen randomly: %s." % triviatopic
            except Exception:
                triviatopic = random.choice(topics)
                topicmsg = "Topic chosen randomly: %s." % triviatopic

            if started == False:
                privmsg(sendto, "Welcome to trivia!")
                privmsg(sendto, topicmsg)
                time.sleep(1)
                started = True
            else:
                privmsg(sendto, "%s: Trivia is already in session, type %sstop to stop." % (sender, prefix))
        elif message.lower().startswith(prefix+"topic") and message.lower() != prefix+"topics":
            if started == True:
                try:
                    testtopic = message.split(" ", 1)[1].strip()
                    if testtopic in topics:
                        triviatopic = testtopic
                        privmsg(sendto, "New topic: %s." % triviatopic)
                        number -= 1
                        answer = ""
                    else:
                        privmsg(sendto, "%s: That doesn't look like a valid topic to me, type %stopics to see all available topics!" % (sender, prefix))
                except Exception:
                    privmsg(sendto, "%s: That doesn't look like a valid topic to me, type %stopics to see all available topics!" % (sender, prefix))
            else:
                privmsg(sendto, "%s: Trivia is not in session, type %sstart to start." % (sender, prefix))
        elif message.lower() == prefix+"topics":
            privmsg(sendto, "All available topics: "+", ".join(topics))
        elif message.lower() in answer:
            if answer != "":
                end = time.time()
                timeelapsed = round(end - start, 2)
                if timeelapsed <= 2.0:
                    pointamount = 5
                elif timeelapsed <= 3.0:
                    pointamount = 3
                elif timeelapsed <= 5.0:
                    pointamount = 2
                else:
                    pointamount = 1
                privmsg(sendto, "%s is correct, %s gains 03%s point%s! (answered in %ss)" % (message.title(), sender, str(pointamount), "" if pointamount == 1 else 's', str(timeelapsed)))
                if sender in points:
                    points[sender] += pointamount
                else:
                    points[sender] = pointamount
                time.sleep(1)
                answer = ""
        elif message.lower() == prefix+"skip":
            if answer != "":
                if started == True:
                    if sender in admins:
                        end = time.time()
                        timeelapsed = str(round(end - start, 2))
                        privmsg(sendto, "%s skipped the question! (skipped after %ss)" % (sender, timeelapsed))
                        time.sleep(1)
                        answer = ""
                    else:
                        if sender in points:
                            if points[sender] >= 5:
                                end = time.time()
                                timeelapsed = round(end - start, 2)
                                if timeelapsed <= 2.0:
                                    pointamount = 5
                                elif timeelapsed <= 5.0:
                                    pointamount = 3
                                elif timeelapsed <= 10.0:
                                    pointamount = 2
                                else:
                                    pointamount = 1
                                privmsg(sendto, "%s skipped the question, they lose 04%s point%s! (skipped after %ss)" % (sender, str(pointamount), "" if pointamount == 1 else 's', str(timeelapsed)))
                                points[sender] -= pointamount
                                if points[sender] == 0:
                                    privmsg(sendto, "%s: Please note, you have no points left, you cannot skip more questions until you gain more." % sender)
                                elif points[sender] < 5:
                                    privmsg(sendto, "%s: Please note, you have less than 5 points left, you cannot skip more questions until you gain more." % sender)
                                time.sleep(1)
                                answer = ""
                            else:
                                privmsg(sendto, "%s: You need at least 5 points to skip a question, you have %s." % (sender, str(points[sender])))
                        else:
                            privmsg(sendto, "%s: You have not answered a single question yet, you need at least 5 points to skip a question." % sender)
                else:
                    privmsg(sendto, "%s: Trivia is not in session, type %sstart to start." % (sender, prefix))
        elif message.lower() == prefix+"stop":
            if started == True:
                answer = ""
                number = 1
                points = {}
                triviatopic = None
                started = False
                privmsg(sendto, "Trivia session ended! Type %sstart to start again!" % prefix)
            else:
                privmsg(sendto, "%s: Trivia is not in session, type %sstart to start." % (sender, prefix))
        elif message.lower() == prefix+"quit":
            if sender in admins:
                if started != True:
                    irc.send('QUIT :Requested by %s.\n' % sender)
                    sys.exit()
                else:
                    privmsg(sendto, "%s: Cannot quit while trivia is in session, please type %sstop and then try again." % (sender, prefix))
            else:
                privmsg(sendto, "%s: You do not have the permission to do this." % sender)
        elif message.lower() == prefix+"points":
            if started == True:
                if not points:
                    privmsg(sendto, "%s: No one has scored a point yet, you can be the first by answering a question!" % sender)
                else:
                    pointlist = []
                    for pointkey in points:
                        pointlist.append(str(pointkey)+": "+str(points[pointkey]))
                    privmsg(sendto, sender+": "+", ".join(pointlist))
            else:
                privmsg(sendto, "%s: Trivia is not in session, type %sstart to start." % (sender, prefix))

    while answer == "" and started == True and triviatopic != None:
        if triviatopic != "all":
            topicjson = open("topics/"+triviatopic+".json")
        else:
            alltopics = topics[:]
            alltopics.remove("all")
            topicjson = open("topics/"+random.choice(alltopics)+".json")
        questions = json.load(topicjson)
        topicjson.close()
        question = random.choice(questions.keys())
        if old_question != question:
            old_question = question
        else:
            question = random.choice(questions.keys())
        answer = questions[question]
        privmsg(sendto, "Question %s: %s" % (number, question))
        start = time.time()
        number += 1
