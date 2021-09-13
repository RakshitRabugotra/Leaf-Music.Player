# Modules for UI
from tkinter import *
from tkinter import filedialog
# Modules for backend
import time
import pygame
from pygame import mixer
from mutagen import mp3 as mp


BACKGROUND_COLOR = "#001B2B"
FOREGROUND_COLOR = "#A61651"

BUTTON_BACKGROUND_COLOR = "#4a62d9"

"""
FOREGROUND -> #301869, #6326e2
BACKGROUND -> #134b72, #848c8c, #4a62d9
"""


class MusicPlayer:
    def __init__(self, window):
        # Setting up the tkinter window
        window.geometry('420x120')
        window.title('Leaf Player')
        window.resizable(0, 0)
        window.config(bg=BACKGROUND_COLOR)
        self.window = window

        # Booleans
        self.musicFile = False
        self.playingState = False

        # Integers
        self.audioLength = 0

        # Strings
        self.defaultStatus = "Load a file to play!"
        self.playingTime = "--:--:--"
        self.totalTime = "--:--:--"
        self.audioFileTitle = ""

        # Setting up Buttons
        Load = Button(window, relief=GROOVE, borderwidth=0, activebackground=FOREGROUND_COLOR, text='Load', width=12, bg=BUTTON_BACKGROUND_COLOR, fg=FOREGROUND_COLOR, font=('Helvetica', 12, 'bold'), command=self.load)
        Pause = Button(window, relief=GROOVE, borderwidth=0, activebackground=FOREGROUND_COLOR, text='Pause/Play', bg=BUTTON_BACKGROUND_COLOR, width=12, fg=FOREGROUND_COLOR, font=('Helvetica', 12, 'bold'), command=self.pause)
        Stop = Button(window, relief=GROOVE, borderwidth=0, activebackground=FOREGROUND_COLOR, text='Stop', width=12, bg=BUTTON_BACKGROUND_COLOR, fg=FOREGROUND_COLOR, font=('Helvetica', 12, 'bold'), command=self.stop)
        Load.place(x=30, y=24)
        Pause.place(x=156, y=24)
        Stop.place(x=276, y=24)
        # Setting up Buttons for global use across the Class
        self.Load, self.Pause, self.Stop = Load, Pause, Stop

        # Setting up Status Label
        self.StatusLabel = Label(window, text=self.defaultStatus, fg=FOREGROUND_COLOR, font=('Helvetica', 12, 'bold'), anchor=W)
        self.StatusLabel.pack(side=BOTTOM, fill=X)

        # Deciding the state of buttons
        self.decideButtonState()

    def load(self):
        self.musicFile = filedialog.askopenfilename()
        if self.musicFile:
            # Initializing Audio File
            mp3 = mp.MP3(self.musicFile)
            mixer.init(frequency=mp3.info.sample_rate)

            # Getting the title of audio file
            self.audioFileTitle = self.musicFile.split('/')[-1]
            self.window.title(self.audioFileTitle)

            # Fetching Audio File length in "HH:MM:SS" format
            self.audioLength = mp3.info.length
            self.totalTime = time.strftime('%H:%M:%S', time.gmtime(self.audioLength))

            # Loading is successful
            # Setting up the duration
            self.changeStatus(msg="File loaded successfully...", after_text="00:00:00/{}".format(self.totalTime))

            # Play the audio file automatically
            self.play()
        elif self.playingState:
            pass
        else:
            # Loading is interrupted
            self.changeStatus(msg="No File selected, cannot proceed...")
        # Change the states of control buttons
        self.decideButtonState()

    def play(self):
        # Loading the file into mixer
        mixer.music.load(self.musicFile)
        mixer.music.play()
        self.Pause['text'] = "Pause"

        # Changing the playing state
        self.playingState = True

        # Starting the recursive time counter
        self.timeElapsed()

    def pause(self):
        if not self.playingState:
            mixer.music.pause()
            self.playingState = True
            self.Pause['text'] = "Pause"
        else:
            mixer.music.unpause()
            self.playingState = False
            self.Pause['text'] = "Play"

    def stop(self):
        # Stopping the mixer
        mixer.music.stop()

    def timeElapsed(self):
        try:
            # Fetching time elapsed playing the audio file
            currentTime = mixer.music.get_pos() // 1000
            # Converting the time fetch (in 'int') to string like "HH:MM:SS"
            self.playingTime = time.strftime('%H:%M:%S', time.gmtime(currentTime))

            # Format => "--:--:--/--:--:--"
            duration = self.playingTime+'/'+self.totalTime
            # Displaying play time on screen using status label
            self.changeStatus(msg=duration, after=False)

            # Increase current time by 1 second
            currentTime += 1

            if currentTime != self.audioLength: self.window.after(1000, self.timeElapsed)
        except pygame.error:
            return

    def changeStatus(self, _type=None, msg=None, after=True, after_text=None):
        if msg is None: msg = self.defaultStatus
        if _type is not None:
            if isinstance(_type, str): msg = _type + " " + msg
            else: raise TypeError("Expected 'str' got '{}' instead...".format(_type.__class__))

        self.StatusLabel['text'] = msg
        if after:
            self.window.after(1000, lambda:self.StatusLabel.config(text=self.defaultStatus if after_text is None else after_text))

    def decideButtonState(self):
        if self.musicFile or self.playingState:
            self.Pause.config(state=NORMAL) 
            self.Stop.config(state=NORMAL)
        else:
            self.Pause.config(state=DISABLED) 
            self.Stop.config(state=DISABLED)

root = Tk()
app = MusicPlayer(root)
root.mainloop()