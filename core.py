#!/usr/bin/python3
import os
import glob
import paho.mqtt.client as mqtt
import pygame
import random
import alsaaudio

sounddir            = "/home/pi/git/soundcore/sounds"
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
spotify_status = "stop"

def on_connect(client, userdata, flags, rc):
    print("Connected to mqtt with result code " + str(rc))
    client.subscribe("score/white")
    client.subscribe("score/red")
    client.subscribe("game/end")
    client.subscribe("sound/volume")
    client.subscribe("sound/play")
    client.subscribe("spotify/status")

def on_message(client, userdata, msg):
    #print("message on "+str(msg.topic)+" payload "+str(msg.payload.decode('utf-8')))
    global score_red, score_white, spotify_status
    try:
        # volume
        if (str(msg.topic) == "sound/volume"):
            m = alsaaudio.Mixer('PCM')
            print("set volume to "+str(msg.payload.decode('utf-8')))
            m.setvolume(int(msg.payload.decode('utf-8')))
            return
        # set score
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

        #custom play
        if (str(msg.topic) == "sound/play"):
            if str(msg.payload.decode('utf-8')) == "goal":
                play_random_sound(GOALSOUNDS)
            elif str(msg.payload.decode('utf-8')) == "end":
                play_random_sound(ENDSOUNDS)
            elif str(msg.payload.decode('utf-8')) == "firstgoal":
                play_random_sound(FIRSTGOALSOUNDS)
            elif str(msg.payload.decode('utf-8')) == "start":
                play_random_sound(STARTSOUNDS)
            return
        #goal sound
        if (str(msg.topic) == "score/white" or str(msg.topic) == "score/red"):
            play_random_sound(GOALSOUNDS)

        # spotify status
        if (str(msg.topic) == "spotify/status"):
            spotify_status = str(msg.payload)


    except Exception as e:
        print(e)

def play_random_sound(list):
    global spotify_status
    if spotify_status != stop:
        print("not playing sound because spotify is playing")
        return
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
