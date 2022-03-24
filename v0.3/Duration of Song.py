from mutagen.mp3 import MP3

PATH = r"E:\Songs\mp3\Bruno Mars - 24K Magic.mp3"


def convert(seconds):
    hours = seconds // 3600
    seconds %= 3600

    mins = seconds // 60
    seconds = seconds % 60

    return hours, mins, seconds


audio = MP3(f"{PATH}")

audio_info = audio.info
length_in_secs = int(audio_info.length)

hours, mins, seconds = convert(length_in_secs)


if hours < 10:
    if mins < 10:
        if seconds < 10:
            print(f"Duration: 0{hours}:0{mins}:0{seconds}")
        else:
            print(f"Duration: 0{hours}:0{mins}:{seconds}")
    else:
        print(f"Duration: 0{hours}:{mins}:{seconds}")
else:
    print(f"Duration: {hours}:{mins}:{seconds}")


# def duration(self):
#     curr_file = self.playlist.curselection()
#     song = self.playlist.get(curr_file)
#
#     song = self.SongDict[song] + '/' + song
#
#     length = time.strftime('%H:%M:%S', time.gmtime(MP3(song).info.length))
#
#     return length

