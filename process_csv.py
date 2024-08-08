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

## export to csv
# print(health)
health.to_csv('processed_' + FILENAME, index=False)




#### StepCount Processing ####
## get csv
steps = health.loc[health['type'] == 'StepCount'].copy()

## get date from endDate
steps['date'] = pd.to_datetime(steps['endDate'].str[:10])

## get rid of unimportant columns
steps.drop('type', axis=1, inplace=True)
steps.drop('unit', axis=1, inplace=True)
steps.drop('startDate', axis=1, inplace=True)
steps.drop('endDate', axis=1, inplace=True)

## merge dates
steps = pd.DataFrame(steps.groupby('date')['value'].sum())

## export to csv
# print(steps)
steps.to_csv('processed_steps_' + FILENAME, index=True)




#### HeadphoneAudioExposure Processing ####
audio = health.loc[health['type'] == 'HeadphoneAudioExposure'].copy()

# get date from endDate
audio['date'] = pd.to_datetime(audio['endDate'].str[:10])

## get rid of unimportant columns
audio.drop('type', axis=1, inplace=True)
audio.drop('unit', axis=1, inplace=True)
audio.drop('startDate', axis=1, inplace=True)
audio.drop('endDate', axis=1, inplace=True)

## TODO: fix this average; it does not take into account time spent recording 
## merge dates
audio = audio.groupby('date')['value'].agg(['mean', 'min', 'max'])

## export to csv
# print(audio)
audio.to_csv('processed_audio_' + FILENAME, index=True)