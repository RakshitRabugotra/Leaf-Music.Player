# Modules for UI
from tkinter import *
from tkinter import filedialog, messagebox, ttk
# Modules for backend
import os
import time
import pygame
from pygame import mixer
from mutagen import mp3 as mp
from mutagen import MutagenError


BACKGROUND_COLOR = "#001B2B"

# Default Title
TITLE = "Leaf Player (V.0.2)"

# Label border width
LABEL_BORDER_WIDTH = 2

# Button width
BUTTON_WIDTH = 25

# Button background & foreground color
BUTTON_BACKGROUND_COLOR = "#0E3D8B"
BUTTON_FOREGROUND_COLOR = "#2B8EE2"

# Button hover background & foreground color
BUTTON_HOVER_BACKGROUND_COLOR = "#2B8EE2"
BUTTON_HOVER_FOREGROUND_COLOR = "#0E3D8B"

# Status button background and & foregrounf color
STATUS_FOREGROUND_COLOR = "#FFFFFE"
STATUS_BACKGROUND_COLOR = "#001B2B"

# Button active background & foreground color
BUTTON_ACTIVE_BACKGROUND_COLOR = "#9400d3"
BUTTON_ACTIVE_FOREGROUND_COLOR = BUTTON_FOREGROUND_COLOR

# Button border width
BUTTON_BORDER_WIDTH = 0

# Global background & foreground color
GLOBAL_BACKGROUND_COLOR = "#d7dade"
GLOBAL_FOREGROUND_COLOR = "#4f5154"

# Global Font familiy & size
GLOBAL_FONT_FAMILY = "Open Sans"
GLOBAL_FONT_SIZE = 10
BOLD = 'bold'
ITALIC = 'italic'

"""
FOREGROUND -> #301869, #6326e2, 
BACKGROUND -> #134b72, #848c8c, #4a62d9, #001B2B
"""

