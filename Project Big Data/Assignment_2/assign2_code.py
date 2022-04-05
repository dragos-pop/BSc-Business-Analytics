import pandas as pd
import datetime
import re
import warnings
import time
import pymongo
import pytz

def read_csv_data(filenames):
    """
    In order to solve this exercise the following assumptions have been made:
     - the input is a list
     - the months of the events are recorded in Dutch lowercase
     - if a time value contains only one digit it is ignored as it could lead to discussions whether it represents
      the hours or the minutes after midnight
     - if a time entry has a value higher than 24 for hours and 60 for minutes it is not taken into account because
      it is nonsensical
      - only the last time one turned the light off in a day was taken into account for his/her bedtime

    """
    warnings.simplefilter(action='ignore', category=FutureWarning)
    start_time = time.time()

    def insert_if_new(df, idx):
        if idx not in df.index:
            df = df.append(pd.Series({'bedtime': float('nan'), 'intended_bedtime': float('nan'), 'rise_time': float('nan'),
                                      'rise_reason': float('nan'), 'fitness': float('nan'), 'adherence_importance': float('nan'),
                                      'in_experimental_group': False}, name = idx))
        return df

    def month_to_int(search_month):
        months = {1: 'januari', 2: 'februari', 3: 'maart', 4: 'april', 5: 'mei', 6: 'juni', 7: 'juli',
                  8: 'augustus', 9: 'september', 10: 'oktober', 11: 'november', 12: 'december'}
        for number, month in months.items():  #
            if month == search_month:
                return number

    def get_index(words):
        user_id = int(words[1])
        date_matches = re.search('([0-9]{2})_([a-z]+)_([0-9]{4})', words[2])
        if date_matches:
            day = int(date_matches.group(1))
            month = month_to_int(date_matches.group(2))
            year = int(date_matches.group(3))
            date = datetime.datetime(year, month, day)
            index = (date, user_id)
            return index

    def bedtime(words, index, df):
        matches = re.search('lamp_change', words[2])
        if matches:
            value = words[3]
            if value == 'OFF':
                time_matches = re.search('_([0-9]{2})_([0-9]{2})_([0-9]{2})_', words[2])
                if time_matches:
                    hour = int(time_matches.group(1))
                    min = int(time_matches.group(2))
                    sec = int(time_matches.group(3))
                    time = datetime.time(hour, min, sec)
                    if type(df.get_value(index, 'bedtime')) == float:
                        df.set_value(index, 'bedtime', time)
                    else:
                        if time > df.get_value(index, 'bedtime'):
                            df.set_value(index, 'bedtime', time)

    def intended_bedtime(words, index, df):
        matches = re.search('bedtime_tonight', words[2])
        if matches:
            time_matches = re.search('([0-9]{2})([0-9]{2})', words[3])
            if time_matches:
                hour = int(time_matches.group(1))
                min = int(time_matches.group(2))
                if hour < 24 and min < 60:
                    time = datetime.time(hour, min)
                    df.set_value(index, 'intended_bedtime', time)
            time_matches_midnight = re.search('^[0-9]{1,2}$', words[3])
            if time_matches_midnight:
                min = int(time_matches_midnight.group(0))
                time = datetime.time(0, min)
                df.set_value(index, 'intended_bedtime', time)

    def rise_time(words, index, df):
        matches = re.search('risetime', words[2])
        if matches:
            time_matches = re.search('([0-9]{1,2})([0-9]{2})', words[3])
            if time_matches:
                hour = int(time_matches.group(1))
                min = int(time_matches.group(2))
                time = datetime.time(hour, min)
                df.set_value(index, 'rise_time', time)
            time_matches_midnight = re.search('^[0-9]{1,2}$', words[3])
            if time_matches_midnight:
                min = int(time_matches_midnight.group(0))
                time = datetime.time(0, min)
                df.set_value(index, 'rise_time', time)

    def reason_fitness_importance(words, index, df):
        list = ['rise_reason', 'fitness', 'adherence_importance']
        for i in range(len(list)):
            matches = re.search(list[i], words[2])
            if matches:
                value = words[3]
                df.set_value(index, list[i], value)

    def in_experimental_group(words, index, df):
        matches = re.search('nudge_time', words[2])
        if matches:
            for i in df.index:
                if i[1] == index[1]:
                     df.set_value(i, 'in_experimental_group', True)

    col_names = ['bedtime', 'intended_bedtime', 'rise_time', 'rise_reason', 'fitness', 'adherence_importance',
                 'in_experimental_group']
    df = pd.DataFrame(columns = col_names)

    for i in range(len(filenames)):
        with open(filenames[i]) as input:
            data = input.read()
            data = data.replace("\"","")
            line = data.split(('\n'))
            for j in range(len(line)-1):
                words = line[j].split(";")
                index = get_index(words)
                if index != None:
                    df = insert_if_new(df, index)
                    bedtime(words, index, df)
                    intended_bedtime(words, index, df)
                    rise_time(words, index, df)
                    reason_fitness_importance(words, index, df)
                    in_experimental_group(words, index, df)

    # with pd.option_context('display.max_rows', None, 'display.max_columns', None):
    #     # taken from https://stackoverflow.com/questions/19124601/pretty-print-an-entire-pandas-series-dataframe
    #     print(df)
    #     for printing the dataftame

    print("\n--- %s seconds ---" % (time.time() - start_time))
    # taken from https://stackoverflow.com/questions/1557571/how-do-i-get-time-of-a-python-programs-execution
    return df


