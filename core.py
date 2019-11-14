#!/usr/bin/python3
import os
import glob
import paho.mqtt.client as mqtt
import pygame
import random
import alsaaudio

sounddir            = "/home/pi/soundcore/sounds"
goalsounddir        = sounddir+"/goal"
firstgoalsounddir   = sounddir+"/firstgoal"
startsounddir       = sounddir+"/start"
endsounddir         = sounddir+"/end"

GOALSOUNDS         = glob.glob(goalsounddir+"/*.mp3")
FIRSTGOALSOUNDS    = glob.glob(firstgoalsounddir+"/*.mp3")
STARTSOUNDS        = glob.glob(startsounddir+"/*.mp3") 
ENDSOUNDS          = glob.glob(endsounddir+"/*.mp3") 

score_red = 0
score_white = 0

def on_connect(client, userdata, flags, rc):
    print("Connected to mqtt with result code " + str(rc))
    client.subscribe("score/white")
    client.subscribe("score/red")
    client.subscribe("game/end")
    client.subscribe("sound/volume")

def on_message(client, userdata, msg):
    #print("message on "+str(msg.topic)+" payload "+str(msg.payload.decode('utf-8')))
    global score_red, score_white
    try:
        if (str(msg.topic) == "sound/volume"):
            m = alsaaudio.Mixer('PCM')
            print("set volume to "+str(msg.payload.decode('utf-8')))
            m.setvolume(int(msg.payload.decode('utf-8')))
            return

        if (str(msg.topic) == "score/red"):
            if (str(msg.payload.decode('utf-8')) == str(score_red)):
                print("red is already "+str(score_red))
                return
            else:
                score_red = int(msg.payload.decode('utf-8'))
                print("set score for red to: "+msg.payload.decode('utf-8'))
        if (str(msg.topic) == "score/white"):
            if (str(msg.payload.decode('utf-8')) == str(score_white)):
                print("white is already:"+str(score_white))
                return
            else:
                score_white = msg.payload.decode('utf-8')
                print("set score for white to: "+msg.payload.decode('utf-8'))   

        # return if reset
        if (str(msg.topic) == "score/red" and int(score_red) == 0):
            print("bla")
            return
        if (str(msg.topic) == "score/white" and int(score_white) == 0):
            return

        # firstblood
        if (int(score_white)+int(score_red) == 1):
            play_random_sound(FIRSTGOALSOUNDS)
            return
        if (str(msg.topic) == "game/end"):
            play_random_sound(ENDSOUNDS)
            return
        #goal sound

        play_random_sound(GOALSOUNDS)


    except Exception as e:
        print(e)

def play_random_sound(list):
    sound = random.choice(list)
    print("playing sound "+sound)
    pygame.mixer.music.load(sound)
    pygame.mixer.music.play()


pygame.mixer.init()
client = mqtt.Client()
client.on_connect = on_connect
client.on_message = on_message
client.connect("172.30.1.32", 1883, 60)


client.loop_forever()
