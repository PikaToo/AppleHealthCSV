import pandas as pd



# modify this string below to match the file name of your health data CSV's name
FILENAME = 'apple_health_export_2024-08-07.csv'

# switch this to false if you want hearing_ to use OSHA values for its db cutoffs instead of NIOSH values
NIOSH_INSTEAD_OF_OSHA = True

# determines whether days with no measurements are dropped or set as 0
KEEP_ACTIVITY_NA = True
KEEP_HEARING_NA = True
KEEP_MOBILITY_NA = True


#### General Total Processing ####
def get_times_and_data():
    ## get csv
    total_data = pd.read_csv(FILENAME, dtype='string', usecols=['type', 'value', 'unit', 'startDate', 'endDate'])

    ## remove unusable data
    total_data.dropna(axis=0, how='any', inplace=True)

    ## remove time zone information and convert to pandas date_time
    total_data['startDate'] = pd.to_datetime(total_data['startDate'].str[:-6])
    total_data['endDate'] = pd.to_datetime(total_data['endDate'].str[:-6])

    ## cast value to numeric; for some reason pandas struggled to do this when reading 
    ##  from csv initially, so reading it as a string and then casting here
    total_data['value'] = pd.to_numeric(total_data['value'])

    earliest_date = total_data['startDate'].min().date()
    latest_date = total_data['endDate'].max().date()

    time_indices = pd.DataFrame(pd.date_range(earliest_date, latest_date), columns=['Date'])

    return time_indices, total_data



#### ACTIVITY ####
def activity(timestamps, data):
    """
    This processes StepCount, DistanceWalkingRunning, and FlightsClimbed.
    
    For simplicity and avoiding non-integers for our counts, we take all action as having 
    happened at the endDate and entirely ignore startDate. 

    This means that the between-hour measurements are not entirely accurate, but in general
    this only leads to error of some measurement being placed an hour later than it should be.
    """

    ## get data we need
    steps = data.loc[data['type'] == 'StepCount'].copy()
    distance = data.loc[data['type'] == 'DistanceWalkingRunning'].copy()
    flights = data.loc[data['type'] == 'FlightsClimbed'].copy()

    ## get date from endDate; round down to the nearest day
    steps['Date'] = steps['endDate'].dt.floor('d')
    distance['Date'] = distance['endDate'].dt.floor('d')
    flights['Date'] = flights['endDate'].dt.floor('d')
    
    ## get rid of unimportant columns
    steps.drop(columns=['type', 'unit', 'startDate', 'endDate'], inplace=True)
    distance.drop(columns=['type', 'unit', 'startDate', 'endDate'], inplace=True)
    flights.drop(columns=['type', 'unit', 'startDate', 'endDate'], inplace=True)

    ## merge dates
    steps    = pd.DataFrame(steps.groupby('Date')['value'].sum())
    distance = pd.DataFrame(distance.groupby('Date')['value'].sum())
    flights  = pd.DataFrame(flights.groupby('Date')['value'].sum())

    ## merge tables; fill outer because we want to keep days with 0 activity
    activity_db = timestamps.copy()
    activity_db = pd.merge(activity_db, steps, on='Date', how='left')
    activity_db = pd.merge(activity_db, distance, on='Date', copy=False, how='left')
    activity_db = pd.merge(activity_db, flights, on='Date', copy=False, how='left')
    activity_db.columns = ['Date', 'Steps Taken (count)', 'Distance Walked (km)', 'Flights Climbed (count)']

    if KEEP_ACTIVITY_NA:
        activity_db.fillna(0, inplace=True)
    else:
        activity_db.dropna(0, inplace=True)

    ## export to csv
    activity_db.to_csv('activity_' + FILENAME, index=False, float_format='%g')



