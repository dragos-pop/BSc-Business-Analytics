import pandas as pd
import math
from shapely.geometry import Point, Polygon
import geopandas as gpd
from datetime import datetime, timezone
import pytz
import numpy as np

MIN_DURATION = 10.0 #minutes
AMS_TIME_ZONE = pytz.timezone('Europe/Amsterdam')
TSTAMP_NEW_BERTH_IN_OPERATION = datetime.timestamp(datetime(2018,10,31))
MAX_DIFFERENCE = 2.0 

duration_df = pd.DataFrame(columns=['MMSI','NAME','IMO','Berth', 'Start', 'End', 'Duration', 'Type', 'A', 'B', 'C', 'D', 'Draught', 'ETA'])

df = pd.read_csv('duration_stay/everything_to_EVOS.csv').sort_values(by='TSTAMP')
df = df[['MMSI','NAME','IMO','NAVSTAT', 'TSTAMP', 'LATITUDE', 'LONGITUDE', 'TYPE', 'DRAUGHT', 'A', 'B', 'C', 'D','ETA']]

berths = gpd.read_file('shapes/Ligplaatsen_zeevaart_.shp')
ship_dict = {}

def coord_lister(geom):
    coords = list(geom.exterior.coords)
    return (coords)

coordinates = berths.geometry.apply(coord_lister)

ak1e2 = Polygon(coordinates[0])
ak1w1 = Polygon(coordinates[1])
ak2e1 = Polygon(coordinates[2])
ak2e3 = Polygon(coordinates[3])
ak2e2 = Polygon(coordinates[4])
ak1w2 = Polygon(coordinates[5])

for i,row in df.iterrows():
    if row['MMSI'] in ship_dict.keys():
        ship_dict[row['MMSI']].append(row)
    else:
        ship_dict[row['MMSI']] = [row]

def create_df_entry(duration_of_stay, berth,start_time, end_time, row, eta):
    global duration_df
    duration_df = duration_df.append([{'MMSI': row['MMSI'],'NAME':row['NAME'],'IMO':row['IMO'], 'Berth': berth, 'Start': start_time.strftime('%Y-%m-%d %H:%M:%S'), 'End': end_time.strftime('%Y-%m-%d %H:%M:%S') ,'Duration':duration_of_stay, 'Type': row['TYPE'], 'A':row['A'], 'B':row['B'], 'C':row['C'], 'D':row['D'], 'Draught': row['DRAUGHT'], 'ETA':eta}], ignore_index=True)

def at_berth(point, date=None):
    return which_berth(point,date) != None
 
def which_berth(point, date=None):
    if ak1e2.contains(point):
        return 'AK 1E1'
    elif ak1w1.contains(point):
        return 'AK 1W1'
    elif ak2e1.contains(point):
        return 'AK 2E2'
    elif ak2e3.contains(point):
        return 'AK 2E2'
    elif ak2e2.contains(point):
        return 'AK 2E2'
    elif (date >= TSTAMP_NEW_BERTH_IN_OPERATION) & (ak1w2.contains(point)):
        return 'AK 1W2'

def merge_entries(df):
    '''Loops through the dataframe and merges the rows where the end time differs up to MAX_DIFFERENCE from the start time of a new entry of that ship.'''

    df['Start'] = [datetime.strptime(time, '%Y-%m-%d %H:%M:%S') for time in list(df['Start'])] 
    df['End'] = [datetime.strptime(time, '%Y-%m-%d %H:%M:%S') for time in list(df['End'])]

    new_df = pd.DataFrame(columns=['MMSI', 'NAME', 'IMO', 'Berth', 'Start', 'End', 'Duration', 'Type', 'A','B', 'C', 'D', 'Draught', 'ETA'])

    for name in df['NAME'].unique():    
        temp = df[df['NAME']==name].reset_index(drop=True)
        
        previous_row = None
        found_same_entry = False

        if len(temp)>=2:
            for i,row in temp.iterrows():
                if previous_row is None:
                    previous_row = 0
                    continue

                if not found_same_entry:
                    previous_row = i-1

                diff = (temp.at[i,'Start'] - temp.at[previous_row,'End']).total_seconds()/3600
                
                if abs(diff < MAX_DIFFERENCE):
                    temp.at[previous_row,'End'] = temp.at[i,'End']
                    temp.at[previous_row, 'Duration'] = round((temp.at[previous_row,'End'] - temp.at[previous_row, 'Start']).total_seconds()/3600,2)
                    temp.at[i,'Start'] = np.nan
                    found_same_entry = True

                else:
                    found_same_entry = False

            temp = temp.dropna(subset=['Start'])
            new_df = pd.concat([new_df, temp], ignore_index=True)
        
        else:  
            new_df = pd.concat([new_df, temp], ignore_index=True)

    new_df = new_df.sort_values(by='Start')
    return new_df

for mmsi in ship_dict.keys():
    start_time = None
    end_time = None

    docked = False
    offset = 0

    for i in range(len(ship_dict[mmsi])):
        five_rows = ship_dict[mmsi][offset:i+1]

        if (i > 4):
            offset += 1

        x_list = [x['LONGITUDE'] for x in five_rows]
        y_list = [x['LATITUDE'] for x in five_rows]
        tstamp_list = [t['TSTAMP'] for t in five_rows]
        eta_list = [x['ETA'] for x in five_rows]
        eta = eta_list[-1]

        centroid = Point(np.mean(x_list), np.mean(y_list))
        centroid_timestamp = round(np.mean(tstamp_list),0)

        if at_berth(centroid,centroid_timestamp) & (docked == False):
            start_time = pytz.utc.localize(datetime.utcfromtimestamp(centroid_timestamp)).astimezone(AMS_TIME_ZONE)
            berth = which_berth(centroid,centroid_timestamp)
            print(ship_dict[mmsi][0])
            docked = True

        elif (at_berth(centroid,centroid_timestamp) == False) & (docked == True):
            end_time = pytz.utc.localize(datetime.utcfromtimestamp(centroid_timestamp)).astimezone(AMS_TIME_ZONE)
            duration_stay =  end_time - start_time

            if duration_stay.total_seconds()/60 > MIN_DURATION:
                duration_stay_hours= round(duration_stay.total_seconds()/3600,2)
                create_df_entry(duration_stay_hours, berth, start_time, end_time, ship_dict[mmsi][0], eta)
                print(ship_dict[mmsi][0])

            docked=False

duration_df = duration_df.sort_values(by='Start')
duration_df = merge_entries(duration_df)
duration_df.to_csv('duration_stay/duration_stay.csv', index=False)