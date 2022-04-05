commands = {
1 : """cat hue_upload.csv hue_upload2.csv > hue_combined.csv""",
2 : """gawk -F\; '{for (i=2; i<NF; i++) printf $i ";"; print $NF}' hue_combined.csv | tr -d \" > hue_combined_cleaned.csv""",
3 : """sort hue_combined_cleaned.csv | uniq > hue.csv""",
4 : """grep -F "lamp_change" hue.csv| wc -l""",
5 : """grep -F "adherence_importance" hue.csv | gawk -F\; '{print $3}'|sort -n| uniq""",
6 : """gawk -F\; '{print $1}' hue.csv | sort -n | uniq -c""",
7 : """grep -o "[a-z]\+\(_[a-z]\+\)*" hue.csv | sort | uniq""",
8 : """gawk -F\; '{print $2}' hue.csv | grep -o "lamp_change_[0-9]\{2\}_[a-z]\+_[0-9]\{4\}" | sort -n| uniq -c"""}

def ex9(): # for exercise 9
    number = input("Enter a number larger than 10: ")

    while (number.isdigit() == False or int(number) < 10):
        number = input("Enter a number larger than 10: ")

    def number_of_digits(n):
        if n < 10:
            return 1
        return number_of_digits(n / 10) + 1

    print("\nNumber of digits: ", number_of_digits((int(number))))
    print("Number of distinct digits: ", len(set(number)))  # taken from https://stackoverflow.com/questions/48274882/how-do-i-return-the-number-of-unique-digits-in-positive-integer

    def sums_consecutive_digits(n):
        sums = []
        for i in range(1, number_of_digits(n)):
            sums.append(n % 10 + int(n % 100 / 10))
            n = int(n / 10)
        return sums

    print("Largest sum of 2 consecutive digits: ", max(sums_consecutive_digits(int(number))))

    def prime_factors(n):  # taken from https://stackoverflow.com/questions/15347174/python-finding-prime-factors
        i = 2
        factors = []
        x = int(n)
        while i * i <= x:
            if x % i:
                i += 1
            else:
                x //= i
                factors.append(i)
        if x > 1:
            factors.append(x)
        return factors

    print("Sum of its distinct prime factors: ", sum(set(prime_factors(number))))

def ex10(filename1,filename2,outfilename):
    def read_file_line_by_line(f):
        with open(f) as input:
            data = input.read()
            line = data.split("\n")
            return line

    words1 = read_file_line_by_line(filename1)
    words2 = read_file_line_by_line(filename2)

    def words_inf1_notf2(f1, f2):
        """returns the words that are in the first list but not in the second"""
        result = []
        for i in range(len(f1)):
            count = 0
            for j in range(len(f2)):
                if words1[i] == words2[j]:
                    count += 1
            if count == 0:
                result.append(words1[i])
        return result

    result = sorted(words_inf1_notf2(words1, words2))

    out = open(outfilename, 'w')
    for i in range(len(result)):
        out.write(str(result[i]) + '\n')

def ex11(filename):
    def read_matrix(f):
        """reads each element of the matrix and stores the distance in the following format: (departure point, arrival point, distance)
        Also, it assumes that the row's elements are separated by a space like in the given example"""
        distances = []
        with open(f) as input:
            data = input.read()
            line = data.split("\n")
            for i in range(len(line)):
                for j in range(len(line)):
                    if line[i][j*2] == '-':
                        d = [i, j, float('Inf')]
                        distances.append(d)
                    else:
                        d = [i, j, line[i][j*2]]
                        distances.append(d)
        return distances

    m = read_matrix(filename)
    number_of_points = int(len(m) ** (1/2))
    available_points = []
    for i in range(number_of_points):
        available_points.append('Point ')
        available_points[i] += str(i)

    def becomes_unavailable(point):
        available_points.remove(point)

    def check_availability(point):
        """returns true if point is available"""
        for i in range(len(path)):
            if point == path[i]:
                return False
        return True

    def find_neighbors(point):
        result = []
        for i in range(number_of_points):
            if point[2] != float('Inf'):
                result.append(point[1])
        print(result)

    print(m[0], m[1], m[2])
    for i in range(number_of_points):
        find_neighbors(m[i])



    def move(point):
        neighbors = find_neighbors(point)

        for i in range(len(neighbors)):
            if check_availability(neighbors[i]):
                d = int(neighbors[i][2])
                distances.append(d)
                total_distance += d

    distances = []
    path = []
    total_distance = 0
    path.append('Point 0')
    becomes_unavailable('Point 0')

    print("\nThere are ", number_of_points, " points")
    print("Available points are: ",available_points)
    print("Path is", path)
    print("Shortest path is: ", total_distance)

def ex12(filename):
    import re

    def keep_valid_lines(f):
        result = []
        with open(f) as input:
            data = input.read()
            line = data.split("\n")
            print("Valid coordinates:")
            for i in range(len(line)):
                matches = re.search('^\([1-9],[1-9]\)\t[w,W,b,B]', line[i])
                if matches:
                    result.append(matches.group(0))
                    print(matches.group(0))
        return result

    def read_valid_lines(valid):
        coordinates = []
        col = []
        for i in range(len(valid_lines)):
            n = re.search("\d,\d", valid_lines[i])
            m = re.search("[a-z]", valid_lines[i])
            if n:
                coordinates.append(n.group(0))
            if m:
                col.append(m.group())
        return (coordinates, col)

    def check_suitable_position(coordinate):
        if abs(coordinate[0] - coordinate[1]) % 2 == 0:
            True
        else:
            False

    def represent_board():
        top = " _______________________________________ \n"
        middle = "|   |   |   |   |   |   |   |   |   |   |\n"
        bottom = "|___|___|___|___|___|___|___|___|___|___|\n"

        board = top + 10 * (2 * middle + bottom)
        print(board)

        for i in range(len(col)):
            if check_suitable_position(coordinates[i]):
                x = (coordinates[i][0] - 12) * 3 + 2
                y = (coordinates[i][1] - 1) * 4 + 2
                board.replace(board[x][y], col)
        print(board)

    valid_lines = keep_valid_lines(filename)
    (coordinates, col) = read_valid_lines(valid_lines)
    represent_board()
