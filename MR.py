"""
This script contains the code for the Time To Fuse paradigm used in Margaret river (python version 3.8.19).
It has two stimulus types, a text mode (the one used in Margaret river) and an image mode
you can choose between 3 discrete VID conditions. This is because the text is prerenderd and the size cannot be reliably changed by python (well maybe it can, but this hasn't been tested)
There are two anaglyph modes depending on whether you're using the cardboard glasses found readily in the office, or the two pairs of plastic glasses we bought for the APS open house
The difficulty parameter only changes the difficulty during the practice trials (it allows for smaller duration and larger magnitudes of VBD). The parameters during the experimental trials are always controlled by AEPsych
When mode is set to "debug", anaglyph compatible text will be displayed. Otherwise, text colour is white
Left, right and back screens: python is inconsistent with screen numbers, and seemingly randomly assigns them to connected monitors. MonitorIdentifier.py can be run to reveal which number corresponds to which screen, so you can properly assign the left right and back screens properly
"""

from psychopy import core, data, event, gui, prefs, sound, visual, monitors, colors
from psychopy.tools.filetools import fromFile, toFile

from datetime import datetime
import numpy as np
import pandas as pd
import math
from random import choice, randrange, uniform
import socket
import json
import os
import os.path


prefs.general['audioLib'] = ['sounddevice']
prefs.hardware['audioLib']=['sounddevice']



# ==========================
# DEFINE SOME KEY PARAMETERS (most are controlled by the gui and are found below)
# ==========================

##directory location of the current experiment (which needs to be a subfolder within the margaret-river folder). The structure of the margaret-river folder is important for this experiment to run correctly
#dir = 'C:/Users/frl/Documents/Margaret River/Time To Fuse/'
dir = 'C:\\Users\\rezasaeedpour\\Documents\\GitHub\\margaret-river\\Time To Fuse\\'


## Vertical disparity parameters
constantOffset          =   0.0     ## arcmin

## image Parameters
imageSize               =   5.0    ## degrees

#background contrast
bgContrast = 0.5



## list of possible parameters (to display in the gui)
vidList = ['57','100','139']
stimList = ['word','image']
locList = ['desk','lab']
modeList = ['debug','test']
bgList = ['off','pinknoise','deadleaves']
practiceList = ['on','off']

## function to reorder lists which helps keep dropdown menus while remembering the previously used parameters
def move_to_front(lst, item):
    lst.remove(item)
    lst.insert(0, item)
    return lst

## Define session parameters. Check to see if a file containing previously used parameters can be found
try:
    sessionInfoTemp = fromFile(dir+'lastInfo.pickle')

    sessionInfo = {
    'Left, Right, and Back Screens': sessionInfoTemp['Left, Right, and Back Screens'],
    'participantID':sessionInfoTemp['participantID'],
    'Horizontal Disparity (arcmin)': sessionInfoTemp['Horizontal Disparity (arcmin)'],
    'Gap Between Stimuli (deg)': sessionInfoTemp['Gap Between Stimuli (deg)'],
    'VID (cm)': move_to_front(vidList, sessionInfoTemp['VID (cm)']),
    'Stim Type': move_to_front(stimList, sessionInfoTemp['Stim Type']),
    'Location': move_to_front(locList, sessionInfoTemp['Location']),
    'Mode': move_to_front(modeList, sessionInfoTemp['Mode']),
    'Background': move_to_front(bgList, sessionInfoTemp['Background']),
    'Practice Session': move_to_front(practiceList, sessionInfoTemp['Practice Session'])


    }
except:
    sessionInfo = {
        'Left, Right, and Back Screens': '1 2 3',
        'participantID':'999',
        'Horizontal Disparity (arcmin)': '5',
        'Gap Between Stimuli (deg)': '8',
        'VID (cm)': vidList,
        'Stim Type': stimList,
        'Location': locList,
        'Mode': modeList,
        'Background': bgList,
        'Practice Session': practiceList


        }

sessionInfo['Difficulty'] = ['easy','hard']
sessionInfo['Anaglyph Type'] = ['plastic','cardboard']
sessionInfo['date'] = data.getDateStr(format="%Y-%m-%d-%H%M")


Order = ['date','Left, Right, and Back Screens','participantID', 'Horizontal Disparity (arcmin)', 'Gap Between Stimuli (deg)', 'VID (cm)', 'Practice Session', 'Background']
## Present a dialogue to change params
dlg = gui.DlgFromDict(sessionInfo, title='Project Margaret River TTF Task', order=Order, fixed=['date'])
if dlg.OK:
    completeName = os.path.join(dir, 'lastInfo.pickle')
    toFile(completeName, sessionInfo)
else:
    core.quit()


## Set parameters based on gui choices
viewDistance = int(sessionInfo['VID (cm)'])
hDisparityMagnitude = int(sessionInfo['Horizontal Disparity (arcmin)'])
stimSpacing = int(sessionInfo['Gap Between Stimuli (deg)'])
loc = sessionInfo['Location']
mode = sessionInfo['Mode']

if sessionInfo['Stim Type'] == 'word':
    stimType = 'w'
elif sessionInfo['Stim Type'] == 'image':
    stimType = 'i'

if sessionInfo['Background'] != 'off':
    background = "on"
    bgType = sessionInfo['Background']
else:
    background = "off"

if sessionInfo['Practice Session'] == 'on':
    practice = True
else:
    practice = False

## demo parameters (changes the difficulty of the )
if sessionInfo['Difficulty'] == 'easy':
    easy = True
elif sessionInfo['Difficulty'] == 'hard':
    easy = False


## screen numbers python has assigned to various screens when doing a multi-monitor setup.
## This is at the top for easy access since python likes to randomize these
screens = sessionInfo['Left, Right, and Back Screens'].split()
screenLeft = int(screens[0])
screenRight = int(screens[1])
screenBack = int(screens[2])


numPracticeTrials = 100



# ==========================
# INITIALIZE THE EXPERIMENT
# ==========================

## Initialize disparity
global currentDisparity
global disparityAmplitude
global stimulusDuration


## Set location to lab or desk and adjust directories/monitors accordingly
if loc == "lab":
    monWidth = 4096
    monHeight = 2160
    monWidthCM = 69.85
    BmonWidth = 3840
    BmonHeight = 2160
    BmonWidthCM = 165
    col = (1,1,1)

elif loc == "desk":
    monWidth = 2560
    monHeight = 1600
    monWidthCM = 40
    ##defining different colors so that analglygh glasses can be used for dichoptic presentation




## Commence setup of functions for AEPsych
continue_if_data = 'yes'


def loadJSON(jsonFile):
    # Opening JSON file
    f = open(jsonFile)

    # returns JSON object as a dictionary
    data = json.load(f)
         # Closing file
    f.close()
    return data

def primeDatabase(data, socket):
    for tell in data:
        SocketSendMessage(socket, tell)
        SocketRecvMessage(socket)


def writeJSON(dataJSON, fileJSON):
    if len(dataJSON) > 0:
        json_object = json.dumps(dataJSON, indent=4)
        with open(fileJSON, "w") as outfile:
            outfile.write(json_object)


