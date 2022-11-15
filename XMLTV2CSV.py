import xml.etree.ElementTree as ET
from datetime import datetime

import urllib.request
import shutil

XMLTVURL = 'http://192.168.4.139:34400/xmltv/xteve.xml'
XMLTVFile = "xmltv.xml"

# Download the file from `url` and save it locally under `file_name`:
with urllib.request.urlopen(XMLTVURL) as response, open(XMLTVFile, 'wb') as out_file:
    shutil.copyfileobj(response, out_file)

def ConvertTimeToTimeslot(datetime):
    # timeslot 36 maps to 10:30 pm local time sync with system timezone set to 6 and daylight savings true
    # timeslot 36 maps to 12:30 AM with system tz set to 8 (central?)

    # so 10 pm would be the 44th 30 minute slot in the day starting at 0 plus one for the :30, so 45 is 10:30 "normally"
    # so (10 * 4) + (1) - 7 gets us to 36 from tz 6 fuck doing the math otherwise but I guess
    # I can use that as a basis and do math from there

    # of course a :30 would be an even timeslot, timeslot 0 doesn't exist, 1 is :00

    # HOUR TIMES FOUR for a 24 HOUR CLOCK DUMMY
    # 2x2x2x30 mins lol
    # so 1 + (hour * 4 + (mins > 30 ? 1 : 0))
    minAdjust = 0;

    #timezone adjust
    tzAdjust = 7;
    
    if datetime.minute >= 30:
        minAdjust = 1;
    # due to timezone adjust, could wrap
    adjusted = (int(datetime.hour) * 4 + (minAdjust) - tzAdjust);
    if(adjusted >=49): adjusted = adjusted - 48;
    return (adjusted);

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

for child in root:
    if(child.tag == 'channel'):
        sourceIdentifier = ''
        channelNumber = child.attrib['id']
        timeslotMask = ''
        callLetters = ''

        flags = 'none'
        for channelinfo in child:
            if(channelinfo.tag == 'display-name'):
                channelName = channelinfo.text
                sourceIdentifier = channelName.split(" ")[0]
                callLetters = sourceIdentifier

                #for later
                channelMap.update({channelNumber : callLetters});
        
#            print(str(sourceIdentifier) + ',' + str(channelNumber) + ',,' + str(callLetters) + ',none')
        #channelCSV = channelCSV + str(sourceIdentifier) + ',' + str(channelNumber) + ',,' + str(callLetters) + ',none\n'

    elif(child.tag == 'programme'):
        sourceIdentifier = ''
        programName = ''
        flags = 'none'

        progstart = datetime.strptime(child.get('start'), '%Y%m%d%H%M%S +0000')
        progend = datetime.strptime(child.get('stop'), '%Y%m%d%H%M%S +0000')
        channel = child.get('channel')
        
        for programinfo in child:
            if(programinfo.tag == 'title'):
                programName = programinfo.text.replace(",", "")

        sourceIdentifier = channel.replace(",", "")

        # length is determined by start time - stop time
        proglen = progend - progstart;

        # 
        programming.append([progstart, channel, programName, (proglen.seconds/60)])

        # timeslot is "horizontal" - the sample file has sequential timeslot numbers, 30 mins each, skip X numbers for long
    

        #programCSV = programCSV + str(timeslot) + ',' + str(sourceIdentifier) + ',' + str(programName) + ',none\n'



# to build programcsv, start with a channel, get it's programs, ordered by date, and write a record, then deduct 30 mins from
# total time and again until done

for program in programming[:10]:
    print("--- Slot: " + str(ConvertTimeToTimeslot(program[0])) + " (" + str(program[0]) + ") Channel: " + program[1] + " " + program[2] + " ---");

    programCSV = programCSV + str(42) + ',' + str(program[1]) + ',' + str(program[2]) + ',none\n'

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

