# sudo apt install libdbus-glib-1-dev dbus libdbus-1-dev
import json
import pygame
from pygame.locals import *

from omxplayer.player import OMXPlayer
from pathlib import Path
from time import sleep
from os import listdir
from os import popen2
from datetime import datetime


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

def handleCrash(player, VIDEO_PATH):
    print('OMX player crashed. Attempting to restart...')

    if player == "static":
        staticPlayer._connection._bus.close()
        staticPlayer._connection = None
        staticPlayer.quit()
        sleep(5)
        staticPlayer = OMXPlayer('./videos/snow.mp4', args=['--layer', '0', '--win', '1,1,500,400'], dbus_name='org.mpris.MediaPlayer2.omxplayer2')
    else:
        player.quit()
        player._connection._bus.close()
        player._connection = None
        sleep(5)
        player = OMXPlayer(VIDEO_PATH, args=['--layer', '1', '--win', '1,1,500,400'], dbus_name='org.mpris.MediaPlayer2.omxplayer1')

        
def analyzeClips():
    print('Analyzing clips...')
    settings = {}
    startTimes = {}
    totalChanDuration = {}
    numClips = {}

    for i in range(maxChans):
        tempChan = 'chan' + str(i+1) 
        fileList = listdir('./videos/' + tempChan)
        
        buildStartTimes = []
        buildTotalDuration = 0
        for clip in fileList:
            buildTotalDuration += video_length_seconds('./videos/' + tempChan + '/' + clip)
            buildStartTimes.append(buildTotalDuration)
            
        startTimes[tempChan] = buildStartTimes
        totalChanDuration[tempChan] = buildTotalDuration
        numClips[tempChan] = len(startTimes[tempChan])
        
    print('total length of channels:' + str(totalChanDuration))
    print('number of clips: ' + str(len(startTimes[tempChan])))

    staticPlayer = OMXPlayer('./videos/snow.mp4', args=['--layer', '0', '--win', '1,1,500,400', '--loop'], dbus_name='org.mpris.MediaPlayer2.omxplayer2')
    settings = {
        'startTimes': startTimes,
        'totalChanDuration': totalChanDuration,
        'numClips': numClips
        }

    with open('settings.json', 'w') as outfile:
        json.dump(settings, outfile)

    return staticPlayer, startTimes, totalChanDuration, numClips


def getSettings():
    with open('settings.json') as json_file:
        data = json.load(json_file)
        startTimes = data['startTimes']
        totalChanDuration  = data['totalChanDuration']
        numClips = data['numClips']
    staticPlayer = OMXPlayer('./videos/snow.mp4', args=['--layer', '0', '--win', '1,1,500,400'], dbus_name='org.mpris.MediaPlayer2.omxplayer2')

    return staticPlayer, startTimes, totalChanDuration, numClips


maxChans = 3
#staticPlayer, startTimes, totalChanDuration, numClips = analyzeClips()
staticPlayer, startTimes, totalChanDuration, numClips = getSettings()


pygame.init()
pygame.display.set_mode((100, 100))

done = False

print('start times')
print(startTimes)

currentChan = 1
currentClip = 0
tick = datetime.now()
fileList = listdir('./videos/chan' + str(currentChan))
VIDEO_PATH = Path('./videos/chan' + str(currentChan) + '/' + fileList[currentClip])

print('channel'+str(currentChan)+' starting')
print('now playing ' + str(VIDEO_PATH))

player = OMXPlayer(VIDEO_PATH, args=['--layer', '1', '--win', '1,1,500,400'], dbus_name='org.mpris.MediaPlayer2.omxplayer1')

currentChanDuration = {'chan1': 0, 'chan2':0, 'chan3':0}
currentClip = {'chan1': 0, 'chan2': 0, 'chan3':0}
chanTimestamps = {'chan1': datetime.now(), 'chan2': datetime.now(), 'chan3': datetime.now()}
clipDuration = 0
checkInterval = datetime.now()
loadingClip = True

