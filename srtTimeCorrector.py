'''
Change all times in a SRT file to a video with slightly different speed
Author: J. Grätzer, 2021-06-14

Input: 2 files
* Subtitle-file in SRT format, UTF-8
* The file srtTimeCorrector.ini
  ---------------------------------
  | inputFileName = test.srt      |
  | time1oldInSRT = 00:01:15.700  | ... time1 is near the start of the video
  | time1inVideo  = 00:01:20.100  |
  | time2oldInSRT = 01:20:58.500  | ... time2 is near the end of the video
  | time2inVideo  = 01:20:54.200  |
  ---------------------------------

Output is: filename.srt_new.srt

'''
import re
from decimal import Decimal

# --- SETTINGS ---
iniFileName = "srtTimeCorrector.ini"

# --- FUNCTIONS ---
def hhmmsssssLineToSecondsFloat(line):
    ''' Converts time-string "HH:MM:SS.SSS"
        to seconds (float).
        Returns None, if string doesn't match
    '''
    # Pattern für den Match auf 'nn:nn:nn --> nn:nn:nn'
    timestampPattern = re.compile('(\d+)\:(\d+)\:([\d,\.]+)')

    m = timestampPattern.search(line)
    if m:
       
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
    '''
    hhInt = int(hhStr)
    mmInt = int(mmStr)
    ssFloat = float(ssStr)
    timeFloat = (hhInt * 60 + mmInt) * 60 + ssFloat
    return timeFloat

def secondsFloatToHhmmsssss(timeFloat):
    ''' Converts seconds (float) to time-string "HH:MM:SS.SSS"
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
            
        elif key == "time1oldInSRT" :
            t1OldStr = value
            
        elif key == "time1inVideo" :
            t1NewStr = value
            
        elif key == "time2oldInSRT" :
            t2OldStr = value
            
        elif key == "time2inVideo" :
            t2NewStr = value
  
#print ("inputFileName=" + inputFileName)  # Test
#print ("time1oldInSRT=" + t1OldStr)  # Test
#print ("time1inVideo=" + t1NewStr)   # Test
#print ("time2oldInSRT=" + t2OldStr)  # Test
#print ("time2inVideo=" + t2NewStr)   # Test

# Read the SRT file into linesList
with open(inputFileName, "r", encoding="utf-8-sig") as f:
    linesList = f.readlines()

# Calculate the time values
t1Old = hhmmsssssLineToSecondsFloat(t1OldStr)
t1New = hhmmsssssLineToSecondsFloat(t1NewStr)
t2Old = hhmmsssssLineToSecondsFloat(t2OldStr)
t2New = hhmmsssssLineToSecondsFloat(t2NewStr)
deltaOld = t2Old - t1Old
deltaNew = t2New - t1New
coeff = deltaNew/deltaOld    # this is the speed coefficient
bias = t1New - t1Old * coeff # this is the bias
        # So the time calculation is: posNew = posOld * coeff + bias

# Regex-pattern for 'nn:nn:nn --> nn:nn:nn'
timestampPattern = re.compile('(\d+)\:(\d+)\:([\d,\.]+) --> (\d+)\:(\d+)\:([\d,\.]+)')

# Process all lines and write output
textOutput = ""
outDataList = list()

outLineCounter = 0
for line in linesList:
    line = line.strip()
    # If there is a match on 'nn:nn:nn --> nn:nn:nn', calculate new times
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

        # Old text is obsolete
        textOutput = "";
        
        # Calculate new times: posNew = posOld * coeff + bias
        startTimeOutput = startTime * coeff + bias
        endTimeOutput = endTime * coeff + bias
        
        # Calculate new line, append to outDataList
        startTimeOutputStr = secondsFloatToHhmmsssss(startTimeOutput)
        endTimeOutputStr = secondsFloatToHhmmsssss(endTimeOutput)
        outputLine = startTimeOutputStr + " --> " + endTimeOutputStr
        outputLine = outputLine.replace('.', ',')   # In SRT files number format is 1,23    
        #print(outputLine)  # Test
        
        outDataList.append(outputLine)
        outDataList.append("\n")

    else :
        # print("Empty line");   # Test
        outLineCounter += 1
        
        # Append the empty line
        outDataList.append(line)
        outDataList.append("\n")

# Store the data in a new SRT file
outFilename = inputFileName + "_new.srt"
with open(outFilename, 'w', encoding="utf-8") as f:
    for item in outDataList:   # Write all lines into file
        f.write(item)

print("Job done: " + outFilename)



