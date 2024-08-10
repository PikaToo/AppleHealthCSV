import pandas as pd



## modify this string below to match the file name of whatever 
## your health data CSV's name is
FILENAME = 'apple_health_export_2024-08-07.csv'




# TODO: convert into functions and also use a main() function


#### General Total Processing ####
## get csv
health = pd.read_csv(FILENAME, 
                     usecols=['type', 'value', 'unit', 'startDate', 'endDate'],
                     dtype='string')

## remove unusable data
health.dropna(axis=0, how='any', inplace=True)

## cast value to numeric; for some reason not able to do this when reading 
##  from csv properly, so reading it as a string and then casting here
health['value'] = pd.to_numeric(health['value'])




#### ACTIVITY ####
#### StepCount, DistanceWalkingRunning, and FlightsClimbed Processing ####
## get csv
steps = health.loc[health['type'] == 'StepCount'].copy()
distance = health.loc[health['type'] == 'DistanceWalkingRunning'].copy()
flights = health.loc[health['type'] == 'FlightsClimbed'].copy()

## get date from endDate
steps['Date'] = pd.to_datetime(steps['endDate'].str[:10])
distance['Date'] = pd.to_datetime(distance['endDate'].str[:10])
flights['Date'] = pd.to_datetime(flights['endDate'].str[:10])

## get rid of unimportant columns
steps.drop(columns=['type', 'unit', 'startDate', 'endDate'], inplace=True)
distance.drop(columns=['type', 'unit', 'startDate', 'endDate'], inplace=True)
flights.drop(columns=['type', 'unit', 'startDate', 'endDate'], inplace=True)

## merge dates
steps = pd.DataFrame(steps.groupby('Date')['value'].sum())
distance = pd.DataFrame(distance.groupby('Date')['value'].sum())
flights = pd.DataFrame(distance.groupby('Date')['value'].sum())

## merge tables
activity = pd.merge(steps, distance, on='Date').merge(flights, on='Date')
activity.columns = ['Steps Taken', 'Distance Walked', 'Flights Climbed']

## export to csv
# print(walking_information)
activity.to_csv('activity_' + FILENAME, index=True, float_format='%g')



#### HEARING ####
#### HeadphoneAudioExposure Processing ####
hearing = health.loc[health['type'] == 'HeadphoneAudioExposure'].copy()

# get date from endDate
hearing['Date'] = pd.to_datetime(hearing['endDate'].str[:10])

## get rid of unimportant columns
hearing.drop(columns=['type', 'unit', 'startDate', 'endDate'], inplace=True)

## TODO: fix this average; it does not take into account time spent recording 
##   also add the time spent on each metric; maybe have time between thresholds 
## merge dates
hearing = hearing.groupby('Date')['value'].agg(['mean', 'min', 'max'])

## export to csv
# print(audio)
hearing.to_csv('hearing_' + FILENAME, index=True, float_format='%g')


#### MOBILITY ####
step_length = health.loc[health['type'] == 'WalkingStepLength'].copy()
step_length['Date'] = pd.to_datetime(step_length['endDate'].str[:10])
step_length.drop(columns=['type', 'unit', 'startDate', 'endDate'], inplace=True)
step_length = step_length.groupby('Date')['value'].agg(['mean', 'min', 'max'])
step_length.columns = ['Mean Step Length', 'Minimum Step Length', 'Maximum Step Length']

walking_speed = health.loc[health['type'] == 'WalkingSpeed'].copy()
walking_speed['Date'] = pd.to_datetime(walking_speed['endDate'].str[:10])
walking_speed.drop(columns=['type', 'unit', 'startDate', 'endDate'], inplace=True)
walking_speed = walking_speed.groupby('Date')['value'].agg(['mean', 'min', 'max'])
walking_speed.columns = ['Mean Walking Length', 'Minimum Walking Speed', 'Maximum Walking Speed']

walking_double_support = health.loc[health['type'] == 'WalkingDoubleSupportPercentage'].copy()
walking_double_support['Date'] = pd.to_datetime(walking_double_support['endDate'].str[:10])
walking_double_support.drop(columns=['type', 'unit', 'startDate', 'endDate'], inplace=True)
walking_double_support = walking_double_support.groupby('Date')['value'].agg(['mean', 'min', 'max'])
walking_double_support.columns = ['Mean Double Support', 'Minimum Double Support', 'Maximum Double Support']

walking_asymmetry = health.loc[health['type'] == 'WalkingAsymmetryPercentage'].copy()
walking_asymmetry['Date'] = pd.to_datetime(walking_asymmetry['endDate'].str[:10])
walking_asymmetry.drop(columns=['type', 'unit', 'startDate', 'endDate'], inplace=True)
walking_asymmetry = pd.DataFrame(walking_asymmetry.groupby('Date')['value'].agg('mean'))
walking_asymmetry.columns = ['Average Walking Asymmetry']

mobility = pd.merge(step_length, walking_speed, on='Date').merge(pd.merge(walking_double_support, walking_asymmetry, on='Date'), on='Date')

mobility.to_csv('mobility_' + FILENAME, index=True, float_format='%g')