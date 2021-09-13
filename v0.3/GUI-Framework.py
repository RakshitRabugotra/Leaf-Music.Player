import os
from tkinter import *
from tkinter import ttk
from tkinter import filedialog
from pygame import mixer
from mutagen import mp3 as mp
from mutagen import MutagenError


DIR = "pngs\\16"
FONT = ('Open Sans', 12)
RESIZABLE = False   # True if you want the window to be resizable
RESOLUTION = "960x540"
MEDIA_CONTROL_COLOR = '#fff'  # Color of Media
VIDEO_FRAME_COLOR = '#000'      # Color of Video
HIGHLIGHT_COLOR = 'green'
STRIPED_COLOR = '#8dd0d9'


class MusicPlayer:
    def __init__(self, master):

        self.playingState = 'stopped'  # ['playing', 'paused', 'stopped']

        self.musicDir = ""
        self.musicFile = ""
        self.SongList = list()
        self.file_open_bool = False
        self.old = ''

        # Icons for Buttons
        self.play_ico = PhotoImage(file=DIR + r'\play.png')
        self.pause_ico = PhotoImage(file=DIR + r'\pause.png')
        self.next_ico = PhotoImage(file=DIR + r'\next.png')
        self.prev_ico = PhotoImage(file=DIR + r'\prev.png')

        toolMenu = Menu(master)
        master.config(menu=toolMenu)

        fileMenu = Menu(toolMenu)
        toolMenu.add_cascade(label="File", menu=fileMenu)

        fileMenu.add_command(label="Open...", command=self.openFILE)
        fileMenu.add_command(label="Open Folder...", command=self.openFOLDER)
        fileMenu.add_separator()
        fileMenu.add_command(label="Exit", command=master.quit)

        Video_Playlist_Frame = Frame(master)
        Video_Playlist_Frame.pack(side=LEFT, fill=BOTH, expand='yes')

        videoFrame = Frame(Video_Playlist_Frame)
        videoFrame.config(width=720, height=540, bg=VIDEO_FRAME_COLOR)
        videoFrame.pack(side=TOP, fill=BOTH, expand='yes')

        playlistFrame = Frame(master)
        playlistFrame.pack(side=LEFT, fill='both')

        BottomFrame = Frame(master)
        BottomFrame.pack(side=LEFT)

        # Listbox initialization & Scrollbar initialization
        myYScrollbar = Scrollbar(playlistFrame, orient=VERTICAL)
        myYScrollbar.pack(side=RIGHT, fill=Y)

        # SINGLE, MULTIPLE, BROWSE, EXTENDED
        self.listbox = Listbox(playlistFrame, width=40, yscrollcommand=myYScrollbar.set, selectmode=EXTENDED)     # xscrollcommand=myXScrollbar.set
        self.listbox.pack(side=LEFT, fill=Y, expand='yes')

        # Configure Scroll bar
        myYScrollbar.config(command=self.listbox.yview)

        # Media Control Frame
        Media_Control_Frame = Frame(videoFrame, bg=MEDIA_CONTROL_COLOR)
        Media_Control_Frame.pack(side=BOTTOM, fill=X)

        ButtonFrame = Frame(Media_Control_Frame)
        ButtonFrame.pack(side=LEFT, padx=1, pady=1, fill=X)

        self.play_btn = Button(ButtonFrame, bg=MEDIA_CONTROL_COLOR, image=self.play_ico, width=18, height=18, relief=RAISED, command=self.chang_N_play)
        self.play_btn.image = self.play_ico

        self.prev_btn = Button(ButtonFrame, bg=MEDIA_CONTROL_COLOR, image=self.prev_ico, width=18, height=18, relief=RAISED, command=None)

        self.next_btn = Button(ButtonFrame, bg=MEDIA_CONTROL_COLOR, image=self.next_ico, width=18, height=18, relief=RAISED, command=None)

        self.prev_btn.pack(side=LEFT)
        self.play_btn.pack(side=LEFT)
        self.next_btn.pack(side=LEFT)

    def get_str_attributes(self, string, target='name'):
        ret = ''
        dir_ = list()
        for i in string[::-1]:
            if i != '/':
                ret += i
            else:
                dir_.append(ret[::-1])
                ret = ''
        dir_.append(ret[::-1])
        ret = dir_.pop(0)
        main_dir = "/".join(reversed(dir_))

        if target == 'name':
            return ret
        else:
            return main_dir

    def openFILE(self):
        self.musicDir = filedialog.askopenfilename()

        if self.playingState == 'playing':
            mixer.music.stop()
            self.play_btn.image = self.play_ico
            self.playingState = 'stopped'

        self.musicFile = self.get_str_attributes(string=self.musicDir, target='name')
        self.musicDir = self.get_str_attributes(string=self.musicDir, target='dir')

        self.old = self.listbox.get(ACTIVE)

        self.file_open_bool = True
        print(f"Music File: {self.musicFile}\nMusic Dir {self.musicDir}")

        self.listbox.insert(END, self.musicFile)
        self.playingState = 'stopped'

        if self.play_btn.image == self.play_ico:
            # start playing
            self.play()
            self.play_btn.config(image=self.pause_ico)
            self.play_btn.image = self.pause_ico

    def openFOLDER(self):
        self.musicDir = filedialog.askdirectory()
        try:
            self.SongList = os.listdir(self.musicDir)
        except FileNotFoundError:
            self.SongList = ''
            print("Try Again")

        if self.SongList:
            for item in self.SongList:
                self.listbox.insert(END, item)

    def play(self):
        if self.old != self.listbox.get(ACTIVE) and self.old != '':
            self.playingState = 'new'
        if self.file_open_bool:
            self.musicFile = self.musicDir + '/' + self.musicFile
        else:
            self.musicFile = self.musicDir + '/' + self.listbox.get(ACTIVE)

        print(self.musicFile)

        try:
            mp3 = mp.MP3(self.musicFile)

            if self.playingState == 'stopped':
                mixer.init(frequency=mp3.info.sample_rate)  # Sets the frequency to optimize audio
                if self.old != self.listbox.get(ACTIVE) and self.old != '':
                    mixer.music.load(self.listbox.get(ACTIVE))
                    mixer.music.play()
                else:
                    mixer.music.load(self.musicFile)
                    mixer.music.play()
                self.old = self.listbox.get(ACTIVE)
                self.playingState = 'playing'
                print(f'Playing: {self.musicFile}')
                self.file_open_bool = False

            elif self.playingState == 'paused':
                mixer.music.unpause()

            elif self.playingState == 'new' and self.play_btn.image == self.play_ico:
                self.musicFile = self.musicDir + '/' + self.listbox.get(ACTIVE)
                mixer.music.load(self.musicFile)
                mixer.music.play()

        except MutagenError:
            print("Song not Loaded")

    def pause(self):
        self.playingState = 'paused'
        mixer.music.pause()

    def stop(self):
        self.playingState = 'stopped'
        mixer.music.stop()

    def Next(self):
        pass

    def Prev(self):
        pass

    def chang_N_play(self):
        if self.play_btn.image == self.play_ico:
            # start playing
            self.play()
            self.play_btn.config(image=self.pause_ico)
            self.play_btn.image = self.pause_ico
        else:
            # pause playing
            self.pause()
            self.play_btn.config(image=self.play_ico)
            self.play_btn.image = self.play_ico


# Configurations and Initialization
app = Tk()
app.title('Leaf Player')
app.geometry(RESOLUTION)

if RESIZABLE:
    app.resizable(1, 1)
else:
    app.resizable(0, 0)

player = MusicPlayer(app)

# Mainloop initialization
if __name__ == '__main__':
    app.mainloop()
