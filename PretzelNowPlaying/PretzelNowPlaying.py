################################
# Author: LintyJuggler90
# Date: 11-29-2020
# Description:  Get the currently playing track from Pretzel Rocks API (v2) and write to file.
#               File containing the output will be inthe same directory as the script.
#               Status messages logged and printed.
#               Exit the script if OBS is not running
################################
import requests
import os
import time
import random
import datetime
from subprocess import check_output, CalledProcessError

# Save the ScriptPath, FilePath, DataPath, and LogPath for repeat use
ScriptPath = os.path.dirname(os.path.abspath(__file__))
FilePath = ScriptPath + "/PretzelTrack.txt"
LogPath = ScriptPath + "/PretzelNowPlaying.log"
DataPath = ScriptPath + "/PretzelNowPlaying.dat"
CurrentSong = ""

def main():
    # Check if OBS is running
    CheckExitState()
    OpenMessage = "[" + datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S") + "] Started PretzelNowPlaying script."
    TeeLog(OpenMessage)
    # Get the TwitchID if not already saved.
    TeeLog("[" + datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S") + "] Getting TwitchID.")
    if os.path.isfile(DataPath):
        DataFile = open(DataPath,"r")
        TwitchID = DataFile.read()
        DataFile.close()
        TeeLog("[" + datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S") + "] Obtained TwitchID from config.")
    else:
        UserName = input("Enter Twitch UserName: ")
        TwitchUserIDURI = "https://twitchuidlookup.herokuapp.com/resolve"
        IDResponse = requests.post(TwitchUserIDURI,data={"names": UserName})
        TwitchID = IDResponse.json()[UserName]
        DataFile = open(DataPath, "x")
        DataFile.write(TwitchID)
        DataFile.close()
        TeeLog("[" + datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S") + "] Obtained TwitchID from API.")
    # Set the PretzelAPI endpoint
    URI = "https://api.pretzel.tv/playing/twitch/" + TwitchID
    # Loop until program is ended.
    while True:
        # Initiate first call before looping.
        CheckMessage = "[" + datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S") + "] Checking Pretzel Rocks API for currently playing song."
        TeeLog(CheckMessage)
        Response = requests.get(URI)
        Retry = False
        while Response.status_code != 200 or Retry == True:
            time.sleep(random.randint(5,10))
            try:
                Response = requests.get(URI)
                Retry = False
            # Wait and retry instead of hard fail if response not received.
            except:
                Retry = True
        Song = (Response.text.split(':'))[1].split("->")[0].strip()
        if os.path.exists(FilePath):
            File = open(FilePath, "r")
            FileSong = File.read()
        else:
            FileSong = ""
        # Write the song to file if it does not match the song recorded in the file.
        if Song[:88] != FileSong[:88]:
            # Save data to file and close.
            if len(Song) > 88:
                SongToFile = Song[:88] + ".."
            else:
                SongToFile = Song
            File = open(FilePath, "w+")
            File.write(SongToFile)
            File.close()
            UpdateMessage = "[" + datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S") + "] Updated song to: " + Song
            TeeLog(UpdateMessage)
            # Sleep 30 seconds before polling again for the song.
            time.sleep(30)
        else:
            # Sleep at a random interval after the first repeat polling.
            time.sleep(random.randint(10,20))
        CheckExitState()

def CheckExitState():
    # Exit if OBS is not running. Prevents leaving the script running unnecessarily in background.
    try:
        Proc = check_output(["pidof","-s","obs"])
    except CalledProcessError:
        Proc = ""
    if Proc == "":
        ExitMessage = "[" + datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S") + "] OBS process not found. Exiting PretzelNowPlaying."
        TeeLog(ExitMessage)
        raise SystemExit
    else:
        return

def TeeLog(Message):
        LogFile = open(LogPath, "a")
        LogFile.write(Message + "\n")
        LogFile.close()
        print(Message)
        return

main()