## Initialize clock
globalClock = core.Clock()





## Make a text file to save datam and
if stimType== "w":
    fileName = "MargaretRiver_TTFuse_PPT" + sessionInfo['participantID'] + "_VID_" + sessionInfo['VID (cm)'] + "_StimType_" + stimType + "_Spacing_" + str(stimSpacing) + "_HorDisparity_" + str(hDisparityMagnitude) + "_XHeight_24arcmin_" + "_Background_" + sessionInfo['Background'] + "_bgContrast_" + str(bgContrast) + "_" + loc + "_" + mode + "_" + sessionInfo['date']
elif stimType == "i":
    fileName = "MargaretRiver_TTFuse_PPT" + sessionInfo['participantID'] + "_VID_" + sessionInfo['VID (cm)'] + "_StimType_" + stimType + "_Spacing_" + str(stimSpacing) + "_HorDisparity_" + str(hDisparityMagnitude) + "_ImageHeight_" + str(imageSize) + "_" + sessionInfo['Background'] + "_bgContrast_" + str(bgContrast) + "_" + loc + "_" + mode + "_" + sessionInfo['date']

completeName = os.path.join(dir, 'Data/'+fileName+'.csv')
dataFile = open(completeName, 'w')

##changeing opactity and blend mode depending on the experimental conditons
if stimType == 'w':
    dataFile.write('trialNum,disparityAmplitude,stimulusDuration,stimulusDuration,word1,word2,popOutChoice,correct,background,timeStamp\n')
elif stimType == 'i':
    dataFile.write('trialNum,disparityAmplitude,stimulusDuration,stimulusDuration,image1,image2,popOutChoice,correct,background,timeStamp\n')



## defining our monitor charactersitics so stimili are presented at the correct size

if mode == "test":
    Bmon = monitors.Monitor("backgroundMonitor")
    Bmon.setWidth = (BmonWidthCM)
    Bmon.setSizePix((BmonWidth, BmonHeight))
    Bmon.setDistance(viewDistance)
    Bmon.saveMon()
    mon = monitors.Monitor("testMonitor")
else:
    mon = monitors.Monitor("debugMonitor")

mon.setWidth = (monWidthCM)
mon.setSizePix((monWidth, monHeight))
mon.setDistance(viewDistance)
mon.saveMon()


## Set mode to debug (single monitor) or test (dual monitor)
if mode == "debug":

    winLeft = visual.Window(
        size=[monWidth, monHeight],
        color='grey',
        monitor=mon,
        units="deg",
        screen=1,
        blendMode="add",
        useFBO=True,
        gammaErrorPolicy="ignore",
        fullscr=False)

    mirrorStimulus = False
    if sessionInfo['Anaglyph Type'] == 'cardboard':
        col = colors.Color('#038080','hex').rgb
        col2 = colors.Color('#850505','hex').rgb
    elif sessionInfo['Anaglyph Type'] == 'plastic':
        col = colors.Color('#850080','hex').rgb
        col2 = colors.Color('#308285','hex').rgb


if mode == "test":

    winLeft = visual.Window(
        size=[monWidth, monHeight],
        color=(-.93,-.93,-.93), #this color was used to ensure the black level of virtual content was 1 nit
        colorSpace='rgb',
        monitor=mon,
        units="deg",
        gammaErrorPolicy="warn",
        screen=screenLeft,
        fullscr=True)

    winRight = visual.Window(
        size=[monWidth, monHeight],
        color=(-.93,-.93,-.93),
        colorSpace='rgb',
        monitor=mon,
        units="deg",
        gammaErrorPolicy="warn",
        screen=screenRight,
        fullscr=True)

    winBack = visual.Window(
        size=[BmonWidth, BmonHeight],
        color='black',
        colorSpace='rgb',
        monitor=Bmon,
        units="deg",
        gammaErrorPolicy="warn",
        screen=screenBack,
        fullscr=True)

    mirrorStimulus = True
    col = (1,1,1)



#I had some issues with databases not being created properly if I made the path too complex.
# Because of this, the database file is created in the parent folder rather than the Data subfolder
#not sure if this is a persistent issue or just a weird glitch I experienced
## Make data files for AEPsych


databaseFile = fileName+'.db'


tellFilename = dir+'Data/'+fileName + '.json'
check_file = os.path.isfile(databaseFile)
check_json = os.path.isfile(tellFilename)
oldDataRows = []
tellContent = []

# is db file present?
if check_file:
# what to do if db file is present, but json file isn't?
    if continue_if_data.lower() == 'yes':
        tellContent = loadJSON(tellFilename)
    current_time2 = datetime.now().strftime("%Y_%m_%d_%Hh_%Mm")
    newDatabaseFile = databaseFile[0:-3] + "_" + current_time2 + ".db"
    os.rename(databaseFile, newDatabaseFile)
#could theoretically use some of the code here to continue an in-progress experiment, but I never added this functionality
    if check_json:
        newTellFilename = tellFilename[0:-5]+"-" + current_time2 + ".json"
        os.rename(tellFilename, newTellFilename)
        #os.remove(tellFilename)


number_reduce_trial_runs_bc_restart = len(tellContent)
print("number of tells: ", number_reduce_trial_runs_bc_restart)



## define image to show when AEPsych is warming up
bg_image = dir+'/assets/bg_image.png'
AEP_image = visual.ImageStim(
    win=winLeft,
    name='AEP_image', units='norm',
    image=bg_image, mask=None, anchor='center',
    ori=0.0, pos=(0, 0), size=(2, 2),
    color=[1,1,1], colorSpace='rgb', opacity=None,
    flipHoriz=False, flipVert=False,
    texRes=128.0, interpolate=True, depth=-1.0)



# --- Prepare to start Routine "AEPsychLauch" ---
continueRoutine = True




## Listing our stimulus files
if stimType == 'w':

    nonsensePath = dir + "assets/Words/" + str(loc) + "/Nonsense/" + str(viewDistance) + "/"
    nonsenseWordFiles = os.listdir(nonsensePath)
    wordPath = dir + "assets/Words/" + str(loc) + "/Real/" + str(viewDistance) + "/"
    wordFiles = os.listdir(wordPath)


elif stimType == 'i':
    flowerFiles = os.listdir(dir+'assets/Flowers/Cropped Images')
    birdFiles = os.listdir(dir+'assets/Birds/Cropped Images')



# ==================
# SCREEN CALIBRATION
# ==================
# If ipd_calibration_vernier.py hasn't been run for this participant, use secondary calibration method (faster, but less accurate)

# Defining function to read in most recent calibration data from ipd_correction.csv (should there be one)
def csv_to_binocular_offset(ipd_csv, subject_name, units='pix'):
    if isinstance(ipd_csv, str):
        ipd_csv = pd.read_csv(ipd_csv)
    # Filter by subject name
    subject_data = ipd_csv.query("subject_name==@subject_name")
    # Find the most recent session
    max_session = subject_data['session'].max()
    # Filter by the most recent session
    recent_session_data = subject_data.query("session==@max_session")
    # Calculate the mean binocular offset
    binocular_offset = [
        recent_session_data[f"ipd_correction_{units}_horizontal"].mean(),
        recent_session_data[f"ipd_correction_{units}_vertical"].mean()
    ]
    return binocular_offset

