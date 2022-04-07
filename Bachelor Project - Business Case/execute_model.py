import logging
import argparse
import sys
import numpy as np
import pandas as pd
from model import model
from model import utils
from datetime import date, timedelta

logging.basicConfig(
    format='%(asctime)s %(levelname)-8s %(message)s',
    level=logging.INFO,
    datefmt='%Y-%m-%d %H:%M:%S'
)


def rolling_execution(objective, target,interval):
    if objective == 1:
        output = 'output_files/cj_{}.csv'.format(target.replace('.csv', ''))
    else:
        output = 'output_files/cmax_{}.csv'.format(target.replace('.csv', ''))

    logging.info("Performing rolling model run")
    from datetime import date, timedelta

    start_date = date(2019, 12, 3)
    end_date = date(2020, 4, 23)
    delta = timedelta(days=interval)

    results = []
    while start_date <= end_date:
        entry = {"date": start_date.strftime("%Y-%m-%d")}
        # try:
        for i in range(1, 5):
            df, remainders, df_remainders = utils.generate_df('2020-01-10', "input_files/{}".format(target), interval)
            # objective_value = create_historical_AIS(start_date.strftime("%Y-%m-%d"), df, objective)
            objective_value, ship_name_to_duration= model.solve_linear_model(df, remainders, mtype=i, objective_function=objective, start=start_date.strftime("%Y-%m-%d"))

            if objective == 1:
                entry[i] = objective_value + sum(remainders)
            if objective == 2:
                entry[i] = max(max(remainders), objective_value)

            print(entry)
            results.append(entry)
        start_date += timedelta(days=1)
        # except Exception as e:
        #     print(e)
        #     start_date += timedelta(days=1)

    results_df = pd.DataFrame(results)
    results_df.to_csv(output)


def single_execution(objective, start, interval, target):

    logging.info("Performing single timeframe model run")
    for j in range(1, 5):
        df, remainders, df_remainders = utils.generate_df('2020-01-10', 'input_files/{}'.format(target), interval)
        colors = [tuple(np.random.uniform(0, 1, size=3)) for _ in range(len(df['NAME']))]
        obj, ship_name_to_duration = model.solve_linear_model(df=df, remainders=remainders, mtype=j,
                                                              objective_function=objective, start=start)


def main():
    import argparse
    parser = argparse.ArgumentParser()
    parser.add_argument("-t", "--type", dest="type", default=False,
                        help="Possible types: normal, 25large, 50large, 75large")
    parser.add_argument("-r", "--rolling",action="store_true", dest="rolling", default=False, help="Toggle 7day rolling schedule generation")
    parser.add_argument("-s", "--start", dest="start", default=False, help="Specify start date as string ex. 2020-01-10")
    parser.add_argument("-ti", "--time_interval", dest="time_interval", default=False, help="Specify number of days to be looked ahead as int")
    parser.add_argument("-m", "--model", dest="model", default=False, help="Specify model type cj=1 or cmax=2 ")

    args = parser.parse_args()

    #TO RUN FOR BIGGER SHIPS ADJUST THE target VARIABLE to one of the other in input_files
    if args.rolling:
        rolling_execution(objective=int(args.model), target='normal_ships_model_input.csv', interval=int(args.time_interval))
    else:
        single_execution(objective=int(args.model), target= 'normal_ships_model_input.csv',start=args.start, interval=int(args.time_interval))


if __name__ == "__main__":
    main()