#### HEARING ####
def hearing(timestamps, data):
    """
    This processes HeadphoneAudioExposure.
    
    We get the time for which each db level is recorded for each day. 

    For simplicity and avoiding non-integers for our counts, we take all action as having 
    happened at the endDate and entirely ignore startDate. 

    This means that the between-hour measurements are not entirely accurate, but in general
    this only leads to error of some measurement being placed an hour later than it should be.
    """
    ## get data we need
    hearing = data.loc[data['type'] == 'HeadphoneAudioExposure'].copy()

    ## get rid of unimportant columns
    hearing.drop(columns=['type', 'unit'], inplace=True)

    ## we will split measurements that span across two days into two separate measurements,
    ##  one per each day

    mask = hearing['startDate'].dt.date != hearing['endDate'].dt.date

    values_before_midnight = hearing[mask].copy()
    values_before_midnight['endDate'] = values_before_midnight['startDate'].dt.normalize() + pd.Timedelta(hours=23, minutes=59, seconds=59)

    values_after_midnight = hearing[mask].copy()
    values_after_midnight['startDate'] = values_after_midnight['endDate'].dt.normalize()

    hearing = pd.concat([hearing[~mask], values_before_midnight, values_after_midnight], ignore_index=True)

    ## converting from startDate/endDate to Date/Duration
    hearing['Duration'] = hearing['endDate'].sub(hearing['startDate']).astype('int64') / 10**9 / 60 / 60
    hearing['Date'] = hearing['endDate'].dt.floor('d')
    hearing.drop(columns=['startDate', 'endDate'], inplace=True)


    ## get total time that db was being measured
    hearing_db = timestamps.copy()
    hearing_db['Total Time (hours)'] = hearing_db['Date'].map(hearing.groupby('Date')['Duration'].sum())
    
    ## get average db
    avg_db = (hearing['value'] * hearing['Duration']).groupby(hearing['Date']).sum() / hearing['Duration'].groupby(hearing['Date']).sum()
    hearing_db['Average dB'] = hearing_db['Date'].map(avg_db)

    if (NIOSH_INSTEAD_OF_OSHA):
        ## NIOSH standards
        hearing_db['>85 dB (hours)'] = hearing_db['Date'].map(hearing[hearing['value']>85].groupby('Date')['Duration'].sum())
        hearing_db['>88 dB (hours)'] = hearing_db['Date'].map(hearing[hearing['value']>88].groupby('Date')['Duration'].sum())
        hearing_db['>91 dB (hours)'] = hearing_db['Date'].map(hearing[hearing['value']>91].groupby('Date')['Duration'].sum())
        hearing_db['>94 dB (hours)'] = hearing_db['Date'].map(hearing[hearing['value']>94].groupby('Date')['Duration'].sum())
        hearing_db['>97 dB (hours)'] = hearing_db['Date'].map(hearing[hearing['value']>97].groupby('Date')['Duration'].sum())
        hearing_db['>100 dB (hours)'] = hearing_db['Date'].map(hearing[hearing['value']>100].groupby('Date')['Duration'].sum())


    else:
        ## OSHA standards
        hearing_db['>90 dB (hours)'] = hearing_db['Date'].map(hearing[hearing['value']>90].groupby('Date')['Duration'].sum()).fillna(0)
        hearing_db['>95 dB (hours)'] = hearing_db['Date'].map(hearing[hearing['value']>95].groupby('Date')['Duration'].sum()).fillna(0)
        hearing_db['>100 dB (hours)'] = hearing_db['Date'].map(hearing[hearing['value']>100].groupby('Date')['Duration'].sum()).fillna(0)
        hearing_db['>105 dB (hours)'] = hearing_db['Date'].map(hearing[hearing['value']>105].groupby('Date')['Duration'].sum()).fillna(0)
        hearing_db['>110 dB (hours)'] = hearing_db['Date'].map(hearing[hearing['value']>110].groupby('Date')['Duration'].sum()).fillna(0)
        hearing_db['>115 dB (hours)'] = hearing_db['Date'].map(hearing[hearing['value']>115].groupby('Date')['Duration'].sum()).fillna(0)

    if KEEP_HEARING_NA:
        hearing_db.fillna(0, inplace=True)
    else:
        hearing_db.dropna(0, inplace=True)
    
    ## export to csv
    hearing_db.to_csv('hearing_' + FILENAME, index=False, float_format='%g')