# this ppd calculation has one use: to apply the horizontal and vertical offsets measured during calibration to the instruction text
# I can't define this text in degrees since I don't want the text to change size based on viewing distance, so I use ppd to apply offset in pixels
ppd = math.pi * (monWidth) / math.atan(monWidthCM/viewDistance/2) / 360
constantOffset = constantOffset/60

# I want to access the parent folder of the experiment so I can minimize the amount of manual path editing. The below function is run twice, because the
# first time it only removes the / at the end of the dir path without acutally returning the parent folder
parent = os.path.dirname(dir)
parent = os.path.dirname(parent)

offsetPath = parent + "/haploscope_utils/ipd_correction.csv"
offsets = np.asarray(csv_to_binocular_offset(offsetPath, sessionInfo['participantID']))

print(offsets)

if not math.isnan(offsets[0]):

    #convert offsets from pix to deg. Using pix means we don't have to calculate a different offset for different viewing distances
    offsetHorizontalpx = offsets[0]
    offsetVerticalpx = offsets[1]
    offsets = offsets/ppd
    offsetHorizontal = offsets[0]
    offsetVertical = offsets[1]


else: #perform the backup calibration procedure (aligning an + inside a circle)
    ## Initialize the offset
    ## Initialize offset
    initialOffsetVertical      = -1.8 ## arcmin
    initialOffsetHorizontal    = -1.1 ## arcmin
    offsetHorizontal = initialOffsetHorizontal + round(uniform(-10,10)/10, 1)
    offsetVertical = initialOffsetHorizontal + round(uniform(-10,10)/10, 1)
    print("Initial vertical offset set to " + str(offsetVertical))
    print("Initial horizontal offset set to " + str(offsetHorizontal))
    global finishedOffset


    finishedOffset = False
    ## Allow participant to adjust the offset
    while finishedOffset == False:

        ## Show target icons (circle and +)
        if mode=="debug":
            offsetLeft = visual.TextStim(winLeft, text=u'\u25EF', font="consolas", units='deg', pos=(0,0), height=0.75, wrapWidth=40, color=col, colorSpace='rgb')
            offsetRight = visual.TextStim(winLeft, text="+", font="consolas", units='deg', pos=(offsetHorizontal,offsetVertical+0.1), height=1, wrapWidth=40, color=col2, colorSpace='rgb')
            offsetTextL = visual.TextStim(winLeft, text='Use arrow keys to adjust the plus symbol until it\'s cetered within the circle. \n Press the spacebar when finished.', font="Optimistic Display", units='pix', pos=(0,-(monHeight*.25)), height=50, wrapWidth=monWidth*.75, color=(1,1,1), colorSpace='rgb', flipHoriz=mirrorStimulus)
            offsetLeft.draw()
            offsetRight.draw()
            offsetTextL.draw()
            winLeft.flip()
        elif mode=="test":

            circle = visual.Circle(winLeft, radius=0.5, units='deg', pos=(0,0), fillColor=(1,0,0), lineColor=(1,0,0))
            offsetLeft = visual.TextStim(winLeft, text=u'\u25EF', font="consolas", units='deg', pos=(0,0), height=0.75, wrapWidth=40, color=(1,1,1), colorSpace='rgb')
            offsetRight = visual.TextStim(winRight, text="+", font="consolas", units='deg', pos=(offsetHorizontal,offsetVertical+0.1), height=1, wrapWidth=40, color=(1,1,1), colorSpace='rgb')
            offsetTextL = visual.TextStim(winLeft, text='Use the arrow keys to adjust the plus symbol until it\'s cetered within the circle. \n Press the spacebar when finished.', font="Optimistic Display", units='pix', pos=(0,-(monHeight*.25)), height=50, wrapWidth=monWidth*.75, color=(1,1,1), colorSpace='rgb', flipHoriz=mirrorStimulus)
            offsetTextR = visual.TextStim(winRight, text='Use the arrow keys to adjust the plus symbol until it\'s cetered within the circle. \n Press the spacebar when finished.', font="Optimistic Display", units='pix', pos=(0,-(monHeight*.25)), height=50, wrapWidth=monWidth*.75, color=(1,1,1), colorSpace='rgb', flipHoriz=mirrorStimulus)
            offsetLeft.draw()
            offsetRight.draw()
            offsetTextL.draw()
            offsetTextR.draw()
            winLeft.flip()
            winRight.flip()

            circle.draw()


        ## Check for keypresses and adjust
        keys = event.getKeys()
        if len(keys):
            print(keys)
        if 'up' in keys:
            offsetVertical = offsetVertical+0.1
            print("Vertical offet increased to " + str(offsetVertical))
        if 'down' in keys:
            offsetVertical = offsetVertical-0.1
            print("Vertical offet decreased to " + str(offsetVertical))
        if 'left' in keys and mirrorStimulus == False:
            offsetHorizontal = offsetHorizontal-0.1
            print("Horizontal offet changed to " + str(offsetHorizontal))
        if 'left' in keys and mirrorStimulus == True:
            offsetHorizontal = offsetHorizontal+0.1
            print("Horizontal offet changed to " + str(offsetHorizontal))
        if 'right' in keys and mirrorStimulus == False:
            offsetHorizontal = offsetHorizontal+0.1
            print("Horizontal offet changed to " + str(offsetHorizontal))
        if 'right' in keys and mirrorStimulus == True:
            offsetHorizontal = offsetHorizontal-0.1
            print("Horizontal offet changed to " + str(offsetHorizontal))

        ## When participant presses spacebar, save the offsets and exit
        if 'space' in keys:
            finishedOffset = True
            offsetHorizontalpx = offsetHorizontal*ppd
            offsetVerticalpx = offsetVertical*ppd
            # Add functions to save and record the offset here


backgroundFile_L = dir + 'assets/Backgrounds/Images/_reza_L.png'
backgroundFile_R = dir + 'assets/Backgrounds/Images/_reza_R.png'

