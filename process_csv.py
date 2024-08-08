import pandas as pd

FILENAME = 'apple_health_export_2024-08-07.csv'

#### GENERAL TOTAL PROCESSING
## get csv
health = pd.read_csv(FILENAME)

## get rid of unimportant columns
health.drop('locale', axis=1, inplace=True)
health.drop('BloodType', axis=1, inplace=True)
health.drop('CardioFitnessMedicationsUse', axis=1, inplace=True)
health.drop('BiologicalSex', axis=1, inplace=True)
health.drop('FitzpatrickSkinType', axis=1, inplace=True)
health.drop('key', axis=1, inplace=True)
health.drop('DateOfBirth', axis=1, inplace=True)
health.drop('creationDate', axis=1, inplace=True)
health.drop('sourceVersion', axis=1, inplace=True)
health.drop('sourceName', axis=1, inplace=True)
health.drop('device', axis=1, inplace=True)

## remove unusable data
health.dropna(axis=0, how='any', inplace=True)

## print data
# print(health)
# print(health.columns)

## export to csv
health.to_csv('processed_' + FILENAME, index=False)


#### STEP COUNTING
## get csv
# health = pd.read_csv('processed_' + FILENAME)
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