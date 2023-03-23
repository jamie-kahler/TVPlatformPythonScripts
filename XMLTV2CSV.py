import xml.etree.ElementTree as ET
from datetime import datetime

import urllib.request
import shutil

XMLTVURL = 'http://192.168.4.182:8409/iptv/xmltv.xml'
XMLTVFile = "xmltv.xml"

# Download the file from `url` and save it locally under `file_name`:
with urllib.request.urlopen(XMLTVURL) as response, open(XMLTVFile, 'wb') as out_file:
    shutil.copyfileobj(response, out_file)

def ConvertTimeToTimeslot(datetime):
    # Timezone 5 observe DST off puts it in sync as of 3/16 (just past spring forward)

    # This has 2:30 PM as timeslot 24
    # TS 43 is midnight, or hour zero

    # to get TS from hour:
    # 43 + (2 * hour) + if(minute > 29, 1, 0) ; if > 48, minus 48
    # 8 AM =
    # (43 + 16 + 

    minAdjust = 0;
    
    if datetime.minute >= 29:
        minAdjust = 1;
    
    timeSlot = 40 + (2 * datetime.hour) + minAdjust
    if(timeSlot > 48): timeSlot = timeSlot - 48
    return (timeSlot);

def GenerateTestData():
    testdata = list(range(1,48,1))
    testCSV = 'timeslot,sourceIdentifier,programName,flags\n';
    for t in testdata:
        testCSV = testCSV + str(t) + ",1," + str(t) + ",none\n"

    f = open('testprograms.csv', 'w', encoding='utf-8')
    f.write(testCSV)
    f.close()
    

GenerateTestData();

tree = ET.parse(XMLTVFile)
root = tree.getroot()

channelCSV = 'sourceIdentifier,channelNumber,timeslotMask,callLetters,flags\n'
programCSV = 'timeslot,sourceIdentifier,programName,flags\n'

channelMap = {}
programming = []

timeslotNow = ConvertTimeToTimeslot(datetime.now());

print("---------------------------------------")
print("Current timeslot: " + str(timeslotNow));
print("---------------------------------------")

for child in root:
    if(child.tag == 'channel'):
        sourceIdentifier = ''
        channelNumber = child.attrib['id'].split('.')[0]
        timeslotMask = ''
        callLetters = ''

        flags = 'none'
        for channelinfo in child:
            if(channelinfo.tag == 'display-name'):
                channelName = channelinfo.text.split('.')[0]
                sourceIdentifier = channelName.split(" ")[0].split('|')[0]
                callLetters = sourceIdentifier

                #for later
                channelMap.update({channelNumber : callLetters});

    elif(child.tag == 'programme'):
        sourceIdentifier = ''
        programName = ''
        flags = 'none'

        progstart = datetime.strptime(child.get('start'), '%Y%m%d%H%M%S +0000')
        progend = datetime.strptime(child.get('stop'), '%Y%m%d%H%M%S +0000')
        channel = str(child.get('channel')).split('.')[0] #stupid ersatz appends .etv in their channels, breaking prevue
        
        for programinfo in child:
            if(programinfo.tag == 'title'):
                programName = programinfo.text.replace(",", "")

        sourceIdentifier = channel.replace(",", "")

        # length is determined by start time - stop time
        proglen = progend - progstart;
        #print(programName + ": Length: " + str(proglen) + " (" + str(progstart) + " to " + str(progend));
        # 
        programming.append([progstart, channel, programName, (proglen.seconds/60)])

#for p in programming: print(p)
# to build programcsv, start with a channel, get it's programs, ordered by date, and write a record, then deduct 30 mins from
# total time and again until done


# walk through channels
# for each, select programming with that channel
# write the top X, then next channel, ez, except it also
# needs to factor length


    
for program in programming:
    programCSV = programCSV + str(ConvertTimeToTimeslot(program[0])) + ',' + str(program[1]).split('|')[0] + ',' + str(program[2]) + ',none\n'

    #print("--- Slot: " + str(ConvertTimeToTimeslot(program[0])) + " (" + str(program[0]) + ") Channel: " + program[1] + " " + program[2] + " ---");

    #programCSV = programCSV + str(ConvertTimeToTimeslot(program[0])) + ',' + str(program[1]).split('|')[0] + ',' + str(program[2]) + ',none\n'

for channel in channelMap:
    print(channel, channelMap[channel]);
    channelCSV = channelCSV + channel + "," + channel + ",," + channelMap[channel] + ",none\n"

#print(channelMap)
#print(programming)
# clean stuff
f = open('yobchannels.csv', 'w', encoding='utf-8')
f.write(channelCSV)
f.close()

f = open('yobprograms.csv', 'w', encoding='utf-8')
f.write(programCSV)
f.close()