if background == 'on':
    backgroundPath = dir + 'assets/Backgrounds/Noise/' + loc + '/' + bgType + '/'

    backgroundFiles = os.listdir(backgroundPath)
    backgroundFile = backgroundPath + backgroundFiles[randrange(0,len(backgroundFiles))]

    #my program was crashing because it was reading in a non-existant background file every once in a while. Now, it re-selects a file every time the non-existant file is chosen
     #this is also a possible issue for text stimuli images. However, I didn't implement a fix like this because I figured out how to get windows to stop generating thumbnails
    while backgroundFile == 'C:/Users/frl/Documents/Margaret River/Time To Fuse/assets/Backgrounds/Noise/lab/deadleaves/Thumbs.db':
       backgroundFile = backgroundPath + backgroundFiles[randrange(0,len(backgroundFiles))]



    if mode == "debug":
        # custom made borders are drawn on top of backgrounds. They have been constructed so that at every viewing distance, the background pattern subtends the same amount of visual field
                #in debug mode, just use border for the furthest viewing distance (which is actually just a completely transparent image)
                #this is because in debug mode, the background distance doesn't move relative to the text stimulus as it does in the haploscope
        borderFile = dir + 'assets/Backgrounds/Borders/100.png'
        backgroundIM = visual.ImageStim(winBack, units="pix", image=backgroundFile, pos=(0,0),contrast=bgContrast)
        borderIM = visual.ImageStim(winBack, units="pix", image=borderFile, pos=(0,0))
    elif mode == "test":
        # custom made borders are drawn on top of backgrounds. They have been constructed so that at every viewing distance, the background pattern subtends the same amount of visual field
        borderFile = dir + 'assets/Backgrounds/Borders/' + str(viewDistance) + '.png'
        backgroundIM = visual.ImageStim(winBack, units="pix", image=backgroundFile, pos=(0,0),contrast=bgContrast)
        borderIM = visual.ImageStim(winBack, units="pix", image=borderFile, pos=(0,0))

        # backgroundIM_R = visual.ImageStim(winRight, units="pix", image=backgroundFile, pos=(0,0),contrast=bgContrast)
        # borderIM_R = visual.ImageStim(winRight, units="pix", image=borderFile, pos=(0,0))


# I could not get my custom tones to play. They were too quiet anyway, so not a big deal
soundPathD = dir + 'assets/Tones/D.wav'
#creating the fixation cross that is presented at the beginning of every trial, prompting the participant to initiate the trial
plusL = visual.TextStim(winLeft, text='+', font="Optimistic Display", units='deg', pos=(offsetHorizontal,offsetVertical), height=1, wrapWidth=monWidth*.75, color=(1,1,1), colorSpace='rgb', flipHoriz=mirrorStimulus)
if mode == 'test':
    plusR = visual.TextStim(winRight, text='+', font="Optimistic Display", units='deg', pos=(0,0), height=1, wrapWidth=monWidth*.75, color=(1,1,1), colorSpace='rgb', flipHoriz=mirrorStimulus)

# =========================================
# SHOW INSTRUCTIONS AND DO PRACTICE SESSION
# =========================================

doneInstructions = False

if practice:

    #Selecting the words to be presented
    if stimType == 'w':
        word1 = wordPath + wordFiles[randrange(0,len(wordFiles))]
        # word2 = nonsensePath + nonsenseWordFiles[randrange(0,len(nonsenseWordFiles))]
        word2 = nonsensePath + nonsenseWordFiles[192]
    elif stimType == 'i':
        image1 = dir + 'assets/Flowers/Cropped Images/' + flowerFiles[randrange(0,len(flowerFiles))]
        image2 = dir + 'assets/Birds/Cropped Images/' + birdFiles[randrange(0,len(birdFiles))]

    #play tone before instructions are shown (mainly to initialize the audio engine)
    #try:
        ##try to play a tone indicating the second interval
        #toneRecorded = sound.Sound(soundPathD)  # 500 Hz beep
        #toneRecorded.play()
    #except Exception as ex:
        #don't play a sound
     #   pass
        #print(ex)

    while doneInstructions == False:


        hpos1 = (hDisparityMagnitude/2)/60
        hpos2 = 0

        #There is no need for VBD on the introductory screen, lets save that for the practice trials
        currentDisparity = 0


        #Blank screen
        if background == "on":
            backgroundIM.draw()
            borderIM.draw()
            # backgroundIM_R.draw()
            #borderIM_R.draw()

            if mode == "test":
                winBack.flip()


        ## Show stimulus example and task instructions
        if mode == "test":
            if stimType == 'w':
                stimRight1 = visual.ImageStim(winRight, image=word1, units='deg', pos=((stimSpacing/2)+offsetHorizontal+hpos1,constantOffset+offsetVertical-currentDisparity/2), color=(1,1,1), colorSpace='rgb', flipHoriz=mirrorStimulus)
                stimRight2 = visual.ImageStim(winRight, image=word2, units='deg', pos=((-stimSpacing/2)+offsetHorizontal+hpos2,constantOffset+offsetVertical-currentDisparity/2), color=(1,1,1), colorSpace='rgb', flipHoriz=mirrorStimulus)
                beginTextR = visual.TextStim(winRight, text='On each trial, one of the two words will pop out (it will appear closer than the other).\nYour task is to identify whether the closer word is real or nonsense.\nPress 1 (the left key) for real or 3 (the right key) for nonsense.\nIn this case, the real word is closer, so the correct answer is 1 (left).\nPress space to start the practice session.', font="Optimistic Display", units='pix', pos=(0+offsetHorizontalpx,offsetVerticalpx-(monHeight*.17)), height=50, wrapWidth=monWidth*.75, color=(1,1,1), colorSpace='rgb', flipHoriz=mirrorStimulus)
            elif stimType == 'i':
                stimRight1 = visual.ImageStim(winRight, image=image1, units='deg', pos=((stimSpacing/2)+offsetHorizontal+hpos1,constantOffset+offsetVertical-currentDisparity/2),size=imageSize,colorSpace='rgb',flipHoriz=mirrorStimulus)
                stimRight2 = visual.ImageStim(winRight, image=image2, units='deg', pos=((-stimSpacing/2)+offsetHorizontal+hpos2,constantOffset+offsetVertical-currentDisparity/2),size=imageSize,colorSpace='rgb',flipHoriz=mirrorStimulus)
                beginTextR = visual.TextStim(winRight, text='On each trial, one of the two images will pop out (it will appear closer than the other).\nYour task is to identify whether the closer image is a flower or a bird.\nPress 1 (the left key) for flower or 3 (the right key) for bird.\nIn this case, the flower is closer, so the correct answer is 1 (left).\nPress space to start the practice session.', font="Optimistic Display", units='pix', pos=(0+offsetHorizontalpx,offsetVerticalpx-(monHeight*.17)), height=50, wrapWidth=monWidth*.75, color=(1,1,1), colorSpace='rgb', flipHoriz=mirrorStimulus)
            beginTextR.draw()
            stimRight1.draw()
            stimRight2.draw()
            winRight.flip()

        elif mode == "debug":
            if stimType == 'w':
                stimRight1 = visual.ImageStim(winLeft, image=word1, units='deg', pos=((stimSpacing/2)+offsetHorizontal+hpos1,constantOffset+offsetVertical-currentDisparity/2), color=col2, colorSpace='rgb', flipHoriz=mirrorStimulus)
                stimRight2 = visual.ImageStim(winLeft, image=word2, units='deg', pos=((-stimSpacing/2)+offsetHorizontal+hpos2,constantOffset+offsetVertical-currentDisparity/2), color=col2, colorSpace='rgb', flipHoriz=mirrorStimulus)
            elif stimType == 'i':
                stimRight1 = visual.ImageStim(winLeft, image=image1, units='deg', pos=((stimSpacing/2)+offsetHorizontal+hpos1,constantOffset+offsetVertical-currentDisparity/2),size=imageSize, color=col2, colorSpace='rgb', flipHoriz=mirrorStimulus)
                stimRight2 = visual.ImageStim(winLeft, image=image2, units='deg', pos=((-stimSpacing/2)+offsetHorizontal+hpos2,constantOffset+offsetVertical-currentDisparity/2),size=imageSize, color=col2, colorSpace='rgb', flipHoriz=mirrorStimulus)
            stimRight1.draw()
            stimRight2.draw()

        if stimType == 'w':
            stimLeft1 = visual.ImageStim(winLeft, image=word1, units='deg', pos=((stimSpacing/2)-hpos1,0+currentDisparity/2), color=col, colorSpace='rgb', flipHoriz=mirrorStimulus)
            stimLeft2 = visual.ImageStim(winLeft, image=word2, units='deg', pos=((-stimSpacing/2)-hpos2,0+currentDisparity/2), color=col, colorSpace='rgb', flipHoriz=mirrorStimulus)
            beginTextL = visual.TextStim(winLeft, text='On each trial, one of the two words will pop out (it will appear closer than the other).\nYour task is to identify whether the closer word is real or nonsense.\nPress 1 (the left key) for real or 3 (the right key) for nonsense.\nIn this case, the real word is closer, so the correct answer is 1 (left).\nPress space to start the practice session.', font="Optimistic Display", units='pix', pos=(0,-(monHeight*.17)), height=50, wrapWidth=monWidth*.75, color=(1,1,1), colorSpace='rgb', flipHoriz=mirrorStimulus)
        elif stimType == 'i':
            stimLeft1 = visual.ImageStim(winLeft, image=image1, units='deg', pos=((stimSpacing/2)-hpos1,0+currentDisparity/2),size=imageSize,color=col, colorSpace='rgb', flipHoriz=mirrorStimulus)
            stimLeft2 = visual.ImageStim(winLeft, image=image2, units='deg', pos=((-stimSpacing/2)-hpos2,0+currentDisparity/2),size=imageSize,color=col, colorSpace='rgb', flipHoriz=mirrorStimulus)
            beginTextL = visual.TextStim(winLeft, text='On each trial, one of the two images will pop out (it will appear closer than the other).\nYour task is to identify whether the closer image is a flower or a bird.\nPress 1 (the left key) for flower or 3 (the right key) for bird.\nIn this case, the flower is closer, so the correct answer is (left).\nPress space to start the practice session.', font="Optimistic Display", units='pix', pos=(0,-(monHeight*.17)), height=50, wrapWidth=monWidth*.75, color=(1,1,1), colorSpace='rgb', flipHoriz=mirrorStimulus)
        beginTextL.draw()
        stimLeft1.draw()
        stimLeft2.draw()
        winLeft.flip()

        ## Check for spacebar keypress
        keys = event.getKeys()
        if 'space' in keys:
             doneInstructions = True
        elif 'q' in keys:
            if mode == 'test':
                winRight.close()
                winBack.close()
            winLeft.close()
            writeJSON(tellContent, tellFilename)
            tellContent = []
            SendExitMessage(AEPsychSocket)
            pAEPsych.kill()
            pAEPsych.terminate()

            core.quit()


