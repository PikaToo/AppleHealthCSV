# Apple Health CSV Processesor

A script that converts Apple Health CSVs from Jameno's script (https://github.com/jameno/Simple-Apple-Health-XML-to-CSV/) into several CSV files for easier human legibility. 

## How To Use 

### 1 - Obtain Starting CSV
Follow the instructions under Jameno's script (https://github.com/jameno/Simple-Apple-Health-XML-to-CSV/) to obtain a CSV containing your Apple Health Data. Doing this additionally should mean you have Python 3 and Pandas installed in your environment, which are also required for this script to run.

### 2 - Configure The File
There are 5 parameters in the file you may modify. 

FILENAME - Replace this with your filename. Ensure you include .csv at the end.

NIOSH_INSTEAD_OF_OSHA - By default, your processed HeadphoneAudioExposure will include the time spent listening at different dB intervals recommended by NIOSH. You can swap to intervals recommended by OSHA, instead, by setting this to False. 

KEEP_ACTIVITY_NA / KEEP_HEARING_NA / KEEP_MOBILITY_NA - by default, you will have empty rows for each date in which no measurements were recorded. The starting date will be determined by the earliest date any measurement occured, and the last date as the latest date any measurement occured. You can instead have all of these empty rows be removed by setting these parameters to False. 

### 3 - Run The File
Ensure that the CSV file from Jameno's script is in the same folder as the process_apple_health_csv.py script and then run the script. 

## Files Generated
The script only processes the following types of measurements and ignores all others: StepCount, DistanceWalkingRunning, FlightsClimbed, HeadphoneAudioExposure, WalkingStepLength, WalkingSpeed, WalkingDoubleSupportPercentage, and WalkingAsymmetryPercentage.

This script will take a FILENAME to form the following CSV files with the following columns. 

### activity_FILENAME
Date* - the date at which the measured values occured. 

Steps Taken (count) - the number of steps taken that day. 

Distanced Walked - the distance travelled by foot that day. In kilometers for metric users. 

Flights Climbed (count) - the number of flights climbed that day. 


### hearing_FILENAME
Date** - the date at which the measured values occured. 

Average dB - the average dB over all measured dB levels recorded that day. 

\>xx dB (hours) - the time spent above xx dB that day in hours. Can swap between NIOSH and OSHA groupings with the NIOSH_INSTEAD_OF_OSHA parameter.


### mobility_FILENAME
Date* - the date at which the measured values occured. 

Mean Step Length - the average length of each step measurement that day. In centimeters for metric users. 

Minimum Step Length - the smallest step measured that day. In centimeters for metric users. 

Maximum Step Length - the largest step measured that day. In centimeters for metric users. 

Mean Walking Speed - the average walking speed measured that day. In kilometers per hour for metric users. 

Minimum Walking Speed (%) - the slowest walking speed measured that day. In kilometers per hour for metric users. 

Maximum Walking Speed (%) - the fastest walking speed measured that day. In kilometers per hour for metric users. 

Mean Double Support (%) - the average percentage of time both feet were on the ground while walking that day. 

Minimum Double Support - the smallest percentage of time both feet were on the ground in any measurement while walking that day. 

Maximum Double Support - the largest percentage of time both feet were on the ground in any measurement while walking that day. 

Mean Walking Asymmetry (%) - the average percentage of time one foot was travelling faster than another while walking that day. 


### Dates Footnote
*Activity and Mobility both take 'endDate' as being the date at which a measurement occured in its entirety. This means that if you took, say, 30 steps between Tuesday 11:50 PM and Wednesday 12:05 AM, all 30 steps will be counted as having occured on Wednesday 12:05 AM. This avoids having non-integer number of steps, but may be changed in the future to match that of Hearing for greater day accuracy. 

**Hearing will average the measurements across days. If you listened to 15 minutes of 80 dB audio between Tuesday 11:50 PM and Wednesday 12:05 AM, this will be counted as 10 minutes of 80 dB audio for Tuesday and 5 minutes of 80 dB audio for Wednesday. 
