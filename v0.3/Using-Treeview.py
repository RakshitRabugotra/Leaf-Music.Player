import os
from tkinter import *
from tkinter import ttk
from tkinter import filedialog
from pygame import mixer
from mutagen.mp3 import MP3
from mutagen import MutagenError


DIR = r"E:\Projects & Others\Projects\Projects 2K20\Project Python\Music Player\v1.0\pngs\16"
INITIAL_DIR = ""    # r"E:\Songs"
FONT = ('Open Sans', 12)
RESIZABLE = True   # True if you want the window to be resizable
RESOLUTION = "960x540"
MEDIA_CONTROL_COLOR = '#fff'  # Color of Media
VIDEO_FRAME_COLOR = '#000'    # Color of Video
HIGHLIGHT_COLOR = 'green'
STRIPED_COLOR = '#8dd0d9'
PLAYLIST_ROW_HEIGHT = 20      # Row Height in Playlist Treeview

global count
count = 0


class MusicPlayer:
    def __init__(self, master):

        self.playingState = 'stopped'  # ['playing', 'paused', 'stopped']

        # Various Variables
        self.musicDir = ""
        self.musicFile = ""
        self.SongDict = dict()
        self.file_open_bool = False
        self.old_song_name = ''
        self.DirList = list()
        self.indexDict = dict()
        self.loop = False
        self.selected = []

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

        file_menu.add_command(label="Open...", command=self.open_file)
        file_menu.add_command(label="Open Folder...", command=self.open_folder)
        file_menu.add_separator()
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
        button_frame = Frame(media_control_frame)
        button_frame.pack(side=LEFT, padx=1, pady=1, fill=X)
        # Initialization of Frames Ends

        # Treeview class & ScrollBar class
        playlist_scroll = ttk.Scrollbar(playlist_frame, orient=VERTICAL)
        playlist_scroll.pack(side=RIGHT, fill=Y)
        # Scroll Bar initialization ends

        # Add some style to Treeview
        style = ttk.Style()

        # Pick a Theme
        style.theme_use('default')  # default, clam, alt, vista

        # Configure our treeview colors
        style.configure("Treeview",
                        background='#fff',  # #D3D3D3
                        foreground='black',
                        rowheight=PLAYLIST_ROW_HEIGHT,
                        fieldbackground='#fff'
                        )
        # Change selection color
        style.map('Treeview',
                  background=[('selected', 'green')])

        # Treeview for playlist
        self.playlist = ttk.Treeview(playlist_frame, yscrollcommand=playlist_scroll, selectmode=BROWSE)
        # Pack to the Screen
        self.playlist.pack(pady=1, fill=Y, expand=YES)

        # Bindings
        self.playlist.bind("<Double-1>", self.instant_play)
        # self.playlist.bind('<<TreeviewSelect>>', self.on_select)

        # Configure the ScrollBar
        playlist_scroll.config(command=self.playlist.yview)

        # Define our Columns
        self.playlist['columns'] = ("Name", "Duration")

        # Format our Columns
        self.playlist.column("#0", width=0, stretch=NO)  # Remove 'minwidth', set 'width=0', add parameter 'stretch=NO'
        self.playlist.column("Name", anchor=W, width=140)
        self.playlist.column("Duration", anchor=CENTER, width=100)
        # self.playlist.column("Favorite Pizza", anchor=W, width=140)

        # Create Headings
        self.playlist.heading("#0", text="", anchor=W)
        self.playlist.heading("Name", text="Name", anchor=W)
        self.playlist.heading("Duration", text="Duration", anchor=CENTER)
        # self.playlist.heading("Favorite Pizza", text="Favorite Pizza", anchor=W)

        # Create striped row tags
        self.playlist.tag_configure('oddRow', background='white')
        self.playlist.tag_configure('evenRow', background='#8dd0d9')

        # Media control Buttons
        self.play_btn = Button(button_frame, bg=MEDIA_CONTROL_COLOR, image=self.play_ico, width=18, height=18, relief=RAISED, borderwidth=0, command=self.change_N_play)
        self.prev_btn = Button(button_frame, bg=MEDIA_CONTROL_COLOR, image=self.prev_ico, width=18, height=18, relief=RAISED, borderwidth=0, command=self.previous_song)
        self.next_btn = Button(button_frame, bg=MEDIA_CONTROL_COLOR, image=self.next_ico, width=18, height=18, relief=RAISED, borderwidth=0, command=self.next_song)
        self.loop_btn = Button(button_frame, bg=MEDIA_CONTROL_COLOR, image=self.loop_off_ico, width=18, height=18, relief=RAISED, borderwidth=0, command=self.loop_song)
        self.stop_btn = Button(button_frame, bg=MEDIA_CONTROL_COLOR, image=self.stop_ico, width=18, height=18, relief=RAISED, borderwidth=0, command=self.stop)

        self.play_btn.image = self.play_ico
        self.loop_btn.image = self.loop_off_ico

        self.prev_btn.pack(side=LEFT)
        self.play_btn.pack(side=LEFT)
        self.next_btn.pack(side=LEFT)
        self.loop_btn.pack(side=LEFT, padx=5)
        self.stop_btn.pack(side=LEFT)
        # Initialization ends

        # Treeview class & ScrollBar class ENDS

    def duration(self, audiofile) -> str:
        audio = MP3(audiofile)
        audio_info = audio.info
        # Convert to Hours, Minutes, Seconds
        seconds = int(audio_info.length)
        hours = seconds // 3600
        seconds %= 3600
        mins = seconds // 60
        seconds = seconds % 60

        ret = ""

        if hours < 10:
            if mins < 10:
                if seconds < 10:
                    ret = f"0{hours}:0{mins}:0{seconds}"
                else:
                    ret = f"0{hours}:0{mins}:{seconds}"
            else:
                ret = f"0{hours}:{mins}:{seconds}"
        else:
            ret = f"{hours}:{mins}:{seconds}"

        return ret

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

    def open_file(self):
        try:
            self.musicDir = filedialog.askopenfilename(initialdir=INITIAL_DIR, title='Open File(s)', filetypes=(("mp3 files", "*.mp3"), ("All files", "*")))
        except MutagenError as err:
            print(f"\nOpen a file to continue\nError: {err}")

        if self.playingState == 'playing':
            mixer.music.stop()
            self.play_btn.image = self.play_ico
            self.playingState = 'stopped'

        self.musicFile = self.get_str_attributes(string=self.musicDir, target='name')
        self.musicDir = self.get_str_attributes(string=self.musicDir, target='dir')

        self.SongDict[self.musicFile] = self.musicDir

        self.file_open_bool = True
        print(f"\nMusic File: {self.musicFile}\nMusic Dir {self.SongDict[self.musicFile]}")

        global count
        if count % 2 == 0:
            self.playlist.insert(parent='', index='end', iid=count, text="", values=(self.musicFile, self.duration(self.SongDict[self.musicFile]+'/'+self.musicFile)), tags=('evenRow'))
        else:
            self.playlist.insert(parent='', index='end', iid=count, text="", values=(self.musicFile, self.duration(self.SongDict[self.musicFile]+'/'+self.musicFile)), tags=('oddRow'))
        self.indexDict[self.musicFile] = count
        count += 1

        try:
            selected = self.playlist.focus()
            values = self.playlist.item(selected, 'values')

            self.old_song_name = values[0]
        except IndexError:
            print("\nTreeview is may Empty")

        self.playingState = 'stopped'

        if self.play_btn.image == self.play_ico:
            # start playing
            self.play()
            self.play_btn.config(image=self.pause_ico)
            self.play_btn.image = self.pause_ico

    def open_folder(self):
        self.musicDir = filedialog.askdirectory()
        try:
            item_list = os.listdir(self.musicDir)
            for item in item_list:
                self.DirList.append([item, self.duration(self.musicDir+'/'+item)])
                self.SongDict[item] = self.musicDir
        except FileNotFoundError:
            # self.DirList = ''
            print("Try Again")

        if self.DirList:
            global count
            for record in self.DirList:
                if count % 2 == 0:
                    self.playlist.insert(parent='', index='end', iid=count, text="", values=(record[0], record[1]), tags=('evenRow'))
                else:
                    self.playlist.insert(parent='', index='end', iid=count, text="", values=(record[0], record[1]), tags=('oddRow'))
                self.indexDict[self.musicFile] = count
                count += 1

    def play(self):
        if self.playlist.item(self.playlist.focus(), 'values'):
            if self.old_song_name != self.playlist.item(self.playlist.focus(), 'values')[0] and self.old_song_name != '':
                self.playingState = 'new'
        if self.file_open_bool:
            self.musicFile = self.musicDir + '/' + self.musicFile
        else:
            self.musicFile = self.musicDir + '/' + self.playlist.item(self.playlist.focus(), 'values')[0]

        try:
            print(f'\nIn Play function: Music File: {self.musicFile}')

            mp3 = MP3(self.musicFile)

            if self.playingState == 'stopped':
                mixer.init(frequency=mp3.info.sample_rate)  # Sets the frequency to optimize audio
                if self.playlist.item(self.playlist.focus(), 'values'):
                    if self.old_song_name != self.playlist.item(self.playlist.focus(), 'values')[0] and self.old_song_name != '':
                        mixer.music.load(self.playlist.item(self.playlist.focus(), 'values')[0])
                        if self.loop:
                            mixer.music.play(loops=1000)
                        else:
                            mixer.music.play()
                    else:
                        mixer.music.load(self.musicFile)
                        if self.loop:
                            mixer.music.play(loops=1000)
                        else:
                            mixer.music.play()
                else:
                    mixer.music.load(self.musicFile)
                    if self.loop:
                        mixer.music.play(loops=1000)
                    else:
                        mixer.music.play()

                self.old_song_name = self.get_str_attributes(string=self.musicFile, target='name')
                self.playingState = 'playing'
                print(f'Playing: {self.musicFile}')
                self.file_open_bool = False

            elif self.playingState == 'paused':
                mixer.music.unpause()

            elif self.playingState == 'new' and self.play_btn.image == self.play_ico:
                selected = self.playlist.focus()
                values = self.playlist.item(selected, 'values')

                self.musicFile = self.SongDict[values[0]] + '/' + values[0]
                mixer.music.load(self.musicFile)
                if self.loop:
                    mixer.music.play(loops=1000)
                else:
                    mixer.music.play()

        except MutagenError as e:
            print(f"\nSong not Loaded\nError: {e}")

    def instant_play(self, event):
        file_name = self.playlist.item(self.playlist.focus(), 'values')[0]
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

        self.play_btn.config(image=self.pause_ico)
        self.play_btn.image = self.pause_ico

    def pause(self):
        self.playingState = 'paused'
        mixer.music.pause()

    def stop(self):
        self.playingState = 'stopped'
        self.play_btn.config(image=self.pause_ico)
        self.play_btn.image = self.pause_ico
        mixer.music.stop()

    def next_song(self):
        pass

    def previous_song(self):
        pass

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

    def change_N_play(self):
        if self.play_btn.image == self.play_ico:
            # start playing
            self.play()
            self.play_btn.config(image=self.pause_ico)
            self.play_btn.image = self.pause_ico
        else:
            # pause song
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
