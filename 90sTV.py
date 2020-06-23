# Dependencies:
#
# sudo apt install libdbus-glib-1-dev dbus libdbus-1-dev
# pip install omxplayer-wrapper
# pip install pathlib
# subtitles don't work with pi4 as of latest build: Thu, 01 Aug 2019 version f543a0d [master]

import json
import pygame
from pygame.locals import *
from omxplayer.player import OMXPlayer
from pathlib import Path
from time import sleep
from os import listdir
from os import popen2
from datetime import datetime
from datetime import timedelta
import RPi.GPIO as GPIO

def video_length_seconds(filename):
    stin, stout = popen2(
        [
            "ffprobe",
            "-v",
            "error",
            "-show_entries",
            "format=duration",
            "-of",
            "default=noprint_wrappers=1:nokey=1",
            filename,
            
        ],
        'rb'
    )
    try:
        output = stout.read().strip('\n')
        return float(output)
    except ValueError:
        print(filename + ' error')
        return(0)

def handleCrash(isStatic, VIDEO_PATH):
    print('OMX player crashed. Attempting to restart...')
    try:
        if isStatic == True:
            staticPlayer._connection._bus.close()
            staticPlayer._connection = None
            staticPlayer.quit()
            sleep(5)
            staticPlayer = OMXPlayer('/home/pi/python/videos/snow.mp4', args=['--no-osd', '--layer', '0', '--win', '1,1,500,400'], dbus_name='org.mpris.MediaPlayer2.omxplayer2')
        else:
            player.quit()
            player._connection._bus.close()
            player._connection = None
            sleep(5)
            player = OMXPlayer(VIDEO_PATH, args=['--no-osd', '--layer', '1', '--win', '1,1,500,400'], dbus_name='org.mpris.MediaPlayer2.omxplayer1')
    except Exception as e:
        print(str(e))
        
def analyzeClips():
    print('Analyzing clips...')
    settings = {}
    startTimes = {}
    totalChanDuration = {}
    numClips = {}

    for i in range(maxChans):
        tempChan = 'chan' + str(i+1) 
        fileList = listdir('/home/pi/python/videos/' + tempChan)
        print('analyzing chan' + str(i+1))
        
        buildStartTimes = []
        buildTotalDuration = 0
        for clip in fileList:
            buildTotalDuration += video_length_seconds('/home/pi/python/videos/' + tempChan + '/' + clip)
            buildStartTimes.append(buildTotalDuration)
            
        startTimes[tempChan] = buildStartTimes
        totalChanDuration[tempChan] = buildTotalDuration
        numClips[tempChan] = len(startTimes[tempChan])
        
    print('total length of channels:' + str(totalChanDuration))
    print('number of clips: ' + str(len(startTimes[tempChan])))

    staticPlayer = OMXPlayer('/home/pi/python/videos/snow.mp4', args=['--no-osd', '--layer', '0', '--loop'], dbus_name='org.mpris.MediaPlayer2.omxplayer2')
    settings = {
        'startTimes': startTimes,
        'totalChanDuration': totalChanDuration,
        'numClips': numClips
        }

    with open('/home/pi/python/settings.json', 'w') as outfile:
        json.dump(settings, outfile)

    return staticPlayer, startTimes, totalChanDuration, numClips


def getSettings():
    with open('/home/pi/python/settings.json') as json_file:
        data = json.load(json_file)
        startTimes = data['startTimes']
        totalChanDuration  = data['totalChanDuration']
        numClips = data['numClips']
    staticPlayer = OMXPlayer('/home/pi/python/videos/snow.mp4', args=['--no-osd', '--layer', '0'], dbus_name='org.mpris.MediaPlayer2.omxplayer2')
    return staticPlayer, startTimes, totalChanDuration, numClips

def buildsrt(duration, chanNum):

    #print('building srt')
    #print('duration is:' + str(duration))
    startTime = str(timedelta(seconds = int(duration)))
    endTime = str(timedelta(seconds = int(duration + 3)))
    line1 = startTime + ',00 --> ' + endTime + ',00'
    line2 = str(chanNum)
    print(line1)
    print(line2)
    file = open('/home/pi/python/caption.srt', 'w')
    file.write(line1)
    file.write("\n")
    file.write(line2)
    
        
# initialize variables and settings

pygame.init()
pygame.display.set_mode((100, 100))
GPIO.setmode(GPIO.BCM)

