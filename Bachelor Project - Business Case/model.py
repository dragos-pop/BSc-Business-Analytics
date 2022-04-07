from pulp import *
import pulp
import pandas as pd

from datetime import datetime
import numpy as np

BUFFER = 2.0
M = 10000

def write_output(prob, mtype):
    f = open('output_files/input{}.txt'.format(mtype), 'w+')

    for v in prob.variables():
        print(v.name, "=", v.varValue, file=f)

    f.close()

def normalize_column(data_frame, colname, start):
    data_frame.reset_index(inplace=True)

    data_frame[colname] = pd.to_datetime(data_frame[colname], format='%d %b %Y %H:%M:%S:%f')
    data_frame.sort_values(by=colname, ignore_index=True, inplace=True)
    start_datetime = datetime.strptime(start, '%Y-%m-%d')

    for i in range(len(data_frame[colname])):
        diff = data_frame.loc[i, colname] - start_datetime
        data_frame.loc[i, colname] = round(diff.total_seconds() / 3600, 2)

    return list(data_frame[colname])


def solve_linear_model(df,remainders, mtype, objective_function, start):
    ''' Takes as input a dataframe with the ships that need to be scheduled and one of the following modeltypes (mtypes):

    1 : FCFS (ships can be scheduled no earlier than their ETA)
    2 : No relaxation (ships can be scheduled no earlier than their ETA)
    3 : 48-hours relaxation (ships can be scheduled up to 48hrs earlier than their ETA)
    4 : Complete arrival time relaxation 

    and one of the following objective functions as objective_function:
    1 : Minimise sum Cj
    2 : Minimise max Cj

    '''

    ships = [str(i) for i in range(len(df['MMSI']))]
    duration = list(round(df['Duration'], 0) + BUFFER)
    weight = list(round(df['Duration'], 0))
    arrival = normalize_column(df, colname='NOR Tendered', start=start)
    width = list(df['Width'])
    berths = ['AK 1W1', 'AK 1W2', 'AK 2E2', 'AK 1E1']

    ship_name_to_duration = dict(zip(ships, duration))

    prob = LpProblem("Ship_Berthing_Problem", LpMinimize)

    # Decision Variables

    
    s = LpVariable.dicts("service_time", ships, lowBound=0, upBound=None, cat='Integer')

    #(13)
    x = LpVariable.dicts("if_ship_in_group_berth", (str((j, i)) for j in ships for i in berths), lowBound=0, upBound=1,
                         cat='Binary')

    #(14)
    I = LpVariable.dicts('if_two_ships-berthed', ((i, (j, k)) for k in ships for j in ships for i in berths),
                         lowBound=0, upBound=1, cat='Binary')
    
    #  (6)
    if mtype == 3:
        relax = LpVariable.dicts('arrival_hours_earlier', ships, lowBound=0, upBound=48, cat='Integer')

    # (1) Objective Function
    if objective_function == 1:
        prob += lpSum(s[ships[j]] + duration[j] for j in range(len(ships)))

    #(2)
    elif objective_function == 2:
        CMax = LpVariable('max_completion_time', upBound=None, cat='Integer')
        prob += CMax

        #(7)
        for j in range(len(ships)):  # Find maximum completion time
            prob += CMax >= s[ships[j]] + duration[j], "Max Completion Time: {}".format(ships[j])

    # CONSTRAINTS

    # (5) FCFS
    if mtype == 1:
        for j in range(len(ships)):
            for j_prime in range(len(ships)):
                if arrival[j] <= arrival[j_prime]:
                    prob += s[ships[j]] <= s[ships[j_prime]]

    # (8) Occupation in the harbour
    for i in range(len(berths)):
        for j in range(len(ships)):
            prob += s[ships[j]] >= (remainders[i] + BUFFER) * x["('{}', '{}')".format(ships[j], berths[i])]

    # (3) One berth per ship
    for j in range(len(ships)):
        prob += lpSum([x["('{}', '{}')".format(ships[j], i)] for i in berths]) == 1

    # (4) Start service after arrival
    if mtype == 1 or mtype == 2:
        for i in range(len(ships)):
            prob += s[ships[i]] >= arrival[i], "Service > Arrival for: {}".format(ships[i])
    elif mtype == 3:
        for j in range(len(ships)):
            prob += s[ships[j]] >= arrival[j] - relax[ships[j]]

    # (9)
    for i in berths:
        for j in range(len(ships)):
            for j_prime in range(len(ships)):
                if j != j_prime:
                    prob += s[ships[j_prime]] >= s[ships[j]] + duration[j] - M * (
                                1 - I[i, (ships[j], ships[j_prime])]), "{}-{}-{}".format(i, ships[j], ships[j_prime])

    # (10)
    for i in berths:
        for j in range(len(ships)):
            for j_prime in range(len(ships)):
                if j < j_prime:
                    prob += I[i, (ships[j], ships[j_prime])] + I[i, (ships[j_prime], ships[j])] <= (1 / 2) * (
                                x["('{}', '{}')".format(ships[j], i)] + x["('{}', '{}')".format(ships[j_prime], i)])

    # (11)
    for i in berths:
        for j in range(len(ships)):
            for j_prime in range(len(ships)):
                if j < j_prime:
                    prob += I[i, (ships[j], ships[j_prime])] + I[i, (ships[j_prime], ships[j])] >= x[
                        "('{}', '{}')".format(ships[j], i)] + x["('{}', '{}')".format(ships[j_prime], i)] - 1

    # (12)
    for j in range(len(ships)):
        for j_prime in range(len(ships)):
            for j_prime_prime in range(len(ships)):
                prob += width[j] * x["('{}', '{}')".format(ships[j], berths[0])] + width[j_prime] * x[
                    "('{}', '{}')".format(ships[j_prime], berths[1])] + width[j_prime_prime] * x[
                            "('{}', '{}')".format(ships[j_prime_prime], berths[2])] <= 106

    print('I will now try to solve the problem, please wait a moment...')
    prob.solve(pulp.PULP_CBC_CMD(maxSeconds=120))
    print("Status:", LpStatus[prob.status], 'with value', value(prob.objective))

    write_output(prob,mtype)
    return value(prob.objective), ship_name_to_duration


