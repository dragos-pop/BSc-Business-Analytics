"""
We truthfully declare:
- to have contributed approximately equally to this assignment [if this is not true, modify this sentence to disclose individual contributions so we can grade accordingly]
- that we have neither helped other students nor received help from other students
- that we provided references for all code that is not our own

Dragos Pop d.pop@student.vu.nl
Jimmy Gijsel c.j.l.n.gijsel@student.vu.nl
"""

# Include these lines without modifications
# Call the script as follows: ./<scriptname> <csv_filename> <mapper function> <reducer function>
# So, for example: ./template_assignment3.py hue_week_3_2017.csv mapper1 reducer1
# This will call the mapper1 function for each line of the data, sort the output, and feed the sorted output into reducer1
import sys
from io import StringIO
import traceback


# Implement these mapper and reducer functions

counter = 0

def mapper1(line):
    words = line.split(',')
    fitness = words[5]
    if fitness != '':
        fitness = float(fitness)
        if fitness > 50:
            print('fitness')

def reducer1(line):
    global counter
    if line == '':
        print(counter)
    words = line.split('\t')
    if words[0] == 'fitness':
        counter += 1


sum = {}
n = {}
users = []

def mapper2(line):
    words = line.split(',')
    user = words[1]
    fitness = words[5]
    if fitness != '':
        print('{}\t{}'.format(user, fitness))

def reducer2(line):
    global sum
    global n
    global users
    if line == '':
        for u in users:
            print(u, "\t", sum[u]/n[u])
    else:
        words = line.split('\t')
        user = words[0]
        fitness = words[1]
        if user in users:
            sum[user] += float(fitness)
            n[user] += 1
        else:
            users.append(user)
            sum[user] = float(fitness)
            n[user] = 1


if (len(sys.argv) == 4):
    data = sys.argv[1]
    mapper = sys.argv[2]
    reducer = sys.argv[3]
else:
    data = 'map_reduce_hue.csv'
    mapper = 'mapper2'
    reducer = 'reducer2'

# Include these lines without modifications

if 'old_stdout' not in globals():
    old_stdout = sys.stdout
mystdout = StringIO()
sys.stdout = mystdout

with open(data) as file:
    try:
        for index, line in enumerate(file):
            if index == 0:
                continue
            line = line.strip()
            locals()[mapper](line)
        locals()[mapper](',,,,,,,')
    except:
        sys.stdout = old_stdout
        print('Error in ' + mapper)
        print('The mapper produced the following output before the error:')
        print(mystdout.getvalue())
        traceback.print_exc()

    sys.stdout = old_stdout
    mapper_lines = mystdout.getvalue().split("\n")

    for index, line in enumerate(sorted(mapper_lines)):
        if index == 0:
            continue
        locals()[reducer](line)
    locals()[reducer]('')

mystdout.close()