# Run 'End Experiment' code from AEPsych
#write out all of the tells to json file
    if easy:
        durRange = (.5, 2)
        dispRange = (0,20)
    else:
        durRange = (.25, 1.5)
        dispRange = (15,60)



    #Show blank screen before practice session
    if background == "on":
        backgroundIM.draw()
        borderIM.draw()

        # backgroundIM_R.draw()
        # # borderIM_R.draw()

    if mode == "test":
        winRight.flip()
        winBack.flip()
    winLeft.flip()


    trialNum = 0

    #Do some practice trials
    while trialNum <= numPracticeTrials:
        trialNum += 1

        #Selecting a random stimulus duration and vertical disparity for each practice trial
        stimulusDuration = uniform(durRange[0],durRange[1])
        currentDisparity = uniform(dispRange[0],dispRange[1])/60


        ##deciding which word will be the real word (left or right?)
        Choice = choice(["A", "B"])
        if Choice == "A":
            if stimType == 'w':
                word1 = wordPath + wordFiles[randrange(0,len(wordFiles))]
                word2 = nonsensePath + nonsenseWordFiles[randrange(0,len(nonsenseWordFiles))]
            elif stimType == 'i':
                image1 = dir + 'assets/Flowers/Cropped Images/' + flowerFiles[randrange(0,len(flowerFiles))]
                image2 = dir + 'assets/Birds/Cropped Images/' + birdFiles[randrange(0,len(birdFiles))]
        else:
            if stimType == 'w':
                word1 = nonsensePath + nonsenseWordFiles[randrange(0,len(nonsenseWordFiles))]
                word2 = wordPath + wordFiles[randrange(0,len(wordFiles))]
            elif stimType == 'i':
                image1 = dir + 'assets/Birds/Cropped Images/' + birdFiles[randrange(0,len(birdFiles))]
                image2 = dir + 'assets/Flowers/Cropped Images/' + flowerFiles[randrange(0,len(flowerFiles))]


        ##deciding which word will pop out (real or nonsense?)
        popOutChoice = choice(['real or flower', 'nonesense or bird'])
        if popOutChoice == 'real or flower':
            if Choice == "A":
                hpos1 = (hDisparityMagnitude/2)/60
                hpos2 = 0
            else:
                hpos1 = 0
                hpos2 = (hDisparityMagnitude/2)/60
        else:
            if Choice == "A":
                hpos1 = 0
                hpos2 = (hDisparityMagnitude/2)/60
            else:
                hpos1 = (hDisparityMagnitude/2)/60
                hpos2 = 0

       #Generating stimuli for the trial
        if stimType == 'w':
            stimLeft1 = visual.ImageStim(winLeft, image=word1, units='deg', pos=((stimSpacing/2)-hpos1,0+currentDisparity/2), colorSpace='rgb', flipHoriz=mirrorStimulus)
            stimLeft2 = visual.ImageStim(winLeft, image=word2, units='deg', pos=((-stimSpacing/2)-hpos2,0+currentDisparity/2), colorSpace='rgb', flipHoriz=mirrorStimulus)
        elif stimType == 'i':
            stimLeft1 = visual.ImageStim(winLeft, image=image1, units='deg', pos=((stimSpacing/2)-hpos1,0+currentDisparity/2),size=imageSize, colorSpace='rgb', flipHoriz=mirrorStimulus)
            stimLeft2 = visual.ImageStim(winLeft, image=image2, units='deg', pos=((-stimSpacing/2)-hpos2,0+currentDisparity/2),size=imageSize, colorSpace='rgb', flipHoriz=mirrorStimulus)

        if mode == "debug":
            if stimType == 'w':
                stimRight1 = visual.ImageStim(winLeft, image=word1, units='deg',pos=((stimSpacing/2)+offsetHorizontal+hpos1,constantOffset+offsetVertical-currentDisparity/2), color=col2, colorSpace='rgb', flipHoriz=mirrorStimulus)
                stimRight2 = visual.ImageStim(winLeft, image=word2, units='deg',pos=((-stimSpacing/2)+offsetHorizontal+hpos2,constantOffset+offsetVertical-currentDisparity/2),color=col2, colorSpace='rgb', flipHoriz=mirrorStimulus)
            elif stimType == 'i':
                stimRight1 = visual.ImageStim(winLeft, image=image1, units='deg', pos=((stimSpacing/2)+offsetHorizontal+hpos1,constantOffset+offsetVertical-currentDisparity/2),size=imageSize, color=col2, colorSpace='rgb', flipHoriz=mirrorStimulus)
                stimRight2 = visual.ImageStim(winLeft, image=image2, units='deg', pos=((-stimSpacing/2)+offsetHorizontal+hpos2,constantOffset+offsetVertical-currentDisparity/2),size=imageSize, color=col2, colorSpace='rgb', flipHoriz=mirrorStimulus)
            stimLeft1.color = col
            stimLeft2.color = col
        elif mode == 'test':
            stimRight1 = stimLeft1
            stimRight2 = stimLeft2

        #Blank screen
        if background == "on":
            backgroundIM.draw()
            # borderIM_L.draw()

            # backgroundIM_R.draw()
            # borderIM_R.draw()
        if mode == "test":
            winBack.flip()
            winRight.flip()
        winLeft.flip()

        #drawing fixation cross, awaiting the participat's initiation of the trial
        # backgroundIM_L.draw()
        # borderIM_L.draw()

        # backgroundIM_R.draw()
        # borderIM_R.draw()
        plusL.draw()
        winLeft.flip()
        if mode == 'test':
            plusR.draw()
            winRight.flip()
        responseKey = event.waitKeys(keyList=["space","q"])
        if "q" in responseKey:
            trialNum = numPracticeTrials+1
            break

        #try:
            ##try to play a tone indicating the second interval
            #toneRecorded = sound.Sound(soundPathD)  # 500 Hz beep
            #toneRecorded.play()
        #except Exception as ex:
            #don't play a sound
            #print(ex)
            #pass


        #commencing the draw loop
        startTime = core.getTime()
        endTime = startTime + stimulusDuration

        exit = False


        while exit == False:
            if background == "on":
                backgroundIM.draw()
                borderIM.draw()

                # backgroundIM_R.draw()
                # borderIM_R.draw()
                if mode == "test":
                    winBack.flip()
            if mode == "test":



                keys = event.getKeys()
                if len(keys):
                    print(keys)
                if 'v' in keys:
                    hpos1 = hpos1+0.01
                    print("horizontsl offet increased to " + str(hpos1*60))
                if 'b' in keys:
                    hpos1 = hpos1-0.01
                    print("horizontsl offet decreased to " + str(hpos1*60))

                if 'n' in keys:
                    currentDisparity = currentDisparity-0.01
                    print("Vertical offet decreased to " + str(currentDisparity*60))
                if 'm' in keys:
                    currentDisparity = currentDisparity+0.01
                    print("Vertical offet decreased to " + str(currentDisparity*60))

                if 'r' in keys:
                    currentDisparity = 0
                    hpos1 = 0
                    print("Vertical offet decreased to " + str(currentDisparity*60))
                    print("horizontsl offet increased to " + str(hpos1*60))

                if 'q' in keys:
                    exit = True



                # print("currentDisparity " + str(currentDisparity))



                stimRight1.pos = ((stimSpacing/2)+offsetHorizontal+hpos1,constantOffset+offsetVertical-currentDisparity/2)
                stimRight1.draw(winRight)
                stimRight2.pos = ((-stimSpacing/2)+offsetHorizontal+hpos2,constantOffset+offsetVertical-currentDisparity/2)
                # stimRight2.draw(winRight)


            stimLeft1.pos = ((stimSpacing/2)-hpos1,0+currentDisparity/2)
            stimLeft1.draw(winLeft)
            stimLeft2.pos = ((-stimSpacing/2)-hpos2,0+currentDisparity/2)
            # stimLeft2.draw(winLeft)
            winLeft.flip()
            if mode == 'test':
                winRight.flip()


            ## Move on to the response dialog

        #Blank screen
        if background == "on":
            backgroundIM.draw()
            borderIM.draw()
            # backgroundIM_R.draw()
            # borderIM_R.draw()
        if mode == "test":
            winBack.flip()
            winRight.flip()
        winLeft.flip()
        #core.wait(0.2)


        #Reminding the participants of the controls
        if stimType == "w":
            reminderText = "left = real word, right = nonsense word"
        elif stimType == "i":
            reminderText = "left = flower, right = bird"

        if background == "on":
            backgroundIM. draw()
            borderIM.draw()
        if mode == "test":
            textRight = visual.TextStim(winRight, text=reminderText, font="Optimistic Display", units='deg', pos=(offsetHorizontal,offsetVertical), height=1, wrapWidth=40, color=(1,1,1), colorSpace='rgb', flipHoriz=mirrorStimulus)
            textRight.draw()
            winRight.flip()
            winBack.flip()
        textLeft = visual.TextStim(winLeft, text=reminderText, font="Optimistic Display", units='deg', pos=(0,0), height=1, wrapWidth=40, color=(1,1,1), colorSpace='rgb', flipHoriz=mirrorStimulus)
        textLeft.draw()
        winLeft.flip()


        #Wait for response
        responseKey = event.waitKeys(keyList=["q","num_1","num_3","1","3"])
        if "q" in responseKey:
            trialNum = numPracticeTrials+1
            break
        elif ("num_1" in responseKey or "1" in responseKey) and "real or flower" in popOutChoice:
            currentResponse = 1
            print("Correct response")
        elif ("num_3" in responseKey or "3" in responseKey) and "nonesense or bird" in popOutChoice:
            currentResponse = 1
            print("Correct response")
        else:
            currentResponse = 0
            print("Incorrect response")


        #Showing whether the participant was right or not after the trial
        if currentResponse == 1:
            resultText = 'Correct'
        else:
            resultText = 'Incorrect'


        #Showing feedback at the end of the trial (was the participant right or wrong?)
        if mode == "debug":
            if background == "on":
                backgroundIM.draw()
                borderIM.draw()
            resultTextL = visual.TextStim(winLeft, text=resultText, font="Optimistic Display", units='deg', pos=(0,0), height=1, wrapWidth=40, color=(1,1,1), colorSpace='rgb', flipHoriz=mirrorStimulus)
            resultTextL.draw()
            winLeft.flip()
        elif mode == "test":
            if background == "on":
                backgroundIM.draw()
                borderIM.draw()
            resultTextL = visual.TextStim(winLeft, text=resultText, font="Optimistic Display", units='deg', pos=(0,0), height=1, wrapWidth=40, color=(1,1,1), colorSpace='rgb', flipHoriz=mirrorStimulus)
            resultTextR = visual.TextStim(winRight, text=resultText, font="Optimistic Display", units='deg', pos=(0+offsetHorizontal,0+offsetVertical), height=1, wrapWidth=40, color=(1,1,1), colorSpace='rgb', flipHoriz=mirrorStimulus)
            resultTextR.draw()
            resultTextL.draw()
            winLeft.flip()
            winRight.flip()
            winBack.flip()


    #practic session over text
    if mode == "debug":
        if background == "on":
            backgroundIM.draw()
            borderIM.draw()
        resultTextL = visual.TextStim(winLeft, text="Practice Session Over!", font="Optimistic Display", units='deg', pos=(0,0), height=1, wrapWidth=40, color=(1,1,1), colorSpace='rgb', flipHoriz=mirrorStimulus)
        resultTextL.draw()
        winLeft.flip()

    elif mode == "test":
        if background == "on":
            backgroundIM.draw()
            borderIM.draw()
        resultTextL = visual.TextStim(winLeft, text="Practice Session Over!", font="Optimistic Display", units='deg', pos=(0,0), height=1, wrapWidth=40, color=(1,1,1), colorSpace='rgb', flipHoriz=mirrorStimulus)
        resultTextR = visual.TextStim(winRight, text="Practice Session Over!", font="Optimistic Display", units='deg', pos=(0+offsetHorizontal,0+offsetVertical), height=1, wrapWidth=40, color=(1,1,1), colorSpace='rgb', flipHoriz=mirrorStimulus)
        resultTextR.draw()
        resultTextL.draw()
        winLeft.flip()
        winRight.flip()
        winBack.flip()

    core.wait(2)



