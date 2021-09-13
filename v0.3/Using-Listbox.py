import os
import time
from tkinter import *
from tkinter import ttk
from tkinter import filedialog
from pygame import mixer
from mutagen.mp3 import MP3
from mutagen import MutagenError

DIR = "pngs\\16"
INITIAL_DIR = ""  # r"E:\Songs"
FONT = ('Open Sans', 12)
RESIZABLE = True  # True if you want the window to be resizable
RESOLUTION = "960x540"
MEDIA_CONTROL_COLOR = '#fff'  # Color of Media
VIDEO_FRAME_COLOR = '#000'  # Color of Video
HIGHLIGHT_COLOR = 'green'
STRIPED_COLOR = '#8dd0d9'
PLAYLIST_ROW_HEIGHT = 20  # Row Height in Playlist Treeview

global count
count = 0


class MusicPlayer:
    def __init__(self, master):
        self.playingState = 'stopped'  # ['playing', 'paused', 'stopped']

        # Various Variables
        self.musicDir = ""              # For acquiring the parent directory
        self.musicFile = ""             # For getting name/full_name of song
        self.SongDict = dict()          # For storing the directory for every file
        self.file_open_bool = False     # Used for conditional operations
        self.old_song_name = ''         # Used for conditional operations
        self.DirList = list()           # Used to iterate through
        self.indexDict = dict()         #
        self.loop = False               # To toggle loop on/off
        self.selected = []
        self.duration = 0

        # Icons for Buttons
        self.play_ico = PhotoImage(file=DIR + r'\play.png')
        self.pause_ico = PhotoImage(file=DIR + r'\pause.png')
        self.next_ico = PhotoImage(file=DIR + r'\next.png')
        self.prev_ico = PhotoImage(file=DIR + r'\prev.png')
        self.loop_off_ico = PhotoImage(file=DIR + r'\colored\loop-off.png')
        self.loop_on_ico = PhotoImage(file=DIR + r'\colored\loop-on.png')
        self.stop_ico = PhotoImage(file=DIR + r'\stop.png')

        # Tool Bar Menu
        tool_menu = Menu(master)
        master.config(menu=tool_menu)

        file_menu = Menu(tool_menu)
        tool_menu.add_cascade(label="File", menu=file_menu)

        file_menu.add_command(label="Open...", command=lambda: self.open_file(multiple=False))
        file_menu.add_command(label="Open files...", command=lambda: self.open_file(multiple=True))
        file_menu.add_command(label="Open Folder...", command=self.open_folder)
        file_menu.add_separator()
        file_menu.add_command(label="Clear Playlist", command=self.clear_playlist)
        file_menu.add_command(label="Exit", command=master.quit)
        # Drop Down Menu Ends

        # Main Windows Configuration with Frames

        # Video and Playlist Frame
        video_playlist_frame = Frame(master)
        video_playlist_frame.pack(side=LEFT, fill=BOTH, expand='yes')

        # Video Frame
        video_frame = Frame(video_playlist_frame)
        video_frame.config(width=720, height=540, bg=VIDEO_FRAME_COLOR)
        video_frame.pack(side=TOP, fill=BOTH, expand='yes')

        # Playlist Frame
        playlist_frame = Frame(master)
        playlist_frame.pack(side=LEFT, fill='both')

        # Bottom Frame
        bottom_frame = Frame(master)
        bottom_frame.pack(side=LEFT)

        # Media control Frame
        media_control_frame = Frame(video_frame, bg=MEDIA_CONTROL_COLOR)
        media_control_frame.pack(side=BOTTOM, fill=X)

        # Button Frame
        button_frame = Frame(media_control_frame, bg='#fff')
        button_frame.pack(side=LEFT, padx=1, pady=1, fill=X)
        # Initialization of Frames Ends

        # ScrollBar for Listbox
        y_scroll = ttk.Scrollbar(playlist_frame, orient=VERTICAL)
        y_scroll.pack(side=RIGHT, fill=Y)

        x_scroll = ttk.Scrollbar(playlist_frame, orient=HORIZONTAL)
        x_scroll.pack(side=BOTTOM, fill=X)

        # Adding style to listbox
        style = ttk.Style()

        # Setting a Theme
        style.theme_use()  # default, clam, alt, vista

        # Listbox for playlist
        self.playlist = Listbox(playlist_frame, yscrollcommand=y_scroll, xscrollcommand=x_scroll, selectmode=BROWSE,
                                width=40, bg='#D3D3D3', fg='#405246', selectbackground='green')
        self.playlist.pack(fill=Y, expand=YES)

        # Binding Listbox
        self.playlist.bind('<Double-1>', self.instant_play)

        # Configuring ScrollBar for listbox
        y_scroll.config(command=self.playlist.yview)
        x_scroll.config(command=self.playlist.xview)

        # Media control Buttons
        self.play_btn = Button(button_frame, bg=MEDIA_CONTROL_COLOR, image=self.play_ico, width=18, height=18,
                               relief=RAISED, borderwidth=0, command=self.change_N_play)
        self.prev_btn = Button(button_frame, bg=MEDIA_CONTROL_COLOR, image=self.prev_ico, width=18, height=18,
                               relief=RAISED, borderwidth=0, command=lambda: self.switch_song(target='prev'))
        self.next_btn = Button(button_frame, bg=MEDIA_CONTROL_COLOR, image=self.next_ico, width=18, height=18,
                               relief=RAISED, borderwidth=0, command=lambda: self.switch_song(target='next'))
        self.loop_btn = Button(button_frame, bg=MEDIA_CONTROL_COLOR, image=self.loop_off_ico, width=18, height=18,
                               relief=RAISED, borderwidth=0, command=self.loop_song)
        self.stop_btn = Button(button_frame, bg=MEDIA_CONTROL_COLOR, image=self.stop_ico, width=18, height=18,
                               relief=RAISED, borderwidth=0, command=self.stop)

        self.play_btn.image = self.play_ico
        self.loop_btn.image = self.loop_off_ico

        self.prev_btn.pack(side=LEFT)
        self.play_btn.pack(side=LEFT)
        self.next_btn.pack(side=LEFT)
        self.loop_btn.pack(side=LEFT, padx=5)
        self.stop_btn.pack(side=LEFT)

        # Duration Widgets
        self.elapsedTime = Label(button_frame, text='--:--:--', bd=0, relief=GROOVE, bg='#fff', fg='#000')
        self.elapsedTime.pack(side=LEFT, padx=1, anchor=E, ipadx=10)

        # Duration Slider
        self.duration_slider = ttk.Scale(button_frame, from_=0, to=f'{int(self.duration)}', orient=HORIZONTAL, value=0, command=self.slide, length=400)
        self.duration_slider.pack(side=LEFT, padx=3, ipadx=10)

        # # Temp Label
        # self.slider_label = Label(button_frame, text='', bg='#fff')
        # self.slider_label.pack()

        # Total length of Song
        self.totalTime = Label(button_frame, text='--:--:--', bd=0, relief=GROOVE, bg='#fff', fg='#000')
        self.totalTime.pack(side=LEFT, padx=1, anchor=W)

        # Duration Widgets Ends

        # Initialization ends

    def play_time(self):
        # Grab Elapsed Time
        # mixer.music.load(file)
        current_time = mixer.music.get_pos() // 1000

        # Throw up temp Label to get Data
        # self.slider_label.config(text=f'Slider: {int(self.duration_slider.get())} and Song Pos: {int(current_time)}')

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
                self.play_btn.image = self.play_ico
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

        if self.play_btn.image == self.play_ico:
            # start playing
            self.play()
            self.play_btn.config(image=self.pause_ico)
            self.play_btn.image = self.pause_ico

    def open_folder(self):
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

            elif self.playingState == 'new' and self.play_btn.image == self.play_ico:
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

        self.play_btn.config(image=self.play_ico)
        self.play_btn.image = self.play_ico

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

        if self.play_btn.image != self.play_ico:
            self.play_btn.config(image=self.pause_ico)
            self.play_btn.image = self.pause_ico

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
        if self.play_btn.image == self.play_ico:
            # start playing
            self.play()
            self.play_btn.config(image=self.pause_ico)
            self.play_btn.image = self.pause_ico
        else:
            self.pause()
            self.play_btn.config(image=self.play_ico)
            self.play_btn.image = self.play_ico

    def loop_song(self):
        if self.loop_btn.image == self.loop_on_ico:
            self.loop = False
            self.loop_btn.config(relief=RAISED)
            self.loop_btn.config(image=self.loop_off_ico)
            self.loop_btn.image = self.loop_off_ico
        else:
            self.loop = True
            self.loop_btn.config(relief=SUNKEN)
            self.loop_btn.config(image=self.loop_on_ico)
            self.loop_btn.image = self.loop_on_ico

    def delete_song(self):
        # Change the icon of Play Button
        if self.play_btn.image == self.play_ico:
            self.play_btn.config(image=self.pause_ico)
            self.play_btn.image = self.pause_ico

        self.playlist.delete(ANCHOR)
        # Stop music if it's playing
        if self.playingState != 'stopped':
            self.playingState = 'stopped'
            mixer.music.stop()

    def clear_playlist(self):
        # Change the icon of Play Button

        self.playlist.delete(0, END)
        # Stop music if it's playing
        if self.playingState != 'stopped':
            self.playingState = 'stopped'
            mixer.music.stop()

        if self.play_btn.image == self.play_ico:
            self.play_btn.config(image=self.pause_ico)
            self.play_btn.image = self.pause_ico


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
