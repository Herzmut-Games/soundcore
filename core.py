#!/usr/bin/python3
import os
import glob
import paho.mqtt.client as mqtt
import pygame
import random
import alsaaudio

sounddir = "/home/pi/git/soundcore/sounds"
stalesounds = []
def on_connect(client, userdata, flags, rc):
    print("Connected to mqtt with result code " + str(rc))
    client.subscribe("sound/volume")
    client.subscribe("sound/play")

def on_message(client, userdata, msg):
    #print("message on "+str(msg.topic)+" payload "+str(msg.payload.decode('utf-8')))
    try:
        # volume
        if (str(msg.topic) == "sound/volume"):
            vol = int(msg.payload.decode('utf-8'))
            m = alsaaudio.Mixer("Headphone")
            if vol > 100 or vol < 0:
                print("volume not valid:"+str(vol))
                return
            m.setvolume(vol)
            print("set volume to "+str(vol))
            return

        #custom play
        if (str(msg.topic) == "sound/play"):
            if "/" in str(msg.payload.decode('utf-8')):
                sound = sounddir+"/"+str(msg.payload.decode('utf-8'))
                if os.path.isfile(sound):
                    print("play requested sound "+sound)
                    play_sound(sound)
                else:
                    print("sound "+sound+" doesn't exist")
            else:
                soundlist = glob.glob(os.path.join(sounddir+"/"+msg.payload.decode('utf-8'), '*'))
                soundlist = list(set(soundlist)-set(stalesounds))
                sound = random.choice(soundlist)
                if len(stalesounds) == 10:
                    stalesounds.pop(0)
                stalesounds.append(sound)
                play_sound(sound)
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