def to_mongodb(df):

    client = pymongo.MongoClient("localhost", 27017)
    db = client.BigData
    sleepdata = db.sleepdata
    sleepdata.delete_many({})

    def get_seconds(time):
        hours = time.hour
        minutes = time.minute
        seconds = time.second
        return seconds + 60 * minutes + 3600 * hours

    def time_to_date(time, index):
        tz = pytz.timezone('Europe/Amsterdam')
        if type(time) != float:
            hours = time.hour
            minutes = time.minute
            seconds = time.second
            bedtime = datetime.datetime(index[0].year, index[0].month, index[0].day, hours, minutes, seconds)
            return tz.localize(bedtime)
        else:
            return float('nan')

    x = {}
    for i in range(len(df.index)):
        index = df.index[i]
        x['_id'] = {'date': index[0], 'user': index[1]}
        bedtime = time_to_date(df.get_value(index, 'bedtime'), index)
        intended_bedtime = time_to_date(df.get_value(index, 'intended_bedtime'), index)
        rise_time = time_to_date(df.get_value(index, 'rise_time'), index)
        rise_reason = df.get_value(index, 'rise_reason')
        fitness = df.get_value(index, 'fitness')
        adherence_importance = df.get_value(index, 'adherence_importance')
        in_experimental_group = df.get_value(index, 'in_experimental_group')
        if type(bedtime) != float and type(rise_time) != float:
            sleep_duration = get_seconds(rise_time) - get_seconds(bedtime)
        else:
            sleep_duration = float('nan')
        sleepdata.insert_one({'_id': x, 'date': index[0], 'user': index[1],  'bedtime': bedtime, 'intended_bedtime': intended_bedtime, 'rise_time': rise_time,
                              'rise_reason': rise_reason, 'fitness': fitness, 'adherence_importance': adherence_importance,
                              'in_experimental_group': in_experimental_group, 'sleep_duration': sleep_duration})
    # for doc in sleepdata.find():
    #     print(doc['in_experimental_group'])
    # for printing the entries in the sleepdata collection
    return sleepdata


def read_mongodb(filter,sort):
    sleepdata = pymongo.MongoClient()['BigData']['sleepdata']
    def keep_date_only(date):
        year = date.year
        month = date.month
        day = date.day
        return datetime.date(year, month, day)

    def keep_time_only(date):
        if type(date) != float:
            hour = date.hour
            minute = date.minute
            second = date.second
            return datetime.time(hour, minute, second)
        else:
            return date

    print("\n%10s\t%8s\t%15s\t%15s\t%15s\t%7s\t%7s\t%7s\t%8s\t%15s\t" % ('date', 'user', 'bedtime', 'intended', 'risetime',
                                                                        'reason', 'fitness', 'adh', 'in_exp', 'sleep_duration'))
    for doc in sleepdata.find(filter).sort(sort, pymongo.ASCENDING):
        print("%10s\t%8s\t%15s\t%15s\t%15s\t%7s\t%7s\t%7s\t%8s\t%15s\t" %
              (str(keep_date_only(doc['date'])), str(doc['user']), str(keep_time_only(doc['bedtime'])),
               str(keep_time_only(doc['intended_bedtime'])), str(keep_time_only(doc['rise_time'])), str(doc['rise_reason']),
               str(doc['fitness']), str(doc['adherence_importance']), str(doc['in_experimental_group']), str(doc['sleep_duration'])))



if __name__ == '__main__':
    # this code block is run if you run solution.py (instead of run_solution.py)
    # it is convenient for debugging

    df = read_csv_data(["hue_upload.csv","hue_upload2.csv"])
    # to_mongodb(df)
    # read_mongodb({},'_id')