chanUpBtn = 17
GPIO.setup(chanUpBtn, GPIO.IN, pull_up_down=GPIO.PUD_UP)
GPIO.add_event_detect(chanUpBtn, GPIO.RISING)
chanDownBtn = 27
GPIO.setup(chanDownBtn, GPIO.IN, pull_up_down=GPIO.PUD_UP)
GPIO.add_event_detect(chanDownBtn, GPIO.RISING)


currentChanDuration = {'chan1': 0, 'chan2':0, 'chan3':0, 'chan4':0, 'chan5':0, 'chan6':0, 'chan7':0, 'chan8':0, 'chan9':0, 'chan10':0, 'chan11':0, 'chan12':0, 'chan13':0, 'chan14':0, 'chan15':0, 'chan16':0, 'chan17':0, 'chan18':0, 'chan19':0, 'chan20':0, 'chan21':0, 'chan22':0, 'chan23':0, 'chan24':0, 'chan25':0, 'chan26':0, 'chan27':0, 'chan28':0, 'chan29':0, 'chan30':0, 'chan31':0, 'chan32':0, 'chan33':0, 'chan34':0, 'chan35':0, 'chan36':0, 'chan37':0, 'chan38':0, 'chan39':0, 'chan40':0, 'chan41':0, 'chan42':0, 'chan43':0, 'chan44':0, 'chan45':0, 'chan46':0, 'chan47':0, 'chan48':0, 'chan49':0, 'chan50':0}
currentClip = {'chan1': 0, 'chan2':0, 'chan3':0, 'chan4':0, 'chan5':0, 'chan6':0, 'chan7':0, 'chan8':0, 'chan9':0, 'chan10':0, 'chan11':0, 'chan12':0, 'chan13':0, 'chan14':0, 'chan15':0, 'chan16':0, 'chan17':0, 'chan18':0, 'chan19':0, 'chan20':0, 'chan21':0, 'chan22':0, 'chan23':0, 'chan24':0, 'chan25':0, 'chan26':0, 'chan27':0, 'chan28':0, 'chan29':0, 'chan30':0, 'chan31':0, 'chan32':0, 'chan33':0, 'chan34':0, 'chan35':0, 'chan36':0, 'chan37':0, 'chan38':0, 'chan39':0, 'chan40':0, 'chan41':0, 'chan42':0, 'chan43':0, 'chan44':0, 'chan45':0, 'chan46':0, 'chan47':0, 'chan48':0, 'chan49':0, 'chan50':0}
chanTimestamps = {'chan1': datetime.now(), 'chan2':datetime.now(), 'chan3':datetime.now(), 'chan4':datetime.now(), 'chan5':datetime.now(), 'chan6':datetime.now(), 'chan7':datetime.now(), 'chan8':datetime.now(), 'chan9':datetime.now(), 'chan10':datetime.now(), 'chan11':datetime.now(), 'chan12':datetime.now(), 'chan13':datetime.now(), 'chan14':datetime.now(), 'chan15':datetime.now(), 'chan16':datetime.now(), 'chan17':datetime.now(), 'chan18':datetime.now(), 'chan19':datetime.now(), 'chan20':datetime.now(), 'chan21':datetime.now(), 'chan22':datetime.now(), 'chan23':datetime.now(), 'chan24':datetime.now(), 'chan25':datetime.now(), 'chan26':datetime.now(), 'chan27':datetime.now(), 'chan28':datetime.now(), 'chan29':datetime.now(), 'chan30':datetime.now(), 'chan31':datetime.now(), 'chan32':datetime.now(), 'chan33':datetime.now(), 'chan34':datetime.now(), 'chan35':datetime.now(), 'chan36':datetime.now(), 'chan37':datetime.now(), 'chan38':datetime.now(), 'chan39':datetime.now(), 'chan40':datetime.now(), 'chan41':datetime.now(), 'chan42':datetime.now(), 'chan43':datetime.now(), 'chan44':datetime.now(), 'chan45':datetime.now(), 'chan46':datetime.now(), 'chan47':datetime.now(), 'chan48':datetime.now(), 'chan49':datetime.now(), 'chan50':datetime.now()}


clipDuration = 0
currentChanNum = 1
currentChanStr = 'chan' + str(currentChanNum)

maxChans = 50 # set to number of directories to look for
tick = datetime.now()
checkInterval = datetime.now()

loadingClip = True
done = False

