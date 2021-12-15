#!/usr/bin/python
# -*- coding: utf-8 -*-
# Trivia bot basado en el codigo de https://github.com/catskittens/triviabot
# se tradujo todo texto que se imprime a castellano
# asi como el comando propio del bot !topic por !tema ya que coincidia
# con el comando irc de la sala y se cambiaba dicho topic si era ejecutado como moderador

import socket, sys, time, random, json, re, operator, os, re
reload(sys)
sys.setdefaultencoding("utf-8")

def privmsg(to, msg):
    irc.send("PRIVMSG %s :%s\r\n" % (to, msg))

def addhelp(prefix, s):
    return prefix + s

# se agrega funcion de eliminacion de codigos de formato
# de texto de irc como colores, negrita, italica, etc
def strip_colours(s):
    ccodes = ["\x0F", "\x16", "\x1D", "\x1F", "\x02",
        "\x03([1-9][0-6]?)?,?([1-9][0-6]?)?"]
    for cc in ccodes:
        s = re.sub(cc, "", s)
    return s

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
realname = "Bot de Trivia en castellano"
savepoints = None

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
        savepoints = settingsjson["savepoints"]

        topics = settingsjson["enabledtopics"]
        topics.sort()
    except Exception:
        print "Error: There is something wrong with your config, please make sure all fields match the example config in the readme."
        sys.exit()
else:
    print "Error: Config file does not exist, did you rename config.example.json to config.json?"
    sys.exit()

##Basic global variables
if savepoints == True:
    if os.path.isfile("points.json"):
        pointsfile = open('points.json')
        points = json.load(pointsfile)
        pointsfile.close()
    else:
        pointsfile = open('points.json', 'w+')
        pointsfile.write(json.dumps({}))
        pointsfile.close()
        points = {}
else:
    points = {}
started = False
question = None
answer = ""
triviatopic = None
number = 1
start = None
end = None
randomtopic = False

#connect
irc = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
print "Connecting to: %s:%s" % (server, str(port))
irc.connect((server, port))
# se agrega una pausa porque si los mensajes de login y pass son muy rapidos
# el server no los reconoce y jamas se puede hacer el join posterior a la sala!
time.sleep(2)
irc.send("USER %s %s %s :%s\n" % (botnick, botnick, botnick, realname))
time.sleep(2)
irc.send("NICK %s\n" % botnick)
if password != "":
    irc.send("PRIVMSG NickServ :identify %s %s\r\n" % (account, password))
	#irc.send("/msg NickServ identify %s \r\n" % (password))
    #una pausa mas para dar tiempo al server y no saturarlo en el login y el join
    time.sleep(2)