# ===========================
# WAIT FOR SPACEBAR KEYPRESS
# ===========================

#Begin the actual experiment
readyToStart = False
while readyToStart == False:

    #Prompt user to press spacebar
    if mode == "debug":
        if background == "on":
            backgroundIM.draw()
            borderIM.draw()
        beginTextL = visual.TextStim(winLeft, text='Press the spacebar to begin', font="Optimistic Display", units='deg', pos=(0,0), height=1, wrapWidth=40, color=(1,1,1), colorSpace='rgb', flipHoriz=mirrorStimulus)
        beginTextL.draw()
        winLeft.flip()
        core.wait(.5)
    elif mode == "test":
        if background == "on":
            backgroundIM.draw()
            borderIM.draw()
        beginTextL = visual.TextStim(winLeft, text='Press the spacebar to begin', font="Optimistic Display", units='deg', pos=(0,0), height=1, wrapWidth=40, color=(1,1,1), colorSpace='rgb', flipHoriz=mirrorStimulus)
        beginTextR = visual.TextStim(winRight, text='Press the spacebar to begin', font="Optimistic Display", units='deg', pos=(0+offsetHorizontal,0+offsetVertical), height=1, wrapWidth=40, color=(1,1,1), colorSpace='rgb', flipHoriz=mirrorStimulus)
        beginTextR.draw()
        beginTextL.draw()
        winLeft.flip()
        winRight.flip()
        winBack.flip()

    ## Check for spacebar keypress
    keys = event.getKeys()
    if 'space' in keys:
        readyToStart = True
    elif 'q' in keys:
        if mode == 'test':
            winRight.close()
            winBack.close()
        winLeft.close()
        writeJSON(tellContent, tellFilename)
        tellContent = []
        SendExitMessage(AEPsychSocket)
        pAEPsych.kill()
        pAEPsych.terminate()
        core.quit()

