import plexapi
from plexapi.server import PlexServer
import json
import time




def WriteSessionToDisk(session):
    with open('plexnowplaying.txt', 'w') as nowPlayingFile:
        if(isinstance(session,  plexapi.video.MovieSession)):
            nowPlayingFile.write(session.title)
        elif(isinstance(session,  plexapi.video.ClipSession)):
            nowPlayingFile.write("(Trailer / Clip) " + session.title);
        else:
            nowPlayingFile.write(session.grandparentTitle + " S" + str(session.parentIndex) + "E" + str(session.index) + " - " + session.title)
    
def ReadSessions(baseurl, token, myUser):
    ourSession = None
    plex = PlexServer(baseurl, token)
    for session in plex.sessions():
        #print(session.grandparentTitle + "\nS" + str(session.parentIndex) + "E" + str(session.index) + ": " + session.title)
        if(session.user.username == myUser):
            # this is what we care about
            ourSession = session;

    if(ourSession is None):
        print("Failed to get session")
    else:
        WriteSessionToDisk(ourSession);

if __name__ == '__main__':
    print("Starting check")
    baseurl = 'http://192.168.4.203:32400'
    token = 'J77kbzR8Wq1BJnz_ssMV'
    myUser = 'jamie.935'
    while True:
        ReadSessions(baseurl, token, myUser);
        time.sleep(2)