irc.send("JOIN %s\n" % channel)
time.sleep(2)

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
    # se mantiene conectividad al server respondiendo
    # el mensaje de ping-pong segun la RFC
    if text.find('PING') != -1:
        irc.send('PONG\r\n')

    if text.find("PRIVMSG") != -1:
        message = text.split(":", 2)[2].strip()
        if message.lower().startswith(prefix+"start"):
            try:
                triviatopic = message.split(" ")[1].strip()
                if triviatopic in topics:
                    topicmsg = "Tema elegido: %s." % triviatopic
                else:
                    triviatopic = random.choice(topics)
                    topicmsg = "Tema al azar: %s." % triviatopic
                    randomtopic = True
            except Exception:
                triviatopic = random.choice(topics)
                topicmsg = "Tema al azar: %s." % triviatopic
                randomtopic = True

            if started == False:
                privmsg(sendto, "Bienvenidos a la trivia!")
		privmsg(sendto, "Podes enviar nuevas preguntas a trivia40plus@gmail.com")
		privmsg(sendto, "indicando Autor, Tema, Pregunta y Respuesta")
		time.sleep(2)
                privmsg(sendto, topicmsg)
                time.sleep(1)
                started = True
            else:
                privmsg(sendto, "%s: la Trivia esta activa, tipea %sstop para detenerla." % (sender, prefix))
        elif message.lower().startswith(prefix+"tema") and message.lower() != prefix+"temas":
            if started == True:
                if sender in admins or randomtopic == True:
                    try:
                        testtopic = message.split(" ")[1].strip()
                        if testtopic in topics:
                            if testtopic != triviatopic:
                                triviatopic = testtopic
                                privmsg(sendto, "Nuevo tema: %s." % triviatopic)
                                randomtopic = False
                                number -= 1
                                answer = ""
                            else:
                                privmsg(sendto, "%s: %s ya es el tema actual, proba otro. Escribi %stemas para ver los temas disponibles!" % (sender, triviatopic, prefix))
                        else:
                            privmsg(sendto, "%s: no parece ser un tema valido, tipea %stemas para ver los temas disponibles!" % (sender, prefix))
                    except Exception:
                        privmsg(sendto, "%s: no parece ser un tema valido, tipea %stemas para ver los temas disponibles!" % (sender, prefix))
                else:
                    if sender in points and randomtopic != True:
                        if points[sender] > 5:
                            try:
                                testtopic = message.split(" ")[1].strip()
                                if testtopic in topics:
                                    if testtopic != triviatopic:
                                        triviatopic = testtopic
                                        privmsg(sendto, "Nuevo tema: %s." % triviatopic)
                                        number -= 1
                                        answer = ""
                                    else:
                                        privmsg(sendto, "%s: %s ya es el tema actual, prueba uno nuevo. Tipea %stemas para ver los temas disponibles!" % (sender, triviatopic, prefix))
                                else:
                                    privmsg(sendto, "%s: no parece ser un tema valido, tipea %stemas para ver los temas disponibles!" % (sender, prefix))
                            except Exception:
                                privmsg(sendto, "%s: no parece ser un tema valido, tipea %stemas para ver los temas disponibles!" % (sender, prefix))
                        else:
                            privmsg(sendto, "%s: Necesitas tener al menos 5 puntos para cambiar de tema, tenes %s." % (sender, str(points[sender])))
                    else:
                        privmsg(sendto, "%s: No respondide ni 1 pregunta todavia, necesitas al menos 5 puntos para cambiar de tema." % sender)
            else:
                privmsg(sendto, "%s: Trivia no iniciada, tipea %sstart para comenzar." % (sender, prefix))
        elif message.lower() == prefix+"temas":
            privmsg(sendto, "Temas disponibles: "+", ".join(topics))
	# se trata de quitar codigos de formateo de texto de respuestas
	# ej colores, bold, italica, underline, etc para cotejar con respuesta almacenada
        elif strip_colours(message.lower()) in [i.lower() for i in answer]:
            if answer != "":
                end = time.time()
                timeelapsed = round(end - start, 2)
                if timeelapsed <= 2.0:
                    pointamount = 5
                elif timeelapsed <= 4.0:
                    pointamount = 3
                elif timeelapsed <= 8.0:
                    pointamount = 2
                else:
                    pointamount = 1
		# se agrega codigo de color y texto camuflado http para
		# lograr que salgan todos los numeros ya que el server
		# dalechatea filtra cuando hay varios nros en un string!
                privmsg(sendto, "\x033,3http\x03%s es correcto!, %s gana 03%s punto%s! (respondida en %ss)\x033,3http\x03" % (message.title(), sender, str(pointamount), "" if pointamount == 1 else 's', str(timeelapsed)))
                if sender in points:
                    points[sender] += pointamount
                else:
                    points[sender] = pointamount
                if savepoints == True:
                    pointsfile = open('points.json', 'w')
                    pointsfile.write(json.dumps(points))
                    pointsfile.close()
                time.sleep(1)
                answer = ""
        elif message.lower() == prefix+"skip":
            if answer != "":
                if started == True:
                    if sender in admins:
                        end = time.time()
                        timeelapsed = str(round(end - start, 2))
                        privmsg(sendto, "\x035,5http\x03%s pregunta salteada! (despues de %ss)\x035,5http\x03" % (sender, timeelapsed))
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
                                privmsg(sendto, "\x035,5http\x03%s salteo de pregunta, pierden 04%s punto%s! (despues de %ss)\x035,5http\x03" % (sender, str(pointamount), "" if pointamount == 1 else 's', str(timeelapsed)))
                                points[sender] -= pointamount
                                if points[sender] == 0:
                                    privmsg(sendto, "%s: Atencion, no te quedan puntos, no podes saltear mas preguntas hasta que no consigas puntos." % sender)
                                elif points[sender] < 5:
                                    privmsg(sendto, "%s: Atencion, tenes menos de 5 puntos, no podes saltear mas preguntas hasta que consigas puntaje." % sender)
                                if savepoints == True:
                                    pointsfile = open('points.json', 'w')
                                    pointsfile.write(json.dumps(points))
                                    pointsfile.close()
                                time.sleep(1)
                                answer = ""
                            else:
                                privmsg(sendto, "%s: Necesitas al menos 5 puntos para saltear la pregunta, tenes %s." % (sender, str(points[sender])))
                        else:
                            privmsg(sendto, "%s: Todavia no respondiste ni una pregunta, necesitas al menos 5 puntos para poder saltear preguntas." % sender)
                else:
                    privmsg(sendto, "%s: Trivia no iniciada, tipea %sstart para comenzar." % (sender, prefix))
        elif message.lower() == prefix+"stop":
            if started == True:
                if sender in admins:
                    answer = ""
                    number = 1
                    if savepoints != True:
                        points = {}
                    triviatopic = None
                    started = False
                    privmsg(sendto, "Trivia finalizada! Tipea %sstart para comenzar de nuevo!" % prefix)
                elif sender in points:
                    if points[sender] > 10:
                        answer = ""
                        number = 1
                        if savepoints != True:
                            points = {}
                        triviatopic = None
                        started = False
                        privmsg(sendto, "Trivia finalizada! Tipea %sstart para comenzar de nuevo!" % prefix)
                    else:
                        privmsg(sendto, "\x035,5http\x03%s: Necesitas al menos 10 puntos para detener el juego, tenes %s.\x035,5http\x03" % (sender, str(points[sender])))
                else:
                    privmsg(sendto, "%s: No respondiste ni una pregunta todavia, precisas al menos 10 puntos para detener el juego." % (sender))
            else:
                privmsg(sendto, "%s: Trivia no iniciada, tipea %sstart para comenzar." % (sender, prefix))
        elif message.lower() == prefix+"quit":
            if sender in admins:
                if started != True:
                    irc.send('FINALIZADA : por %s.\n' % sender)
                    sys.exit()
                else:
                    privmsg(sendto, "%s: Imposible salir de la Trivia mientras hay un juego, tipea %sstop y prueba nuevamente." % (sender, prefix))
            else:
                privmsg(sendto, "%s: No tenes autorizacion para realizar esta funcion." % sender)
        elif message.lower() == prefix+"points":
            if started == True or savepoints == True:
                if not points:
                    privmsg(sendto, "%s: Nadie contesto ni una pregunta todavia, vamos, quien sera el primero?!" % sender)
                else:
                    pointlist = []
		    # se ordena alfabeticamente usuarios para mostrar sus puntajes
		    # teniendo en cuenta que hay nicks mezclados tanto en mayusculas
		    # como en minusculas
                    for pointkey in sorted(points, key=lambda x: x.lower()):
			#privmsg(sendto, str(pointkey)+": "+str(points[pointkey]))
                        pointlist.append(str(pointkey)+": "+str(points[pointkey]))
                    privmsg(sendto, "\x034,4http\x03"+sender+": "+", ".join(pointlist)+"\x034,4http\x03")
            else:
                privmsg(sendto, "%s: Trivia no inciada, tipea %sstart para comenzar." % (sender, prefix))
        elif message.lower().startswith(prefix+"switch"):
            if sender in admins:
                if started != True:
                    try:
                        test_channel = message.split(" ", 1)[1].strip()
                        if re.match(r'#{1,}[A-Za-z0-9!"#%&\/()=`\'*.\-_~\+:;@{}\[\]\\]{0,}', test_channel):
                            irc.send("PART %s :Switching channel...\r\n" % channel)
                            irc.send("JOIN %s\r\n" % test_channel)
                        else:
                            privmsg(sendto, "%s: The channel you entered was invalid." % (sender))
                    except Exception:
                        privmsg(sendto, "%s: The channel you entered was invalid." % (sender))
                else:
                    privmsg(sendto, "%s: Cannot switch channels while trivia is in session, please type %sstop to stop." % (sender, prefix))
            else:
                privmsg(sendto, "%s: No tenes autorizacion para realizar esta funcion." % sender)
        elif message.lower() == prefix+"commands" or message.lower() == prefix+"commandlist" or message.lower() == prefix+"help":
            command_list = []
            if started != True:
                command_list.append(addhelp(prefix, "start"))
            if started == True:
                command_list.append(addhelp(prefix, "stop"))
                command_list.append(addhelp(prefix, "skip"))
                command_list.append(addhelp(prefix, "tema"))
            if started == True or savepoints == True:
                command_list.append(addhelp(prefix, "points"))
            command_list.append(addhelp(prefix, "commands"))
            command_list.append(addhelp(prefix, "commandlist"))
            command_list.append(addhelp(prefix, "help"))
            if sender in admins:
                if started != True:
                    command_list.append(addhelp(prefix, "quit"))
                    command_list.append(addhelp(prefix, "switch"))
            privmsg(sendto, "%s: los comandos que tenes disponibles son %s" % (sender, ", ".join(command_list)))

    while answer == "" and started == True and triviatopic != None:
        if triviatopic != "todos":
            topicjson = open("topics/"+triviatopic+".json")
        else:
            alltopics = topics[:]
            alltopics.remove("todos")
            topicjson = open("topics/"+random.choice(alltopics)+".json")
        questions = json.load(topicjson)
        if question in questions:
            questions.pop(question, None)
        topicjson.close()
        question = random.choice(questions.keys())
        answer = questions[question]
	# se asume una sola respuesta para la trivia
	# espaniola standard (aunque este bot soporta
	# multiples rtas a una misma pregunta
	# y se obtiene cantidad de palabras como ayuda
	# en el enunciado de la pregunta
	cantPals = len(answer[0].split())
	pals = "palabra"
	if cantPals > 1:
		pals = pals + "s"
        privmsg(sendto, "\x036,6http\x03Pregunta %s: %s (%s %s)\x036,6http\x03" % (number, question, cantPals, pals))
        start = time.time()
        number += 1
