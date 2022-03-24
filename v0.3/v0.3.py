import os
import time
from tkinter import *
from tkinter import ttk
from tkinter import filedialog
from pygame import mixer
from mutagen.mp3 import MP3
from mutagen import MutagenError

global count
count = 0

class MusicPlayer:
    def __init__(self, master):
        """
        CONSTANTS
        """
        BACKGROUND_COLOR = "#010" # "#001B2B"

        # Default Title
        TITLE = "Leaf Player (V.0.3)"
        # Whether window will be resizable or not
        self.RESIZABLE = True 

        DIR = "pngs\\16"
        RESOLUTION = "960x540"

        # System Colors
        MEDIA_CONTROL_COLOR = '#fff'  # Color of Media
        VIDEO_FRAME_COLOR = '#000'  # Color of Video
        HIGHLIGHT_COLOR = 'green'
        STRIPED_COLOR = '#8dd0d9'

        # Row height in playlist treeview
        PLAYLIST_ROW_HEIGHT = 20

        # Default volume of player (Should be between [0.0, 1.0] else 0.5 is considered)
        DEFAULT_VOLUME = 0.8

        # Timer accuracy (in miliseconds) increasing will 
        TIME = 1000

        # Label border width
        LABEL_BORDER_WIDTH = 2

        # Button width
        BUTTON_WIDTH = 25

        # Button background & foreground color
        BUTTON_BACKGROUND_COLOR = "#0E3D8B" # "#1E8EAB" # "#74655E" # "#0E3D8B"
        BUTTON_FOREGROUND_COLOR = "#2B8EE2" # "#FFF" # "#BDB19A" # #2B8EE2"

        # Button hover background & foreground color
        BUTTON_HOVER_BACKGROUND_COLOR = BUTTON_FOREGROUND_COLOR # "#120460" # "#2B8EE2"
        BUTTON_HOVER_FOREGROUND_COLOR = BUTTON_BACKGROUND_COLOR # "#1E8EAB" # "#0E3D8B"

        # Status button background and & foregrounf color
        STATUS_BACKGROUND_COLOR = "#120460" # "#563D39" # "#001B2B"
        STATUS_FOREGROUND_COLOR = "#FFF" # "#BDB19A" # "#FFFFFE"

        # Button active background & foreground color
        BUTTON_ACTIVE_BACKGROUND_COLOR = "#9400d3"
        BUTTON_ACTIVE_FOREGROUND_COLOR = BUTTON_BACKGROUND_COLOR

        # Button border width
        BUTTON_BORDER_WIDTH = 0

        # Global background & foreground color
        GLOBAL_BACKGROUND_COLOR = "#001B2B" # "#004696" # "#687E8D" # "#E3CAC3" # "#d7dade"
        GLOBAL_FOREGROUND_COLOR = "#FFF" # "#4f5154"

        # Global Font familiy & size
        GLOBAL_FONT_FAMILY = "Helvetica" # "Open Sans"
        GLOBAL_FONT_SIZE = 10
        # Presets
        FONT_BOLD = (GLOBAL_FONT_FAMILY, GLOBAL_FONT_SIZE, 'bold')
        FONT_ITALIC = (GLOBAL_FONT_FAMILY, GLOBAL_FONT_SIZE, 'italic')
        FONT = (GLOBAL_FONT_FAMILY, GLOBAL_FONT_SIZE)

        # Icons for buttons
        PLAY_ICO = PhotoImage(file=DIR + '\\play.png')
        PAUSE_ICO = PhotoImage(file=DIR + '\\pause.png')
        NEXT_ICO = PhotoImage(file=DIR + '\\next.png')
        PREV_ICO = PhotoImage(file=DIR + '\\prev.png')
        LOOP_OFF_ICO = PhotoImage(file=DIR + '\\colored\\loop-off.png')
        LOOP_ON_ICO = PhotoImage(file=DIR + '\\colored\\loop-on.png')
        STOP_ICO = PhotoImage(file=DIR + '\\stop.png')

        # Setting up tkinter window
        master.geometry(f'{RESOLUTION}+150+150')
        master.title(TITLE)
        master.resizable(0, 0)
        master.config(bg=BACKGROUND_COLOR)
        self.master = master

        if self.RESIZABLE:
            master.resizable(1, 1)
        else:
            master.resizable(0, 0)

        # Dictionaries
        self.songDict = {}

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

        # Useless for now variables
        self.loop = False               # To toggle loop on/off
        self.selected = []
        self.duration = 0


        # Tool Bar Menu
        toolMenu = Menu(master)
        master.config(menu=toolMenu)

        fileMenu = Menu(toolMenu)
        toolMenu.add_cascade(label="File", menu=fileMenu)

        fileMenu.add_command(label="Open...", command=lambda: self.open_file(multiple=False))
        fileMenu.add_command(label="Open files...", command=lambda: self.open_file(multiple=True))
        fileMenu.add_command(label="Open Folder...", command=self.openFolder)
        fileMenu.add_separator()
        fileMenu.add_command(label="Clear Playlist", command=self.clearPlaylist)
        fileMenu.add_command(label="Exit", command=master.quit)

        # Main Windows Configuration with Frames

        # Video and Playlist Frame
        videoPlaylistFrame = Frame(master)
        videoPlaylistFrame.pack(side=LEFT, fill=BOTH, expand='yes')

        # Video Frame
        videoFrame = Frame(videoPlaylistFrame)
        videoFrame.config(width=720, height=540, bg=VIDEO_FRAME_COLOR)
        videoFrame.pack(side=TOP, fill=BOTH, expand='yes')

        # Playlist Frame
        playlistFrame = Frame(master)
        playlistFrame.pack(side=LEFT, fill='both')

        # Bottom Frame
        bottomFrame = Frame(master)
        bottomFrame.pack(side=LEFT)

        # Media control Frame
        mediaControlFrame = Frame(videoFrame, bg=MEDIA_CONTROL_COLOR)
        mediaControlFrame.pack(side=BOTTOM, fill=X)

        # Button Frame
        buttonFrame = Frame(mediaControlFrame, bg='#fff')
        buttonFrame.pack(side=LEFT, padx=1, pady=1, fill=X)
        # Initialization of Frames Ends

        # ScrollBar for Listbox
        yScroll = ttk.Scrollbar(playlistFrame, orient=VERTICAL)
        yScroll.pack(side=RIGHT, fill=Y)

        xScroll = ttk.Scrollbar(playlistFrame, orient=HORIZONTAL)
        xScroll.pack(side=BOTTOM, fill=X)

        # Adding style to listbox
        style = ttk.Style()

        # Setting a Theme
        style.theme_use()  # default, clam, alt, vista

        # Listbox for playlist
        self.playlist = Listbox(playlistFrame, yscrollcommand=yScroll, xscrollcommand=xScroll, selectmode=BROWSE,
                                width=40, bg='#D3D3D3', fg='#405246', selectbackground='green')
        self.playlist.pack(fill=Y, expand=YES)

        # Binding Listbox
        self.playlist.bind('<Double-1>', self.instant_play)

        # Configuring ScrollBar for listbox
        yScroll.config(command=self.playlist.yview)
        xScroll.config(command=self.playlist.xview)

        # Media control Buttons
        self.playBTN = Button(buttonFrame, bg=MEDIA_CONTROL_COLOR, image=PLAY_ICO, width=18, height=18,
                               relief=RAISED, borderwidth=0, command=self.change_N_play)
        self.prevBTN = Button(buttonFrame, bg=MEDIA_CONTROL_COLOR, image=PREV_ICO, width=18, height=18,
                               relief=RAISED, borderwidth=0, command=lambda: self.switch_song(target='prev'))
        self.nextBTN = Button(buttonFrame, bg=MEDIA_CONTROL_COLOR, image=NEXT_ICO, width=18, height=18,
                               relief=RAISED, borderwidth=0, command=lambda: self.switch_song(target='next'))
        self.loopBTN = Button(buttonFrame, bg=MEDIA_CONTROL_COLOR, image=LOOP_OFF_ICO, width=18, height=18,
                               relief=RAISED, borderwidth=0, command=self.loop_song)
        self.stopBTN = Button(buttonFrame, bg=MEDIA_CONTROL_COLOR, image=STOP_ICO, width=18, height=18,
                               relief=RAISED, borderwidth=0, command=self.stop)

        self.playBTN.image = PLAY_ICO
        self.loopBTN.image = LOOP_OFF_ICO

        self.prevBTN.pack(side=LEFT)
        self.playBTN.pack(side=LEFT)
        self.nextBTN.pack(side=LEFT)
        self.loopBTN.pack(side=LEFT, padx=5)
        self.stopBTN.pack(side=LEFT)

        # Duration Widgets
        self.elapsedTime = Label(buttonFrame, text='--:--:--', bd=0, relief=GROOVE, bg='#fff', fg='#000')
        self.elapsedTime.pack(side=LEFT, padx=1, anchor=E, ipadx=10)

        # Duration Slider
        self.duration_slider = ttk.Scale(buttonFrame, from_=0, to=f'{int(self.duration)}', orient=HORIZONTAL, value=0, command=self.slide, length=400)
        self.duration_slider.pack(side=LEFT, padx=3, ipadx=10)

        # Total length of Song
        self.totalTime = Label(buttonFrame, text='--:--:--', bd=0, relief=GROOVE, bg='#fff', fg='#000')
        self.totalTime.pack(side=LEFT, padx=1, anchor=W)

        # Duration Widgets Ends

        # Initialization ends

    def play_time(self):
        # Grab Elapsed Time
        # mixer.music.load(file)
        current_time = mixer.music.get_pos() // 1000

        # Get currently playing song
        curr_file = self.playlist.curselection()
        song = self.playlist.get(curr_file)

        song = self.SongDict[song] + '/' + song

        elapsed_time = time.strftime('%H:%M:%S', time.gmtime(current_time))
        song_length = time.strftime('%H:%M:%S', time.gmtime(MP3(song).info.length))

        # Increase Current time by 1 second
        current_time += 1

        if int(self.duration_slider.get()) == int(MP3(song).info.length):
            # Output time to status bar
            self.elapsedTime.config(text=f'{elapsed_time}')
            self.totalTime.config(text=f'{song_length}')
            self.stop()

        elif int(self.duration_slider.get()) == int(current_time):
            # Slider hasn't been moved
            # Update Slider to position
            slider_position = int(self.duration)

            self.duration_slider.config(to=slider_position, value=int(current_time))
        else:
            # Slider has been moved
            # Update Slider to position
            slider_position = int(self.duration)

            # Convert to time format
            elapsed_time = time.strftime('%H:%M:%S', time.gmtime(int(self.duration_slider.get())))

            # Output time to Status Bar
            self.duration_slider.config(to=slider_position, value=int(self.duration_slider.get()))

            # Output time to status bar
            self.elapsedTime.config(text=f'{elapsed_time}')
            self.totalTime.config(text=f'{song_length}')

            # Move this thing along one second
            next_time = int(self.duration_slider.get()) + 1
            self.duration_slider.config(value=next_time)

        # Update Time

        self.elapsedTime.after(1000, self.play_time)     # To run the function after every 1000 milliseconds

    def slide(self, event):
        song = self.playlist.get(ACTIVE)
        song = self.SongDict[song] + '/' + song

        mixer.music.load(song)
        if self.loop:
            mixer.music.play(loops=1000, start=int(self.duration_slider.get()))
        else:
            mixer.music.play(loops=0, start=int(self.duration_slider.get()))

    def get_str_attributes(self, string, target='name') -> str:
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

    def open_file(self, multiple=False):
        if multiple:
            self.musicDir = filedialog.askopenfilenames(title='Open Files', filetypes=(("mp3 files", "*.mp3"),
                                                                                       ("All files", "*")))

            if self.playingState == 'playing':
                mixer.music.stop()
                self.playBTN.image = PLAY_ICO
                self.playingState = 'stopped'

            for item in self.musicDir:
                self.musicFile = self.get_str_attributes(string=item, target='name')
                self.musicDir = self.get_str_attributes(string=item, target='dir')
                self.SongDict[self.musicFile] = self.musicDir

                self.playlist.insert(END, self.musicFile)

                print(f"Music File: {self.musicFile}\nMusic Dir {self.musicDir}")

            self.playingState = 'multi-open'
        else:
            self.musicDir = filedialog.askopenfilename(title='Open File', filetypes=(("mp3 files", "*.mp3"), ("All files", "*")))
            self.musicFile = self.get_str_attributes(string=self.musicDir, target='name')
            self.musicDir = self.get_str_attributes(string=self.musicDir, target='dir')
            self.SongDict[self.musicFile] = self.musicDir

            self.playlist.insert(END, self.musicFile)

            print(f"Music File: {self.musicFile}\nMusic Dir {self.musicDir}")

            self.playingState = 'single-open'

        self.old_song_name = self.playlist.get(ACTIVE)

        if self.playBTN.image == PLAY_ICO:
            # start playing
            self.play()
            self.playBTN.config(image=PAUSE_ICO)
            self.playBTN.image = PAUSE_ICO

    def openFolder(self):
        self.musicDir = filedialog.askdirectory()
        try:
            self.DirList = os.listdir(self.musicDir)
        except FileNotFoundError:
            self.DirList = ''
            print("Try Again")

        if self.DirList:
            for item in self.DirList:
                self.SongDict[item] = self.musicDir
                self.playlist.insert(END, item)

        self.playingState = 'folder-open'

    def play(self):
        if self.playingState != 'new-paused':
            if self.old_song_name != self.playlist.get(ACTIVE) and self.old_song_name != '':
                self.playingState = 'new'

        print(self.musicFile, f'\n{self.playingState}')

        try:
            try:
                self.musicDir = self.SongDict[self.musicFile]
                self.musicFile = self.musicDir + '/' + self.musicFile
            except KeyError:
                pass
            mp3 = MP3(self.musicFile)

            if self.playingState == 'paused' or self.playingState == 'new-paused':
                mixer.music.unpause()

            elif self.playingState == 'stopped':
                mixer.init(frequency=mp3.info.sample_rate)  # Sets the frequency to optimize audio
                if self.old_song_name != self.playlist.get(ACTIVE) and self.old_song_name != '':
                    self.musicFile = self.playlist.get(ACTIVE)
                    mixer.music.load(self.musicFile)
                    mixer.music.play()
                else:
                    mixer.music.load(self.musicFile)
                    mixer.music.play()
                self.old_song_name = self.playlist.get(ACTIVE)
                self.playingState = 'playing'
                print(f'Playing: {self.musicFile}')
                self.file_open_bool = False

                # Set the duration
                self.duration = MP3(self.musicFile).info.length
                # Get the current position
                self.play_time()

            elif self.playingState == 'new' and self.playBTN.image == PLAY_ICO:
                self.musicFile = self.SongDict[self.playlist.get(ACTIVE)] + '/' + self.playlist.get(ACTIVE)
                mixer.music.load(self.musicFile)
                mixer.music.play()
                self.old_song_name = self.playlist.get(ACTIVE)
                self.playingState = 'playing'

                # Set the duration
                self.duration = MP3(self.musicFile).info.length
                # Get the current position
                self.play_time()

            elif self.playingState == 'multi-open' or self.playingState == 'folder-open' or self.playingState == 'single-open':
                mixer.init(frequency=mp3.info.sample_rate)
                self.playlist.selection_set(0, 0)

                self.musicFile = self.SongDict[self.playlist.get(ACTIVE)] + '/' + self.playlist.get(ACTIVE)

                mixer.music.load(self.musicFile)
                mixer.music.play()
                self.playingState = 'playing'

                # Set the duration
                self.duration = MP3(self.musicFile).info.length
                # Get the current position
                self.play_time()

            # # Update Slider to position
            # slider_position = int(self.duration)
            # self.duration_slider.config(to=slider_position, value=0)

        except MutagenError as e:
            print(f"Song not Loaded\nError: {e}\nPlaying State: {self.playingState}")

    def instant_play(self, event):
        file_name = self.playlist.get(ACTIVE)
        file = self.SongDict[file_name] + '/' + file_name
        mp3 = MP3(file)
        mixer.init(frequency=mp3.info.sample_rate)
        mixer.music.load(file)
        if self.loop:
            mixer.music.play(loops=1000)
        else:
            mixer.music.play()
        self.playingState = 'playing'
        print(f'Playing: {file_name}\nFrom: {self.SongDict[file_name]}')
        self.file_open_bool = False

        self.playBTN.config(image=PLAY_ICO)
        self.playBTN.image = PLAY_ICO

    def stop(self):
        self.playingState = 'stopped'

        self.duration_slider.config(value=0)

        mixer.music.stop()

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

        # Grab song from playlist
        song = self.playlist.get(next_one)
        self.duration_slider.config(value=0)
        self.elapsedTime.config(text=time.strftime('%H:%M:%S', time.gmtime(0)))

        self.musicFile = self.SongDict[song] + '/' + song
        mixer.music.load(self.musicFile)
        mixer.music.play()
        self.playingState = 'playing'

        if self.playBTN.image != PLAY_ICO:
            self.playBTN.config(image=PAUSE_ICO)
            self.playBTN.image = PAUSE_ICO

        # Get the current position
        self.play_time()

        # Set the duration
        self.duration = MP3(self.musicFile).info.length
        # # Update Slider to position
        # slider_position = int(self.duration)
        # self.duration_slider.config(to=slider_position, value=0)

        # Clear active selection
        self.playlist.selection_clear(0, END)

        # Activate next song
        self.playlist.activate(next_one)

        # Set Active Bat to Next Song
        self.playlist.selection_set(next_one, last=None)

    def pause(self):
        # pause song
        mixer.music.pause()

        song = self.playlist.get(ACTIVE)
        song = self.SongDict[song] + '/' + song

        elapsed_time = time.strftime('%H:%M:%S', time.gmtime((mixer.music.get_pos() // 1000)))
        total_length = time.strftime('%H:%M:%S', time.gmtime(MP3(song).info.length))

        if self.playingState == 'new':
            self.playingState = 'new-paused'
        else:
            self.playingState = 'paused'

        print(self.playingState)

        self.elapsedTime.config(text=elapsed_time)
        self.totalTime.config(text=total_length)

    def change_N_play(self):
        if self.playBTN.image == PLAY_ICO:
            # start playing
            self.play()
            self.playBTN.config(image=PAUSE_ICO)
            self.playBTN.image = PAUSE_ICO
        else:
            self.pause()
            self.playBTN.config(image=PLAY_ICO)
            self.playBTN.image = PLAY_ICO

    def loop_song(self):
        if self.loopBTN.image == LOOP_ON_ICO:
            self.loop = False
            self.loopBTN.config(relief=RAISED)
            self.loopBTN.config(image=LOOP_OFF_ICO)
            self.loopBTN.image = LOOP_OFF_ICO
        else:
            self.loop = True
            self.loopBTN.config(relief=SUNKEN)
            self.loopBTN.config(image=LOOP_ON_ICO)
            self.loopBTN.image = LOOP_ON_ICO

    def delete_song(self):
        # Change the icon of Play Button
        if self.playBTN.image == PLAY_ICO:
            self.playBTN.config(image=PAUSE_ICO)
            self.playBTN.image = PAUSE_ICO

        self.playlist.delete(ANCHOR)
        # Stop music if it's playing
        if self.playingState != 'stopped':
            self.playingState = 'stopped'
            mixer.music.stop()

    def clearPlaylist(self):
        # Change the icon of Play Button

        self.playlist.delete(0, END)
        # Stop music if it's playing
        if self.playingState != 'stopped':
            self.playingState = 'stopped'
            mixer.music.stop()

        if self.playBTN.image == PLAY_ICO:
            self.playBTN.config(image=PAUSE_ICO)
            self.playBTN.image = PAUSE_ICO


# Configurations and Initialization
app = Tk()
player = MusicPlayer(app)

# Mainloop initialization
if __name__ == '__main__':
    app.mainloop()