class MusicPlayer:
    def __init__(self, window):
        # Setting up tkinter window
        window.geometry('600x300+150+150')
        window.title(TITLE)
        window.resizable(0, 0)
        self.window = window

        # Booleans
        self.musicFile = False
        self.playingState = False

        # Integers
        self.audioLength = 0

        # Strings
        self.musicDir = ""
        self.defaultStatus = "Load a file to play!"
        self.playingTime = "--:--:--"
        self.totalTime = "--:--:--"
        self.audioFileTitle = ""

        # MP3 and mixer obejcts
        self.mp3 = None

        # Frames
        controlFrame = LabelFrame(window, relief=GROOVE, bg=GLOBAL_FOREGROUND_COLOR, width=240, height=150)

        # Labels
        self.SongNameLabel = Label(window, relief=GROOVE, bd=LABEL_BORDER_WIDTH, text="", bg=STATUS_BACKGROUND_COLOR, fg=STATUS_FOREGROUND_COLOR, font=(GLOBAL_FONT_FAMILY, GLOBAL_FONT_SIZE))
        self.StatusLabel = Label(controlFrame, relief=SUNKEN, bd=LABEL_BORDER_WIDTH, text=self.defaultStatus, width=30, bg=STATUS_BACKGROUND_COLOR, fg=STATUS_FOREGROUND_COLOR, font=(GLOBAL_FONT_FAMILY, GLOBAL_FONT_SIZE), anchor=W)

        # Load
        self.Load = Button(controlFrame, relief=GROOVE, borderwidth=BUTTON_BORDER_WIDTH, text='Load', width=BUTTON_WIDTH, fg=BUTTON_FOREGROUND_COLOR, bg=BUTTON_BACKGROUND_COLOR, font=(GLOBAL_FONT_FAMILY, GLOBAL_FONT_SIZE), command=self.load)
        # Play options
        self.Pause = Button(controlFrame, relief=GROOVE, borderwidth=BUTTON_BORDER_WIDTH, text='Pause', width=BUTTON_WIDTH, fg=BUTTON_FOREGROUND_COLOR, bg=BUTTON_BACKGROUND_COLOR, font=('Open Sans', 10), command=self.pause)
        self.Stop = Button(controlFrame, relief=GROOVE, borderwidth=BUTTON_BORDER_WIDTH, text='Stop', width=BUTTON_WIDTH, fg=BUTTON_FOREGROUND_COLOR, bg=BUTTON_BACKGROUND_COLOR, font=(GLOBAL_FONT_FAMILY, GLOBAL_FONT_SIZE), command=self.stop)
        # Quit
        self.Quit = Button(controlFrame, relief=GROOVE, borderwidth=BUTTON_BORDER_WIDTH, text='Quit', width=BUTTON_WIDTH, fg=BUTTON_FOREGROUND_COLOR, bg=BUTTON_BACKGROUND_COLOR, font=(GLOBAL_FONT_FAMILY, GLOBAL_FONT_SIZE), command=lambda:window.quit() if messagebox.askyesno("Quit to Windows", "Do you want to exit?") else "")

        # Switching songs - Next
        self.Next = Button(controlFrame, relief=GROOVE, borderwidth=BUTTON_BORDER_WIDTH, text='Next', width=BUTTON_WIDTH-15, fg=BUTTON_FOREGROUND_COLOR, bg=BUTTON_BACKGROUND_COLOR, font=(GLOBAL_FONT_FAMILY, GLOBAL_FONT_SIZE), command=lambda:self.switch_song(target='next'))
        # Switching songs - Previous
        self.Prev = Button(controlFrame, relief=GROOVE, borderwidth=BUTTON_BORDER_WIDTH, text='Previous', width=BUTTON_WIDTH-15, fg=BUTTON_FOREGROUND_COLOR, bg=BUTTON_BACKGROUND_COLOR, font=(GLOBAL_FONT_FAMILY, GLOBAL_FONT_SIZE), command=lambda:self.switch_song(target='prev'))

        # Packing Widgets on screen
        self.SongNameLabel.pack(fill=X, pady=2, side=TOP)
        controlFrame.pack(side=LEFT, fill='y')
        self.Load.pack(padx=10, pady=5)
        self.Pause.pack(padx=10)
        self.Stop.pack(padx=10)
        self.Quit.pack(padx=10, pady=55)
        self.Prev.place(x=25, y=95)
        self.Next.place(x=135, y=95)
        self.StatusLabel.pack(side=BOTTOM, fill=X)

        # Listbox widget
        self.playlist = Listbox(window, bg=GLOBAL_BACKGROUND_COLOR, selectmode=SINGLE, highlightcolor='#3582e8')
        self.playlist.pack(side=LEFT, fill='both', expand='yes')

        # Scale Widget
        self.VolumeLevel = Scale(window, from_=1.0, to_=0.0, orient=VERTICAL, resolution=0.1)
        self.VolumeLevel.config(bg=GLOBAL_BACKGROUND_COLOR)
        self.VolumeLevel.pack(side=LEFT, fill='y')

        # bindings and functions
        self.decideButtonState()
        self.playlist.bind("<Double-1>", self.play)

    def load(self):
        self.changeStatus(msg='Loading...', after=False)
        songList = filedialog.askopenfilenames(filetypes=[("Audio file (.MP3/ .OGG/ .WAV)", ".mp3 .ogg .wav"), ("All files", "*")])


        # Iteratiing through Songlist`
        if songList:
            self.musicDir = '/'.join(songList[0].split('/')[:-1])
            # Creating position varibale for inserting items in listbox
            pos = 0
            while pos < len(songList):
                self.playlist.insert(pos, songList[pos].split('/')[-1])
                pos += 1
            self.changeStatus(msg="Loading Completed!", after=False)

            # Plays the fist song on loading if no song is already playing
            self.play() if not self.playingState else None
        # Some song is playing and user didn't select any new songs so let it pass
        elif self.playingState: pass
        # Loading is interrupted
        else: self.changeStatus(msg="No File selected, cannot proceed...")

    def play(self, event=None):
        # Getting the active element in listbox
        self.musicFile = self.playlist.get(ACTIVE)
        self.musicFile = os.path.join(self.musicDir, self.musicFile)

        # Getting the current selection in listbox  
        currSelection = self.playlist.curselection()
        if not currSelection:
            self.playlist.activate(0)
            self.playlist.selection_set(0, last=None)

        # Getting the title of audio file
        self.audioFileTitle = self.playlist.get(ACTIVE)
        self.SongNameLabel['text'] = self.audioFileTitle

        try:
            if self.musicFile:
                # Initializing the the mp3 instance
                mp3 = mp.MP3(self.musicFile)
                self.mp3 = mp3
                # Sets the frequency to optimize audio
                mixer.init(frequency=mp3.info.sample_rate)  
                # Loading the file into mixer
                mixer.music.load(self.musicFile)
                # Play the file
                mixer.music.play()
                # Changing the status to playing song
                self.changeStatus(msg="Playing Song", after=False)
                # Fetching Audio File length in "HH:MM:SS" format
                self.audioLength = mp3.info.length
                self.totalTime = time.strftime('%H:%M:%S', time.gmtime(self.audioLength))
                # Changing the playing state
                self.playingState = True
                # Changing the title of the window
                self.window.title(TITLE + ' | ' + self.audioFileTitle)
        except UnboundLocalError:
            # Song is not selected form the listbox
            self.changeStatus(msg="Song not selected", after_text="Select a song")
        # Change the states of control buttons
        self.decideButtonState()
        # Display information about elapsed time
        self.timeElapsed()

    def pause(self):
        if self.playingState:
            mixer.music.pause()
            self.playingState = False
            self.Pause['text'] = "Play"
            self.window.title(TITLE + ' | ' + self.audioFileTitle+" (Paused)")
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

    def stop(self):
        # Stopping the mixer
        mixer.music.stop()
        self.window.title(TITLE + ' | ' + self.audioFileTitle+" (Stopped)")
        if mixer.music.get_pos()//1000 == -1:
            # Changin the playing state var
            self.playingState = False
            # Changing the text on Label to 'Play'
            self.Pause['text'] = 'Play'
            # Changing the status to Stopped
            self.changeStatus(msg="00:00:00/"+self.totalTime+" (Music Stopped)", after=False)

    def switch_song(self, target):
        # Get the current song tuple number
        next_one = self.playlist.curselection()

        # Ending index of playlist
        end = len(self.playlist.get(0, END)) - 1

        # Add one to the current song number
        if target == 'next':
            next_one = next_one[0] + 1
        else:
            next_one = next_one[0] - 1

        # If 'next_one' exceeds ENDing Index of Listbox
        if next_one > end:
            next_one = 0
        # Or 'next_one' becomes less than zero
        elif next_one < 0:
            next_one = end

        # Clear active selection
        self.playlist.selection_clear(0, END)

        # Activate next song
        self.playlist.activate(next_one)

        # Set Active Bat to Next Song
        self.playlist.selection_set(next_one, last=None)

        # Play the active element in listbox
        self.play()


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
        else:
            # Audio File has ended successfully
            # Play the next file
            self.switch_song(target='next')


    def changeStatus(self, _type=None, msg=None, after=True, after_text=None):
        if msg is None: msg = self.defaultStatus
        if _type is not None:
            if isinstance(_type, str): msg = _type + ": " + msg
            else: raise TypeError("Expected 'str' got '{}' instead...".format(_type.__class__))

        self.StatusLabel['text'] = msg
        if after:
            self.window.after(1000, lambda:self.StatusLabel.config(text=self.defaultStatus if after_text is None else after_text))

    def decideButtonState(self):
        if self.musicFile or self.playingState:
            self.Pause.config(state=NORMAL) 
            self.Stop.config(state=NORMAL)
            self.Next.config(state=NORMAL)
            self.Prev.config(state=NORMAL)
        else:
            self.Pause.config(state=DISABLED) 
            self.Stop.config(state=DISABLED)
            self.Next.config(state=DISABLED)
            self.Prev.config(state=DISABLED)


root = Tk()
app = MusicPlayer(root)

if __name__ == '__main__':
    root.mainloop()
