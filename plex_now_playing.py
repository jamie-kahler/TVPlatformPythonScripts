from plexapi.server import PlexServer
import json

baseurl = 'http://192.168.4.156:32400'
token = 'J77kbzR8Wq1BJnz_ssMV'

plex = PlexServer(baseurl, token)

for session in plex.sessions():
    print(session.grandparentTitle + "\nS" + str(session.parentIndex) + "E" + str(session.index) + ": " + session.title)

session = plex.sessions()[0];

JSONString = {"Series": plex.sessions()[0].grandparentTitle, "Season": session.parentIndex, "Episode": session.index, "Title": session.title};
print(json.JSONEncoder().encode(JSONString));