while not done:
    tock = datetime.now()
    fileList = listdir('./videos/chan' + str(currentChan))
    if (tock-checkInterval).total_seconds() > 0.1 and loadingClip == True:
        try:
            print('checking player position')
            playerPosition = player.position()
        except Exception as e:
            print(e)
            handleCrash("player", VIDEO_PATH)
        
        if playerPosition < clipDuration:
            checkInterval = datetime.now()
        else:
            try:
                print('muting static')
                staticPlayer.mute()
            except Exception as e:
                print(e)
                handleCrash("static", VIDEO_PATH)
            
            checkInterval = datetime.now()
            loadingClip = False
            staticMuted = True
            
    # update individual channel durations. channels count starting at 1. Clips count from 0.
    for i in range(1, maxChans + 1):
        currentChanDuration['chan' + str(i)] = (tock - chanTimestamps['chan' + str(i)]).total_seconds() 
        
        # check for end of channel
        if currentChanDuration['chan' + str(i)] > 0.99 * totalChanDuration['chan' + str(i)]:
            currentChanDuration['chan' + str(i)] = 0
            chanTimestamps['chan' + str(i)] = datetime.now()
            if 'chan' + str(i) == 'chan' + str(currentChan):
                currentClip['chan' + str(i)] = 0
                VIDEO_PATH = Path('./videos/chan' + str(currentChan) + '/' + fileList[currentClip['chan' + str(i)]])
                clipDuration = 0
                print('end of channel now playing ' + str(VIDEO_PATH))

                try:
                    player.load(VIDEO_PATH)
                except Exception as e:
                    print(e)
                    handleCrash("player", VIDEO_PATH)
    
        
        # check for end of clip
        if currentChanDuration['chan' + str(i)] > (0.99 * startTimes['chan' + str(i)][currentClip['chan' + str(i)]]):
            currentClip['chan' + str(i)] += 1
            if currentClip['chan' + str(i)] > numClips['chan' + str(i)]:
                currentClip['chan' + str(i)] = 0
            if 'chan' + str(i) == 'chan' + str(currentChan):
                VIDEO_PATH = Path('./videos/chan' + str(currentChan) + '/' + fileList[currentClip['chan' + str(i)]])
                clipDuration = 0
                print('end of clip. now playing ' + str(VIDEO_PATH))
                
                try:
                    player.load(VIDEO_PATH)
                except Exception as e:
                    print(e)
                    handleCrash("player", VIDEO_PATH)

    events = pygame.event.get()
    for event in events:
        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_LEFT:
                staticPlayer.unmute()
                print("LEFT")
                currentChan -= 1
                if currentChan < 1:
                    currentChan = maxChans
                fileList = listdir('./videos/chan' + str(currentChan))
                
                # determine clip number based on duration
                for i in range(len(startTimes['chan' + str(currentChan)])):
                    #print('i = '+ str(i))
                    currentClip['chan' + str(currentChan)] = 0
                    if i == len(startTimes['chan' + str(currentChan)]):
                        currentClip['chan' + str(currentChan)] = i
                        break
                    if currentChanDuration['chan' + str(currentChan)] > startTimes['chan' + str(currentChan)][i] and currentChanDuration['chan' + str(currentChan)] < startTimes['chan' + str(currentChan)][i+1]:
                        print('chan duration > start time')
                        print('current clip is being set to ' + str(i+1))
                        currentClip['chan' + str(currentChan)] = i+1
                        break
                #print('1. current clip is still ' + str(currentClip['chan' + str(currentChan)]))
                
                if currentClip['chan' + str(currentChan)] == 0:
                    clipDuration = currentChanDuration['chan' + str(currentChan)]
                else:        
                    clipDuration = currentChanDuration['chan' + str(currentChan)] - startTimes['chan' + str(currentChan)][currentClip['chan' + str(currentChan)]-1]
                #
                #elif currentChanDuration['chan' + str(currentChan)] >= startTimes['chan' + str(currentChan)][currentClip['chan' + str(currentChan)]]:
                
                print('current channel is now: ' + str(currentChan))
                print('current channel duration is: '+ str(currentChanDuration['chan' + str(currentChan)]))               
                print('current clip is now: ' + str(currentClip['chan' + str(currentChan)]))
                print('current clip duration is: ' + str(clipDuration))
                
                VIDEO_PATH = Path('./videos/chan' + str(currentChan) + '/' + fileList[currentClip['chan' + str(currentChan)]])
                try:
                    player.load(VIDEO_PATH)
                except Exception as e:
                    print(e)
                    handleCrash("player", VIDEO_PATH)

                # NEEDS TO ACTUALLY SET CLIP DURATION ON CRASH/EXCEPTION
                try:
                    player.set_position(clipDuration)
                except Exception as e:
                    print(e)
                    handleCrash("player", VIDEO_PATH)
                
                print('now playing ' + str(VIDEO_PATH))
                loadingClip = True
                
                try:
                    print('unmuting static')
                    staticPlayer.unmute()
                except Exception as e:
                    print(e)
                    handleCrash("static", VIDEO_PATH)

            if event.key == pygame.K_RIGHT:
                print("RIGHT")
                currentChan += 1
                if currentChan > maxChans:
                    currentChan = 1
                fileList = listdir('./videos/chan' + str(currentChan))
                VIDEO_PATH = Path('./videos/chan' + str(currentChan) + '/' + fileList[currentClip['chan' + str(currentChan)]])
                print('current channel is now: ' + str(currentChan))
                print('current clip is now: ' + str(currentClip['chan' + str(currentChan)]))
                print('current channel duration is: '+ str(currentChanDuration['chan' + str(currentChan)]))
                player.quit()

            if event.key == pygame.K_ESCAPE:
                print("ESCAPE")                
                player.quit()
                staticPlayer.quit()
                done = True
