import os
from tkinter import *
from tkinter import ttk
from tkinter import filedialog
from pygame import mixer
from mutagen import mp3 as mp
from mutagen import MutagenError


class MusicPlayer:
    def __init__(self, window):
        window.geometry('480x300')
        window.title('Py-Player')
        window.resizable(0, 0)

        B_COLOR = "#d7dade"     # Background Color of Buttons
        F_COLOR = "#4f5154"     # Foreground Color of Buttons

        window.config(bg=B_COLOR)

        self.music_file = "Load a Directory To continue"    # The Quick Brown Fox Jumped Over the Dog
        self.playing_state = False
        self.music_dir = ""     # Music Directory
        self.status = ""

        self.SongNameLabel = Label(window, text=self.music_file, bg=F_COLOR, fg=B_COLOR, font=('Open Sans', 10))

        songProgress = ttk.Progressbar(window, orient=HORIZONTAL, length=320, mode='determinate')

        self.SongNameLabel.pack(fill='x', pady=2, side=TOP)

        songProgress.pack(fill='x', padx=5, pady=5)

        controlFrame = LabelFrame(window, bg=F_COLOR, width=240, height=150)
        controlFrame.pack(side=LEFT, fill='y')

        self.Load = Button(controlFrame, text='Load', width=10, fg=F_COLOR, bg=B_COLOR, font=('Open Sans', 10), command=self.load)
        self.Play = Button(controlFrame, text='Play', width=10, fg=F_COLOR, bg=B_COLOR, font=('Open Sans', 10), command=self.play)
        self.Pause = Button(controlFrame, text='Pause', width=10, fg=F_COLOR, bg=B_COLOR, font=('Open Sans', 10), command=self.pause)
        self.Stop = Button(controlFrame, text='Stop', width=10, fg=F_COLOR, bg=B_COLOR, font=('Open Sans', 10), command=self.stop)

        self.StatusLabel = Label(controlFrame, text="Load a Directory", bd=1, relief=SUNKEN, anchor=W, fg=F_COLOR, bg=B_COLOR, font=('Open Sans', 10))

        self.Load.pack(padx=10, pady=2.5)
        self.Play.pack(padx=10, pady=2.5)
        self.Pause.pack(padx=10, pady=2.5)
        self.Stop.pack(padx=10, pady=2.5)

        self.StatusLabel.pack(side=BOTTOM, fill=X)

        self.playlist = Listbox(window, highlightcolor='#3582e8', bg=B_COLOR, selectmode=SINGLE)
        self.playlist.pack(side=LEFT, fill='both', expand='yes')

        self.VolumeLevel = Scale(window, from_=0.0, to_=1.0, orient=VERTICAL, resolution=0.1)
        self.VolumeLevel.config(bg=B_COLOR)
        self.VolumeLevel.pack(side=LEFT, fill='y')

    def load(self):
        self.StatusLabel['text'] = "Loading..."
        self.music_dir = filedialog.askdirectory()
        try:
            SongList = os.listdir(self.music_dir)
        except FileNotFoundError:
            SongList = ''
            print("Try Again")
        pos = 0

        if SongList is not '':
            for item in SongList:
                self.playlist.insert(pos, item)
                pos += 1
        self.StatusLabel['text'] = "Loading Completed!"

    def play(self):
        self.SongNameLabel['text'] = self.playlist.get(ACTIVE)
        self.music_file = self.music_dir + '/' + self.SongNameLabel['text']

        try:
            mp3 = mp.MP3(self.music_file)
        except MutagenError:
            print("Song not Loaded")

        try:
            if self.music_file:
                mixer.init(frequency=mp3.info.sample_rate)  # Sets the frequency to optimize audio
                mixer.music.load(self.music_file)
                mixer.music.play()
                self.StatusLabel['text'] = "Playing Song..."
                self.Play['text'] = 'Replay'
                self.Pause['text'] = 'Pause/Play'
        except UnboundLocalError:
            print("Song not selected/Error playing the song")

    def pause(self):
        if not self.playing_state:
            mixer.music.pause()
            self.StatusLabel['text'] = "Paused..."
            self.playing_state = True
        else:
            mixer.music.unpause()
            self.StatusLabel['text'] = "Playing Song..."
            self.playing_state = False

    def stop(self):
        mixer.music.stop()
        self.Play['text'] = 'Play'
        self.StatusLabel['text'] = "Stopped Playing..."


root = Tk()
app = MusicPlayer(root)

if __name__ == '__main__':
    root.mainloop()