#Blank screen
if background == "on":
    backgroundIM.draw()
    borderIM.draw()
if mode == "test":
    winRight.flip()
    winBack.flip()
winLeft.flip()



# continueRoutine = True
# #Intialize trial counter
# trialNum = 0

# while continueRoutine:


#     trialNum += 1
#     continueRoutine = True
#     # ask AEPsych for first parameters. This really just sets up the dictionary
#     SendAskMessage(AEPsychSocket)

#     #Read the parameters from the server
#     #Also convert from byte string to dict
#     AEPsychTrialParameters = SocketRecvMessage(AEPsychSocket)
#     AEPsychTrialParameters = json.loads(AEPsychTrialParameters)

#     #Getting parameters from AEPsych
#     stimulusDuration = float(AEPsychTrialParameters['config']['stimulusDuration'][0])
#     disparityAmplitude = float(AEPsychTrialParameters['config']['disparityAmplitude'][0])
#     currentDisparity = disparityAmplitude/60 #divide by 60 to convert disparity into dva



#     #if is_finished": server.strat.finished
#     # we want out.
#     if(AEPsychTrialParameters['is_finished']):
#         continueRoutine = False # end the current routine



#     ##deciding which word will be the real word (left or right?)
#     Choice = choice(["A", "B"])
#     if Choice == "A":
#         if stimType == 'w':
#             word1 = wordPath + wordFiles[randrange(0,len(wordFiles))]
#             word2 = nonsensePath + nonsenseWordFiles[randrange(0,len(nonsenseWordFiles))]
#         elif stimType == 'i':
#             image1 = dir + 'assets/Flowers/Cropped Images/' + flowerFiles[randrange(0,len(flowerFiles))]
#             image2 = dir + 'assets/Birds/Cropped Images/' + birdFiles[randrange(0,len(birdFiles))]
#     else:
#         if stimType == 'w':
#             word1 = nonsensePath + nonsenseWordFiles[randrange(0,len(nonsenseWordFiles))]
#             word2 = wordPath + wordFiles[randrange(0,len(wordFiles))]
#         elif stimType == 'i':
#             image1 = dir + 'assets/Birds/Cropped Images/' + birdFiles[randrange(0,len(birdFiles))]
#             image2 = dir + 'assets/Flowers/Cropped Images/' + flowerFiles[randrange(0,len(flowerFiles))]

#     ##deciding which word will pop out (real or nonsense?)
#     popOutChoice = choice(['real or flower', 'nonesense or bird'])
#     if popOutChoice == 'real or flower':
#         if Choice == "A":
#             hpos1 = (hDisparityMagnitude/2)/60
#             hpos2 = 0
#         else:
#             hpos1 = 0
#             hpos2 = (hDisparityMagnitude/2)/60
#     else:
#         if Choice == "A":
#             hpos1 = 0
#             hpos2 = (hDisparityMagnitude/2)/60
#         else:
#             hpos1 = (hDisparityMagnitude/2)/60
#             hpos2 = 0


#         ## Blank screen
#     if background == "on":
#         backgroundIM.draw()
#         borderIM.draw()
#     if mode == "test":
#         winBack.flip()
#         winRight.flip()
#     winLeft.flip()


#     #generating stimuli for the trial
#     if stimType == 'w':
#         stimLeft1 = visual.ImageStim(winLeft, image=word1, units='deg', pos=((stimSpacing/2)-hpos1,0+currentDisparity/2), colorSpace='rgb', flipHoriz=mirrorStimulus)
#         stimLeft2 = visual.ImageStim(winLeft, image=word2, units='deg', pos=((-stimSpacing/2)-hpos2,0+currentDisparity/2), colorSpace='rgb', flipHoriz=mirrorStimulus)
#     elif stimType == 'i':
#         stimLeft1 = visual.ImageStim(winLeft, image=image1, units='deg', pos=((stimSpacing/2)-hpos1,0+currentDisparity/2),size=imageSize, colorSpace='rgb', flipHoriz=mirrorStimulus)
#         stimLeft2 = visual.ImageStim(winLeft, image=image2, units='deg', pos=((-stimSpacing/2)-hpos2,0+currentDisparity/2),size=imageSize, colorSpace='rgb', flipHoriz=mirrorStimulus)

