'''
Change all times in a SRT file (UTF-8)
Author: J. Grätzer, 2020-01-22

Needs this file _srtTimeShifter.ini
-----------------------------------
inputFileName = "test.srt"
addSeconds = -25.7

Example input:
--------------
SRT input from file:
1
00:00:05,468 --> 00:00:09,484
First subtitle line 1
First subtitle line 2

2
00:00:09,484 --> 00:00:13,244
Second subtitle

'''
import re

# --- SETTINGS ---
iniFileName = u"srtTimeShifter.ini"

# --- FUNCTIONS ---
def hhmmsssssLineToSecondsFloat(line):
    ''' Converts time-string "HH:MM:SS,SSS" or "HH:MM:SS.SSS"
        to seconds (float).
        Returns None, if string doesn't match
    '''
    # Pattern für den Match auf 'nn:nn:nn --> nn:nn:nn'
    timestampPattern = re.compile(r'(\d+)\:(\d+)\:([\d,\.]+)')

    m = timestampPattern.search(line)
    if m:
        #print(m.groups())      # Angabe der Match-Inhalte aller Gruppen als Tupel
        #print(m.group(0))      # bzw.: m.group() ... Alles von erster bis letzter Gruppe
        #print(m.group(1))      # Angabe des Match-Inhalts der 1. Gruppe als String, usw
        #print(m.group(2))
        
        hhStr = m.group(1)
        mmStr = m.group(2)
        ssStr = m.group(3)
        ssStr = ssStr.replace(',', '.')
        
        hhInt = int(hhStr)
        mmInt = int(mmStr)
        ssFloat = float(ssStr)
        timeFloat = (hhInt * 60 + mmInt) * 60 + ssFloat
        return timeFloat
    else:
        return None

def hhmmsssssToSecondsFloat(hhStr, mmStr, ssStr):
    ''' Converts time-values h, m, s to seconds (float)
        Returns timeFloat (float)
    '''
    hhInt = int(hhStr)
    mmInt = int(mmStr)
    ssFloat = float(ssStr)
    timeFloat = (hhInt * 60 + mmInt) * 60 + ssFloat
    return timeFloat

def secondsFloatToHhmmsssss(timeFloat):
    ''' Converts seconds (float) to time-string "HH:MM:SS.SSS"
        Returns timeString
    '''
    mm, ss = divmod(timeFloat, 60)
    hh, mm = divmod(mm, 60)
    timeString = '{:02d}:{:02d}:{:06.3f}'.format(int(hh), int(mm), ss) # Python 3
    return timeString


# --- MAIN SCRIPT ---
print("Job start.")
# read the ini-file into linesList
with open(iniFileName, encoding="utf8") as f:
    iniLinesList = f.readlines()

# get inFileName and addSecondsFloat from iniLinesList
inputFileName = ""
addSecondsFloat = 0
for line in iniLinesList: # Ausgabe Textdatei
    # delete comments after ";"
    commentStart = line.find(";")
    if commentStart >= 0 :
        line = line[0:commentStart]
        
    # remove leading and trailing white spaces 
    line = line.strip()  
    
    # get the values of inputFileName and addSecondsFloat
    iniKeyValue = line.split("=", maxsplit=1)
    if len(iniKeyValue) > 1 :
        key = iniKeyValue[0].strip()
        value = iniKeyValue[1].strip()
        #print ("found a key: " + key + " with value: " + value)  # Test
        if key == "inputFileName" :
            inputFileName = value
            # Entferne Anführungszeichen zu Beginn und Ende des Strings
            if inputFileName[0] == "\"" :
                inputFileName = inputFileName[1:]
            if inputFileName[-1] == "\"" :
                inputFileName = inputFileName[:-1]
            
        elif key == "addSeconds" :
            addSecondsFloat = float(value)
            
print ("inputFileName=" + inputFileName)  # Test
print ("addSecondsFloat=" + str(addSecondsFloat))  # Test

# read the SRT file into linesList
with open(inputFileName, encoding="utf8") as f:
    linesList = f.readlines()

# Pattern für den Match auf 'nn:nn:nn --> nn:nn:nn'
timestampPattern = re.compile(r'(\d+)\:(\d+)\:([\d,\.]+) --> (\d+)\:(\d+)\:([\d,\.]+)')

# Alle Zeilen durchlaufen, Daten rausfischen und in Liste "outDataArray" schreiben
textOutput = ""    # Variable deklarieren
outDataList = list()

outLineCounter = 0
for line in linesList:   # Folgende Zeilen der Ausgabe
    line = line.strip()
    # Wenn jetzt Match auf 'nn:nn:nn --> nn:nn:nn', dann beide Zeitwerte ermitteln
    m = timestampPattern.search(line)
    if m:
        #print(m.groups())      # Angabe der Match-Inhalte aller Gruppen als Tupel
        #print(m.group(0))      # bzw.: m.group() ... Alles von erster bis letzter Gruppe
        #print(m.group(1))      # Angabe des Match-Inhalts der 1. Gruppe als String, usw
        #print(m.group(2))
        #print(m.group(3))
        #print(m.group(4))
        #print(m.group(5))
        #print(m.group(6))
        
        hoursStartStr = m.group(1)
        minutsStartStr = m.group(2)
        secondsStartStr = m.group(3)
        secondsStartStr = secondsStartStr.replace(',', '.')

        hoursEndStr = m.group(4)
        minutsEndStr = m.group(5)
        secondsEndStr = m.group(6)
        secondsEndStr = secondsEndStr.replace(',', '.')
        
        startTime = hhmmsssssToSecondsFloat(hoursStartStr, minutsStartStr, secondsStartStr)
        endTime = hhmmsssssToSecondsFloat(hoursEndStr, minutsEndStr, secondsEndStr)

        # Empty the textOutput for next subtitle text
        textOutput = "";
        
        # Calculate the new times
        startTimeOutput = startTime + addSecondsFloat
        if startTimeOutput < 0 :
            startTimeOutput = 0
        endTimeOutput = endTime + addSecondsFloat
        if endTimeOutput < 0 :
            endTimeOutput = 0
            
        # Add the line to outDataList
        startTimeOutputStr = secondsFloatToHhmmsssss(startTimeOutput)
        endTimeOutputStr = secondsFloatToHhmmsssss(endTimeOutput)
        outputLine = startTimeOutputStr + " --> " + endTimeOutputStr
        outputLine = outputLine.replace('.', ',')   # In SRT data we use "," insead "."     
        print(outputLine)  # Test
        
        outDataList.append(outputLine)
        outDataList.append("\n")
        
    else :
        # print("Test: This is a empty line");   # Test
        outLineCounter += 1
        
        # Add that line to the output too
        outDataList.append(line)
        outDataList.append("\n")

# Write the output to destination file
outFilename = inputFileName + "_new.srt"
with open(outFilename, 'w', encoding="utf8") as f :
    for item in outDataList :
        f.write(item)

print("Job done: " + outFilename)
