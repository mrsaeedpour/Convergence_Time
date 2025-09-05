########
# This script displays the screen numbers assigned by psychopy to a given screen on said screen
# Necessary because python changes these numbers every time a monitor is turned off or unplugged 
# For multi-monitor psychopy experiments, this is a usefuly tool 
# Press q or space to end the program once screen numbers have been noted
#
#
#
######


from psychopy import core, event, visual

win0 = visual.Window(
    color='black', 
    screen=0,
    fullscr=True,
    monitor="zero" 
    )

win1 = visual.Window(
    color='black', 
    screen=1,
    fullscr=True,
    monitor="one" 
    )

win2 = visual.Window(
    color='black', 
    screen=2,
    fullscr=True,
    monitor="two" 
    )

win3 = visual.Window(
    color='black', 
    screen=3,
    fullscr=True,
    monitor="three" 
    )

zero = visual.TextStim(win0, text='0', font="consolas", units='pix', pos=(0,0), height=1000, wrapWidth=40, color=(1,1,1), colorSpace='rgb')
one = visual.TextStim(win1, text='1', font="consolas", units='pix', pos=(0,0), height=1000, wrapWidth=40, color=(1,1,1), colorSpace='rgb')
two = visual.TextStim(win2, text='2', font="consolas", units='pix', pos=(0,0), height=1000, wrapWidth=40, color=(1,1,1), colorSpace='rgb')
three = visual.TextStim(win3, text='3', font="consolas", units='pix', pos=(0,0), height=1000, wrapWidth=40, color=(1,1,1), colorSpace='rgb')

identify = True

while identify == True:
    zero.draw()
    one.draw()
    two.draw()
    three.draw()
    win0.flip()
    win1.flip()
    win2.flip()
    win3.flip()

    responseKey = event.waitKeys(keyList=["q","space"])
    if "q" in responseKey or "space" in responseKey:
        identify = False
        break

win0.close()
win1.close()
win2.close()
win3.close()
core.quit
       