fileList = listdir('/home/pi/python/videos/chan' + str(currentChanNum))
VIDEO_PATH = Path('/home/pi/python/videos/chan' + str(currentChanNum) + '/' + fileList[0])
TITLE_PATH = Path('/home/pi/python/caption.srt')

staticPlayer, startTimes, totalChanDuration, numClips = getSettings() # comment out when first running
#staticPlayer, startTimes, totalChanDuration, numClips = analyzeClips() # comment out after first run

buildsrt(0,currentChanNum) # build srt starting with time zero and starting chanNum
player = OMXPlayer(VIDEO_PATH, args=['--no-osd', '--subtitles', TITLE_PATH,'--lines', '1', '--align', 'center', '--font-size', '100', '--layer', '1', ], dbus_name='org.mpris.MediaPlayer2.omxplayer1')
sleep (5)
while not done:
    tock = datetime.now()
    fileList = listdir('/home/pi/python/videos/chan' + str(currentChanNum))
    
    # slow down checking player position to every 0.1 s to avoid dbus crashing
    if (tock-checkInterval).total_seconds() > 0.1 and loadingClip == True:
        try:
            print('checking player position')
            playerPosition = player.position()
        except Exception as e:
            print(e)
            handleCrash(False, VIDEO_PATH)
        
        # continue checking to see if the main video player has loaded, else mute static player and set loadingClip to False
        if playerPosition < clipDuration:
            checkInterval = datetime.now()
        else:
            staticPlayer.mute()
            checkInterval = datetime.now()
            loadingClip = False
            staticMuted = True
            
    # update individual channel durations. Channels count starting at 1. Clips count from 0.
    for i in range(1, maxChans + 1):
        channel = 'chan' + str(i)
        currentChanDuration[channel] = (tock - chanTimestamps[channel]).total_seconds() 
        
        # check for end of channel
        if currentChanDuration[channel] > 0.99 * totalChanDuration[channel]:
            currentChanDuration[channel] = 0
            chanTimestamps[channel] = datetime.now()
            if channel == currentChanStr:
                currentClip[channel] = 0
                
                VIDEO_PATH = Path('/home/pi/python/videos/' + channel + '/' + fileList[currentClip[channel]])
                clipDuration = 0
                player.hide_subtitles()
                print('End of channel. Now playing ' + str(VIDEO_PATH))

                try:
                    player.quit()
                    player = OMXPlayer(VIDEO_PATH, args=['--no-osd', '--subtitles', TITLE_PATH,'--lines', '1', '--align', 'center', '--font-size', '100', '--layer', '1', ], dbus_name='org.mpris.MediaPlayer2.omxplayer1')
                except Exception as e:
                    print(e)
                    handleCrash(False, VIDEO_PATH)
    
        # check for end of clip
        if currentChanDuration[channel] > (0.99 * startTimes[channel][currentClip[channel]]):
            currentClip[channel] += 1
            if currentClip[channel] > numClips[channel]:
                currentClip[channel] = 0
            if channel == currentChanStr:
                
                VIDEO_PATH = Path('/home/pi/python/videos/chan' + str(currentChanNum) + '/' + fileList[currentClip[channel]])
                clipDuration = 0
                player.hide_subtitles()
                print('End of clip. Now playing ' + str(VIDEO_PATH))
                
                try:
                    player.quit()
                    player = OMXPlayer(VIDEO_PATH, args=['--no-osd', '--subtitles', TITLE_PATH,'--lines', '1', '--align', 'center', '--font-size', '100', '--layer', '1', ], dbus_name='org.mpris.MediaPlayer2.omxplayer1')

                except Exception as e:
                    print(e)
                    handleCrash(False, VIDEO_PATH)
    
    # listen for button changes using pygame
    chanUpInputState = GPIO.input(chanUpBtn)
    chanDownInputState = GPIO.input(chanDownBtn)
    
    if chanUpInputState == False or chanDownInputState == False:
        # adjust channel number and re-initialize fileList 
        if chanUpInputState == False:
            print('Channel Up')
            currentChanNum += 1
            if currentChanNum > maxChans:
                currentChanNum = 1
        else:        
            currentChanNum -= 1
            if currentChanNum < 1:
                currentChanNum = maxChans
        currentChanStr = 'chan' + str(currentChanNum)
        fileList = listdir('/home/pi/python/videos/' + currentChanStr)
        
        # determine clip number based on duration
        for i in range(len(startTimes[currentChanStr])):
            currentClip[currentChanStr] = 0
            if i == len(startTimes[currentChanStr]):
                currentClip[currentChanStr] = i
                break
            if currentChanDuration[currentChanStr] > startTimes[currentChanStr][i] and currentChanDuration[currentChanStr] < startTimes[currentChanStr][i+1]:
                print('chan duration > start time')
                print('current clip is being set to ' + str(i+1))
                currentClip[currentChanStr] = i+1
                break

        # if the current clip is the first in the list then the clip duration is the same as the channel duration, else set the clip duration using start times from settings.json
        if currentClip[currentChanStr] == 0:
            clipDuration = currentChanDuration[currentChanStr]
        else:        
            clipDuration = currentChanDuration[currentChanStr] - startTimes[currentChanStr][currentClip[currentChanStr]-1]
        
        print('current channel is now: ' + str(currentChanNum))
        print('current channel duration is: '+ str(currentChanDuration[currentChanStr]))               
        print('current clip is now: ' + str(currentClip[currentChanStr]))
        print('current clip duration is: ' + str(clipDuration))
        
        buildsrt(clipDuration, currentChanNum)
                 
        VIDEO_PATH = Path('/home/pi/python/videos/chan' + str(currentChanNum) + '/' + fileList[currentClip[currentChanStr]])
        try:
            player.show_subtitles()
            player.quit()
            player = OMXPlayer(VIDEO_PATH, args=['--no-osd', '--subtitles', TITLE_PATH,'--lines', '1', '--align', 'center', '--font-size', '100', '--layer', '1', ], dbus_name='org.mpris.MediaPlayer2.omxplayer1')
            player.show_subtitles()
            #player.load(VIDEO_PATH)
        except Exception as e:
            print(e)
            handleCrash(False, VIDEO_PATH)

        player.set_position(clipDuration)
        print('now playing ' + str(VIDEO_PATH))
        loadingClip = True
        sleep(0.5)

    
    events = pygame.event.get()
    for event in events:
        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_LEFT:
                print("LEFT")
                staticPlayer.unmute()
                
                # adjust channel number and re-initialize fileList
                currentChanNum -= 1
                if currentChanNum < 1:
                    currentChanNum = maxChans
                currentChanStr = 'chan' + str(currentChanNum)
                fileList = listdir('/home/pi/python/videos/' + currentChanStr)
                
                # determine clip number based on duration
                for i in range(len(startTimes[currentChanStr])):
                    currentClip[currentChanStr] = 0
                    if i == len(startTimes[currentChanStr]):
                        currentClip[currentChanStr] = i
                        break
                    if currentChanDuration[currentChanStr] > startTimes[currentChanStr][i] and currentChanDuration[currentChanStr] < startTimes[currentChanStr][i+1]:
                        print('chan duration > start time')
                        print('current clip is being set to ' + str(i+1))
                        currentClip[currentChanStr] = i+1
                        break

                # if the current clip is the first in the list then the clip duration is the same as the channel duration, else set the clip duration using start times from settings.json
                if currentClip[currentChanStr] == 0:
                    clipDuration = currentChanDuration[currentChanStr]
                else:        
                    clipDuration = currentChanDuration[currentChanStr] - startTimes[currentChanStr][currentClip[currentChanStr]-1]
                
                print('current channel is now: ' + str(currentChanNum))
                print('current channel duration is: '+ str(currentChanDuration[currentChanStr]))               
                print('current clip is now: ' + str(currentClip[currentChanStr]))
                print('current clip duration is: ' + str(clipDuration))
                
                buildsrt(clipDuration, currentChanNum)
                         
                VIDEO_PATH = Path('/home/pi/python/videos/chan' + str(currentChanNum) + '/' + fileList[currentClip[currentChanStr]])
                try:
                    player.show_subtitles()
                    player.quit()
                    player = OMXPlayer(VIDEO_PATH, args=['--no-osd', '--subtitles', TITLE_PATH,'--lines', '1', '--align', 'center', '--font-size', '100', '--layer', '1', ], dbus_name='org.mpris.MediaPlayer2.omxplayer1')
                    player.show_subtitles()
                    #player.load(VIDEO_PATH)
                except Exception as e:
                    print(e)
                    handleCrash(False, VIDEO_PATH)

                player.set_position(clipDuration)
                print('now playing ' + str(VIDEO_PATH))
                loadingClip = True
                staticPlayer.unmute()
                


            if event.key == pygame.K_ESCAPE:
                print("ESCAPE")                
                player.quit()
                staticPlayer.quit()
                done = True