#     if mode == "debug":
#         if stimType == 'w':
#             stimRight1 = visual.ImageStim(winLeft, image=word1, units='deg',pos=((stimSpacing/2)+offsetHorizontal+hpos1,constantOffset+offsetVertical-currentDisparity/2), color=col2, colorSpace='rgb', flipHoriz=mirrorStimulus)
#             stimRight2 = visual.ImageStim(winLeft, image=word2, units='deg',pos=((-stimSpacing/2)+offsetHorizontal+hpos2,constantOffset+offsetVertical-currentDisparity/2),color=col2, colorSpace='rgb', flipHoriz=mirrorStimulus)
#         elif stimType == 'i':
#             stimRight1 = visual.ImageStim(winLeft, image=image1, units='deg', pos=((stimSpacing/2)+offsetHorizontal+hpos1,constantOffset+offsetVertical-currentDisparity/2),size=imageSize, color=col2, colorSpace='rgb', flipHoriz=mirrorStimulus)
#             stimRight2 = visual.ImageStim(winLeft, image=image2, units='deg', pos=((-stimSpacing/2)+offsetHorizontal+hpos2,constantOffset+offsetVertical-currentDisparity/2),size=imageSize, color=col2, colorSpace='rgb', flipHoriz=mirrorStimulus)
#         stimLeft1.color = col
#         stimLeft2.color = col
#     elif mode == 'test':
#         stimRight1 = stimLeft1
#         stimRight2 = stimLeft2


#     #try:
#         ##try to play a tone indicating the second interval
#         #toneRecorded = sound.Sound(soundPathD)  # 500 Hz beep
#         #toneRecorded.play()
#     #except Exception as ex:
#         #don't play a sound
#         #print(ex)
#        # pass

#     #Draw fixation cross, wait for participant to initiate trial
#     backgroundIM.draw()
#     borderIM.draw()
#     plusL.draw()
#     winLeft.flip()
#     if mode == 'test':
#         plusR.draw()
#         winRight.flip()
#     responseKey = event.waitKeys(keyList=["space","q"])
#     if "q" in responseKey:
#         continueRoutine = False
#         break

#     #the draw loop
#     startTime = core.getTime()
#     endTime = startTime + stimulusDuration
#     while core.getTime() < endTime:
#         if background == "on":
#             backgroundIM.draw()
#             borderIM.draw()
#             if mode == "test":
#                 winBack.flip()
#         if mode == "test":
#             stimRight1.pos = ((stimSpacing/2)+offsetHorizontal+hpos1,constantOffset+offsetVertical-currentDisparity/2)
#             stimRight1.draw(winRight)
#             stimRight2.pos = ((-stimSpacing/2)+offsetHorizontal+hpos2,constantOffset+offsetVertical-currentDisparity/2)
#             stimRight2.draw(winRight)
#         elif mode == "debug":
#             stimRight1.pos = ((stimSpacing/2)+offsetHorizontal+hpos1,constantOffset+offsetVertical-currentDisparity/2)
#             stimRight1.draw()
#             stimRight2.pos = ((-stimSpacing/2)+offsetHorizontal+hpos2,constantOffset+offsetVertical-currentDisparity/2)
#             stimRight2.draw()
#         stimLeft1.pos = ((stimSpacing/2)-hpos1,0+currentDisparity/2)
#         stimLeft1.draw(winLeft)
#         stimLeft2.pos = ((-stimSpacing/2)-hpos2,0+currentDisparity/2)
#         stimLeft2.draw(winLeft)
#         winLeft.flip()
#         if mode == 'test':
#             winRight.flip()


#     ## Move on to the response dialog
#     #Blank screen
#     if background == "on":
#         backgroundIM.draw()
#         borderIM.draw()
#     if mode == "test":
#         winBack.flip()
#         winRight.flip()
#     winLeft.flip()


#     #Wait for response
#     responseKey = event.waitKeys(keyList=["q","num_1","num_3","1","3"])
#     if "q" in responseKey:
#         continueRoutine = False
#         break
#     elif ("num_1" in responseKey or "1" in responseKey) and "real or flower" in popOutChoice:
#         currentResponse = 1
#         print("Correct response")
#     elif ("num_3" in responseKey or "3" in responseKey) and "nonesense or bird" in popOutChoice:
#         currentResponse = 1
#         print("Correct response")
#     else:
#         currentResponse = 0
#         print("Incorrect response")

#     print(trialNum)

#     #Tell the AEPsych server our outcome for this iteration
#     SendTellMessage(AEPsychSocket, AEPsychTrialParameters, currentResponse)
#     #Server will send "acq" if the tell message went well

#     print("Server Response: " + SocketRecvMessage(AEPsychSocket))

#     #Add trial info to the data file
#     timeStamp = data.getDateStr(format="%H%M%S")
#     if background != 'on':
#         backgroundFile = 'none'

#     if stimType == 'w':
#         dataFile.write('%i,%.3f,%.3f,%s,%s,%s,%i,%s,%s\n' %(trialNum, disparityAmplitude, stimulusDuration, word1, word2, popOutChoice, currentResponse,backgroundFile,timeStamp))
#     elif stimType == 'i':
#         dataFile.write('%i,%.3f,%.3f,%s,%s,%s,%i,%s,%s\n' %(trialNum, disparityAmplitude, stimulusDuration, image1, image2, popOutChoice, currentResponse,backgroundFile,timeStamp))

#     # core.wait(.2) %It takes so long to draw the text stimuli that theres no need to add any extra time



# # ## Close the data file
# dataFile.close()


# ## End the experiment
if mode == "debug":
    core.wait(1)
    endExperiment = visual.TextStim(winLeft, text='End of experiment. Thanks!', font="Optimistic Display", units='deg', pos=(0,0), height=1, wrapWidth=40, color=(1,1,1), colorSpace='rgb', flipHoriz=mirrorStimulus)
    endExperiment.draw()
    winLeft.flip()
    core.wait(5)
elif mode=="test":
    core.wait(1)
    endLeft = visual.TextStim(winLeft, text='End of experiment. Thanks!', font="Optimistic Display", units='deg', pos=(0,0), height=1, wrapWidth=40, color=(1,1,1), colorSpace='rgb', flipHoriz=mirrorStimulus)
    endRight = visual.TextStim(winRight, text="End of experiment. Thanks!", font="Optimistic Display", units='deg', pos=(offsetHorizontal,offsetVertical), height=1, wrapWidth=40, color=(1,1,1), colorSpace='rgb', flipHoriz=mirrorStimulus)
    endLeft.draw()
    endRight.draw()
    winLeft.flip()
    winRight.flip()
    winBack.flip()
    core.wait(5)
    winRight.close()
    winBack.close()
winLeft.close()


# Run 'End Experiment' code from AEPsych
#write out all of the tells to json file
writeJSON(tellContent, tellFilename)
tellContent = []


# Run 'End Experiment' code from end_message_log
#Find a way to kill aepsych and even launch aepsych better
SendExitMessage(AEPsychSocket)

pAEPsych.kill()
pAEPsych.terminate()


core.quit()
