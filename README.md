# SRT-time-shifter
This very simple Python script shifts all the times in a SRT subtitle file by a given time span.

Let's say, you have subtitles of a mediafile. The subtitles are in the SRT format. And you want to shift all subtitle times by a given time span. Than write the name of the SRT file and the time span into the file srtTimeShifter.ini. Next, run the script srtTimeShifter.py. The script reads the subtitle file and outputs a new subtitle file. The whole process is shown in this Data Processing Map:

![Data Processing Map](srtTimeShifter_dataProcessingMap.png)

Here is an example of the srtTimeShifter.ini file:

inputFileName = "file.srt"

addSeconds = -3.435
