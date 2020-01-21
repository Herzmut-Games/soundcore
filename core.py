#!/usr/bin/python3
import os
import glob
import paho.mqtt.client as mqtt
import pygame
import random
import alsaaudio

sounddir = "/home/pi/git/soundcore/sounds"

def on_connect(client, userdata, flags, rc):
    print("Connected to mqtt with result code " + str(rc))
    client.subscribe("sound/volume")
    client.subscribe("sound/play")

def on_message(client, userdata, msg):
    #print("message on "+str(msg.topic)+" payload "+str(msg.payload.decode('utf-8')))
    try:
        # volume
        if (str(msg.topic) == "sound/volume"):
            m = alsaaudio.Mixer('PCM')
            print("set volume to "+str(msg.payload.decode('utf-8')))
            m.setvolume(int(msg.payload.decode('utf-8')))
            return

        #custom play
        if (str(msg.topic) == "sound/play"):
            if "/" in str(msg.payload.decode('utf-8')):
                dir = sounddir+"/"+str(msg.payload.decode('utf-8'))
                if os.path.isdir(dir):
                    play_sound(dir+"/"+random.choice(os.listdir(dir)))
                else:
                    print("sound "+str(msg.payload.decode('utf-8'))+" doesn't exist")
            else:
                category = random.choice(os.listdir(sounddir+"/"+msg.payload.decode('utf-8')))
                sound = random.choice(os.listdir(sounddir+"/"+msg.payload.decode('utf-8')+"/"+category))
                play_sound(sounddir+"/"+msg.payload.decode('utf-8')+"/"+category+"/"+sound)
            return

    except Exception as e:
        print(e)

def play_sound(sound):
    print("playing sound "+sound)
    pygame.mixer.music.load(sound)
    pygame.mixer.music.play()


pygame.mixer.init()
client = mqtt.Client()
client.on_connect = on_connect
client.on_message = on_message
client.connect("kickerpi.local", 1883, 60)

client.loop_forever()
