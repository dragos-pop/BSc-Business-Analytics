import pandas as pd
import numpy as np
import math 
import datetime
import time

import requests
from bs4 import BeautifulSoup

import matplotlib.pyplot as plt
import seaborn as sns

from sklearn.model_selection import train_test_split
from sklearn.metrics import mean_squared_error
from sklearn.model_selection import cross_val_score

from sklearn.preprocessing import MinMaxScaler
from sklearn.preprocessing import StandardScaler

from keras.layers import Dense, Activation
from keras.models import Sequential

df_train = pd.read_csv('recommender/final.csv')

def get_GT(mmsi):
    url = 'https://www.vesselfinder.com/vessels?name=' + str(mmsi)
    
    page = requests.get(url, headers={'User-Agent': 'Safari/13.1.1'})
    soup = BeautifulSoup(page.content, 'html.parser')
    tables = soup.find_all("table")
    
    try:
        table = tables[0]
        tab_data = [[cell.text for cell in row.find_all(["th","td"])]
                           for row in table.find_all("tr")]

        d = pd.DataFrame(tab_data)

        element = d[3][1]

        try:
            return float(element)
        except ValueError:
            return np.nan
    except IndexError:
            return np.nan

def time_morning(x):
    start = datetime.time(4, 0, 1)
    end = datetime.time(12, 0, 0)
    return start <= x <= end

def time_afternoon(x):
    start = datetime.time(12, 0, 1)
    end = datetime.time(17, 0, 0)
    return start <= x <= end

def time_evening(x):
    start = datetime.time(17, 0, 1)
    end = datetime.time(23, 59, 59)
    return start <= x <= end

def time_night(x):
    start = datetime.time(0, 0, 0)
    end = datetime.time(4, 0, 0)
    return start <= x <= end

def  preprocess_data(df):
    df = df[['MMSI','NAME',	'IMO',	'Berth','Start','End','Duration','Type','A','B','C','D','Draught']]

    df['MMSI_MID'] = df['MMSI'].astype(str).str[:3]                   # country code
    df['MMSI_MID_continent'] = df['MMSI_MID'].astype(str).str[:1] 
    df['MMSI_Inmarsat'] = df['MMSI'].astype(str).str[-3:]

    df['MMSI_Inmarsat_BCM'] = (df['MMSI_Inmarsat'].astype(str) == '000').astype(int).astype(str)
    df['MMSI_Inmarsat_C'] = ((df['MMSI_Inmarsat'].astype(str).str[-1:] == '0').astype(int) & (df['MMSI_Inmarsat_BCM'] == 0)).astype(int).astype(str)
    df['MMSI_Inmarsat_A'] = (df['MMSI_Inmarsat_C'] + df['MMSI_Inmarsat_BCM'] != 1).astype(int).astype(str)
    df = df.drop(['MMSI_Inmarsat'], axis=1)

    df['Start'] = pd.to_datetime(df['Start'])
    df['End'] = pd.to_datetime(df['End'])
    
    df['Start_day'] = df['Start'].dt.dayofweek.astype(str)
    df['Start_time'] = [datetime.datetime.time(d) for d in df['Start']]

    df['Start_morning'] = df['Start_time'].apply(time_morning).astype(int).astype(str)
    df['Start_afternoon'] = df['Start_time'].apply(time_afternoon).astype(int).astype(str)
    df['Start_evening'] = df['Start_time'].apply(time_evening).astype(int).astype(str)
    df['Start_night'] = df['Start_time'].apply(time_night).astype(int).astype(str)
    df = df.drop(['Start_time'], axis=1)

    df['Gross Tonnage'] = df['MMSI'].apply(get_GT)

    df['X'] = df['End'] - df['Start']
    df = df.drop(['X'], axis=1)

    df['Type_str'] = df['Type'].astype(str)

    df = df.drop(['Berth'], axis=1)
    df = df.drop(['IMO'], axis=1)
    df = df.drop(['NAME'], axis=1)
    df = df.drop(['End'], axis=1)
    df = df.drop(['Gross Tonnage'], axis=1)
    df = df.drop(['Start'], axis=1)
    
    df_dummy = pd.get_dummies(df)
    df_dummy.drop('Duration',axis=1,inplace=True)
    print('DF DUMMY SHAPE:',df_dummy.shape)
    return df_dummy


def build_NN(X_for_prediction):
    # takes as input the name of the features on which the model is trained on, the training data including both
    # the features and the target variable and the data (containing only the features) for which the prediction
    # is wanted
    prediction_x_df = preprocess_data(X_for_prediction)

    features = prediction_x_df.columns

    target = 'Duration'
    
    y_train = df_train['Duration']
    X_train = df_train[features]
    print('shape X_train:', X_train.shape)
    print('Prediction_x_df shape:',prediction_x_df.shape)
    
    # Feature Scaling
    sc = StandardScaler()
    X_train = sc.fit_transform(X_train)

    # Initialising the ANN
    model = Sequential()

    # Adding the input layer and the first-third hidden layer
    model.add(Dense(32, activation = 'relu', input_dim = len(features)))
    model.add(Dense(units = 32, activation = 'relu'))
    model.add(Dense(units = 32, activation = 'relu'))

    # Adding the output layer
    model.add(Dense(units = 1))

    # Compiling the ANN
    model.compile(optimizer = 'adam', loss = 'mean_squared_error')

    # Fitting the ANN to the Training set
    model.fit(X_train, y_train, batch_size = 10, epochs = 100);
    
    return model.predict(sc.transform(prediction_x_df))