#### MOBILITY ####
def mobility(timestamps, data):
    """
    This processes WalkingStepLength, WalkingSpeed, WalkingDoubleSupportPercentage, and 
    WalkingAsymmetryPercentage.
    
    Like activity, we only use endDate and ignore startDate.

    We REMOVE days with 0 measurements. This is because they make it harder to see trends
    on line graphs. 
    """
    ## get data we need
    step_length = data.loc[data['type'] == 'WalkingStepLength'].copy()
    walking_speed = data.loc[data['type'] == 'WalkingSpeed'].copy()
    walking_double_support = data.loc[data['type'] == 'WalkingDoubleSupportPercentage'].copy()
    walking_asymmetry = data.loc[data['type'] == 'WalkingAsymmetryPercentage'].copy()
    
    ## get date from endDate; round down to the nearest day
    step_length['Date'] = step_length['endDate'].dt.floor('d')
    walking_speed['Date'] = walking_speed['endDate'].dt.floor('d')
    walking_double_support['Date'] = walking_double_support['endDate'].dt.floor('d')
    walking_asymmetry['Date'] = walking_asymmetry['endDate'].dt.floor('d')
    
    ## get rid of unimportant columns
    step_length.drop(columns=['type', 'unit', 'startDate', 'endDate'], inplace=True)
    walking_speed.drop(columns=['type', 'unit', 'startDate', 'endDate'], inplace=True)
    walking_double_support.drop(columns=['type', 'unit', 'startDate', 'endDate'], inplace=True)
    walking_asymmetry.drop(columns=['type', 'unit', 'startDate', 'endDate'], inplace=True)

    ## merge dates; don't use outer because we don't care about days with 0 activity
    step_length = pd.DataFrame(step_length.groupby('Date')['value'].agg(['mean', 'min', 'max']))
    walking_speed = pd.DataFrame(walking_speed.groupby('Date')['value'].agg(['mean', 'min', 'max']))
    walking_double_support = pd.DataFrame(walking_double_support.groupby('Date')['value'].agg(['mean', 'min', 'max']))
    walking_asymmetry = pd.DataFrame(walking_asymmetry.groupby('Date')['value'].agg('mean'))
    
    ## merge tables; we don't need timestamps but keeping it for consistency with the other functions
    mobility_db = timestamps.copy()
    mobility_db = pd.merge(mobility_db, step_length, on='Date', how='left')
    mobility_db = pd.merge(mobility_db, walking_speed, on='Date', copy=False, how='left')
    mobility_db = pd.merge(mobility_db, walking_double_support, on='Date', copy=False, how='left')
    mobility_db = pd.merge(mobility_db, walking_asymmetry, on='Date', copy=False, how='left')
    mobility_db.columns = [ 'Date',
                            'Mean Step Length', 'Minimum Step Length', 'Maximum Step Length',
                            'Mean Walking Speed', 'Minimum Walking Speed', 'Maximum Walking Speed',
                            'Mean Double Support', 'Minimum Double Support', 'Maximum Double Support',
                            'Mean Walking Asymmetry' ]

    if KEEP_MOBILITY_NA:
        mobility_db.fillna(0, inplace=True)
    else:
        mobility_db.dropna(0, inplace=True)

    ## export to csv
    mobility_db.to_csv('mobility_' + FILENAME, index=False, float_format='%g')


def main():
    timestamps, total_data = get_times_and_data()
    activity(timestamps, total_data)
    hearing(timestamps, total_data)
    mobility(timestamps, total_data)


if __name__ == "__main__":
    main()