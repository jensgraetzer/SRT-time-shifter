'''
Change all times in a SRT file: Add some seconds
Author: J. Grätzer, 2020-01-22

Input: 2 files
* Subtitle-file in SRT format, UTF-8
* The file srtTimeShifter.ini
  ----------------------------------
  | inputFileName = "filename.srt" |
  | addSeconds = -25.7             |
  ----------------------------------

Output is: filename.srt_new.srt

'''
import re

# --- SETTINGS ---
iniFileName = "srtTimeShifter.ini"

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
        ssStr = ssStr.replace(',', '.')   # In SRT files number format is 1,23 
        
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
# read the INI-file into linesList
with open(iniFileName, "r", encoding="utf-8-sig") as f:
    iniLinesList = f.readlines()

# get values inFileName and addSecondsFloat from iniLinesList
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

        # Remove " from begin and end of value (if any)
        if value[0] == "\"" :
            value = value[1:]
        if value[-1] == "\"" :
            value = value[:-1]
        
        # Store the values in variables
        if key == "inputFileName" :
            inputFileName = value

        elif key == "addSeconds" :
            addSecondsFloat = float(value)
            
print ("inputFileName=" + inputFileName)  # Test
print ("addSecondsFloat=" + str(addSecondsFloat))  # Test

# Read the SRT file into linesList
with open(inputFileName, "r", encoding="utf-8-sig") as f:
    linesList = f.readlines()

# Pattern für den Match auf 'nn:nn:nn --> nn:nn:nn'
timestampPattern = re.compile(r'(\d+)\:(\d+)\:([\d,\.]+) --> (\d+)\:(\d+)\:([\d,\.]+)')

# Process all lines, write zhe list "outDataArray"
textOutput = ""
outDataList = list()
outLineCounter = 0
for line in linesList:
    line = line.strip()
    # Is there a match on 'nn:nn:nn --> nn:nn:nn'? Then calculate new times!
    m = timestampPattern.search(line)
    if m:
        
        hoursStartStr = m.group(1)
        minutsStartStr = m.group(2)
        secondsStartStr = m.group(3)
        secondsStartStr = secondsStartStr.replace(',', '.') # In SRT files number format is 1,23

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
        outputLine = outputLine.replace('.', ',')  # In SRT files number format is 1,23     
        print(outputLine)  # Test
        
        outDataList.append(outputLine)
        outDataList.append("\n")
        
    else :
        # print("Test: This is an empty line");   # Test
        outLineCounter += 1
        
        # Add that line to the output too
        outDataList.append(line)
        outDataList.append("\n")

# Write the output to destination file
outFilename = inputFileName + "_new.srt"
with open(outFilename, 'w', encoding="utf-8") as f :
    for item in outDataList :
        f.write(item)

print("Job done: " + outFilename)

