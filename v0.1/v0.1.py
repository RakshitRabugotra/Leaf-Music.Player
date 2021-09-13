# Modules for UI
from tkinter import *
from tkinter import filedialog, messagebox
# Modules for backend
import time
import pygame
from pygame import mixer
from mutagen import mp3 as mp


BACKGROUND_COLOR = "#001B2B"

BUTTON_BACKGROUND_COLOR = "#0E3D8B"
BUTTON_FOREGROUND_COLOR = "#2B8EE2"

STATUS_FOREGROUND_COLOR = "#FFFFFE"
STATUS_BACKGROUND_COLOR = "#001B2B"

BUTTON_BORDER_WIDTH = 0

"""
FOREGROUND -> #301869, #6326e2, 
BACKGROUND -> #134b72, #848c8c, #4a62d9, #001B2B
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

        # MP3 and mixer obejcts
        self.mp3 = None

        # Strings
        self.defaultStatus = "Load a file to play!"
        self.playingTime = "--:--:--"
        self.totalTime = "--:--:--"
        self.audioFileTitle = ""

        # Setting up Buttons
        Load = Button(window, relief=GROOVE, borderwidth=BUTTON_BORDER_WIDTH, activebackground=BUTTON_FOREGROUND_COLOR, text='Load', width=12, bg=BUTTON_BACKGROUND_COLOR, fg=BUTTON_FOREGROUND_COLOR, font=('Helvetica', 12, 'bold'), command=self.load)
        Pause = Button(window, relief=GROOVE, borderwidth=BUTTON_BORDER_WIDTH, activebackground=BUTTON_FOREGROUND_COLOR, text='Pause/Play', width=12, bg=BUTTON_BACKGROUND_COLOR, fg=BUTTON_FOREGROUND_COLOR, font=('Helvetica', 12, 'bold'), command=self.pause)
        Stop = Button(window, relief=GROOVE, borderwidth=BUTTON_BORDER_WIDTH, activebackground=BUTTON_FOREGROUND_COLOR, text='Stop', width=12, bg=BUTTON_BACKGROUND_COLOR, fg=BUTTON_FOREGROUND_COLOR, font=('Helvetica', 12, 'bold'), command=self.stop)

        # Quit Button
        Button(window, relief=GROOVE, borderwidth=BUTTON_BORDER_WIDTH, activebackground=BUTTON_FOREGROUND_COLOR, text='Quit', width=34, bg=BUTTON_BACKGROUND_COLOR, fg=BUTTON_FOREGROUND_COLOR, font=('Helvetica', 12, 'bold'), command=lambda:self.window.quit() if messagebox.askyesno("Quit to Windows", "Do you want to exit?") else "").place(x=42, y=56)

        # Placing the buttons
        Load.place(x=30, y=24)
        Pause.place(x=156, y=24)
        Stop.place(x=276, y=24)
        # Setting up Buttons for global use across the Class
        self.Load, self.Pause, self.Stop = Load, Pause, Stop

        # Setting up Status Label
        self.StatusLabel = Label(window, text=self.defaultStatus, bg=STATUS_BACKGROUND_COLOR, fg=STATUS_FOREGROUND_COLOR, font=('Helvetica', 12, 'italic'), anchor=W)
        self.StatusLabel.pack(side=BOTTOM, fill=X)

        # Deciding the state of buttons
        self.decideButtonState()

    def load(self):
        self.musicFile = filedialog.askopenfilename(filetypes=[("Audio file (.MP3/ .OGG/ .WAV)", ".mp3 .ogg .wav"), ("All files", "*")])
        if self.musicFile:
            # Initializing Audio File
            mp3 = mp.MP3(self.musicFile)
            self.mp3 = mp3
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
        if self.playingState:
            mixer.music.pause()
            self.playingState = False
            self.Pause['text'] = "Play"
            self.window.title(self.audioFileTitle+" (Paused)")
        else:
            if mixer.music.get_pos()//1000 == -1:
                # The Music has stopped and file should be rewinded (begin from start 00:00:00)
                mixer.music.rewind()
                # Playing the audio file
                mixer.music.play()
            else:
                # Try unpausing the file if it is not playing
                mixer.music.unpause()

            self.playingState = True
            self.Pause['text'] = "Pause"
            self.window.title(self.audioFileTitle)

    def stop(self):
        # Stopping the mixer
        mixer.music.stop()
        if mixer.music.get_pos()//1000 == -1:
            # Changin the playing state var
            self.playingState = False
            # Changing the text on Label to 'Play'
            self.Pause['text'] = 'Play'
            # Changing the status to Stopped
            self.changeStatus(msg="00:00:00/"+self.totalTime+" (Music Stopped)", after=False)


    def timeElapsed(self):
        if mixer.music.get_pos() != -1:
            # Fetching time elapsed playing the audio file
            currentTime = mixer.music.get_pos() // 1000
            # Converting the time fetch (in 'int') to string like "HH:MM:SS"
            self.playingTime = time.strftime('%H:%M:%S', time.gmtime(currentTime))

            # Format => "--:--:--/--:--:--"
            duration = self.playingTime+'/'+self.totalTime
            # Displaying play time on screen using status label
            self.changeStatus(msg=duration, after=False)

            if self.playingState:
                # Increase current time by 1 second
                currentTime += 1
            else:
                self.changeStatus(msg=duration+" (Music Paused)", after=False)
        self.window.after(1000, self.timeElapsed)
        

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
