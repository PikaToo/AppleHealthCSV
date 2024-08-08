import pandas as pd

FILENAME = 'apple_health_export_2024-08-07.csv'

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

## print data
# print(health)
# print(health.columns)

## export to csv
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

## print data
# print(steps)

## export to csv
steps.to_csv('processed_steps_' + FILENAME, index=True)