import pandas as pd
import re
import warnings
import scipy.stats
import matplotlib.pyplot as plt
import numpy as np
import statsmodels.api as sm

warnings.simplefilter(action='ignore', category=FutureWarning)

def read_data(file):
    df = pd.read_csv(file, header=0, index_col=0, low_memory=False)
    return df

df = read_data('DC_Properties.csv')
# print(df.info())
del df['LIVING_GBA']
del df['X']
del df['Y']

# Evolution of price over time
def count_sales_year(df):
    result = {}
    for i in df.index:
        date = df.get_value(i, 'SALEDATE')
        if type(date) == str:
            match = re.search('([0-9]{4})-([0-9]{2})-[0-9]{2}', date)
            if match:
                year = int(match.group(1))
                if year in result:
                    result[year] += 1
                else:
                    result[year] = 1
    return result

def price_sales_year(df):
    result = {}
    for i in df.index:
        date = df.get_value(i, 'SALEDATE')
        price = df.get_value(i, 'PRICE')
        if type(date) == str and np.isnan(price) == False:
            match = re.search('([0-9]{4})-([0-9]{2})-[0-9]{2}', date)
            if match:
                year = int(match.group(1))
                if year in result:
                    result[year] += price
                else:
                    result[year] = price
    return result

def square_foot_sales_year(df):
    result = {}
    for i in df.index:
        date = df.get_value(i, 'SALEDATE')
        gba = df.get_value(i, 'GBA')
        if type(date) == str and np.isnan(gba) == False:
            match = re.search('([0-9]{4})-([0-9]{2})-[0-9]{2}', date)
            if match:
                year = int(match.group(1))
                if year in result:
                    result[year] += gba
                else:
                    result[year] = gba
    return result

def commonvalues(dict1, dict2):
    result = []
    for i in dict1.keys():
        if i in dict2.keys():
            result.append(i)
    result.sort()
    return result

def average_sales_year(count, price):
    result = {}
    for i in commonvalues(count, price):
        result[i] = price[i] / count[i]
    return result

def line_plot(dict, title, xlabel, ylabel):
    x = list(dict.keys())
    y = list(dict.values())
    plt.plot(x, y, '-')
    plt.title(title)
    plt.xlabel(xlabel)
    plt.ylabel(ylabel)
    plt.xlim(1981, 2019)
    plt.show()


average_year = average_sales_year(count_sales_year(df), price_sales_year(df))
line_plot(average_year, "Evolution of average price", "Years", "Average price ($)")   # average price with outlier

print("-"*90, "\nMost expensive houses in the dataset")
print(df['PRICE'].max())
df1 = df[df.PRICE != df['PRICE'].max()]
print(df1['PRICE'].max())
df2 = df1[df1.PRICE != df1['PRICE'].max()]
print(df2['PRICE'].max())
df3 = df2[df2.PRICE != df2['PRICE'].max()]
print(df3['PRICE'].max())

average_year = average_sales_year(count_sales_year(df3), price_sales_year(df3)) # average price
line_plot(average_year, "Evolution of average price", "Years", "Average price ($)")

average_square_foot_year = average_sales_year(square_foot_sales_year(df3), price_sales_year(df3)) # average price per square foot
line_plot(average_square_foot_year, "Evolution of average price of square foot", "Years", "Average price per square foot ($)")



# Factors that have the largest influence on price
def correlate(df, x, y):
    df1 = df[[x, y]].dropna()
    factor1 = df1[x]
    factor2 = df1[y]
    print(scipy.stats.kendalltau(factor1, factor2))

# correlate(df3, 'PRICE', 'GBA') # 0.34, p-value = 0           ------------
# correlate(df3, 'PRICE', 'HEAT') # 0.014, p-value = 0.00001
# correlate(df3, 'PRICE', 'AC') # 0.18, p-value = 0
# correlate(df3, 'PRICE', 'ROOMS') # 0.22, p-value = 0
# correlate(df3, 'PRICE', 'QUALIFIED') # 0.14, p-value = 0
# correlate(df3, 'PRICE', 'STYLE') # 0.23, p-value = 0
# correlate(df3, 'PRICE', 'STRUCT') # 0.06, p-value = 0.000001
# correlate(df3, 'PRICE', 'GRADE') # 0.28, p-value = 0       -------------
# correlate(df3, 'PRICE', 'CNDTN') # 0.32, p-value = 0         ---------------
# correlate(df3, 'PRICE', "SALEDATE") # 0.30, p-value = 0      --------------
# correlate(df3, 'PRICE', 'EXTWALL') # 0.0003, p-value = 0.92
# correlate(df3, 'PRICE', 'ROOF') # 0.16, p-value = 0
# correlate(df3, 'PRICE', 'INTWALL') # 0.015, p-value = 0.00003
# correlate(df3, 'PRICE', 'LANDAREA') # 0.08, p-value = 0
# correlate(df3, 'PRICE', 'ZIPCODE') # 0.17, p-value = 0
# correlate(df3, 'PRICE', 'QUADRANT') # 0.03, p-value = 0.0000001
# correlate(df3, 'PRICE', 'WARD') # 0.22, p-value = 0
# correlate(df3, 'PRICE', 'ASSESSMENT_NBHD') # 0.03, p-value = 0.000000001

def scatter_plot(x, y, title, xlabel, ylabel):
    plt.scatter(x, y)
    plt.title(title)
    plt.xlabel(xlabel)
    plt.ylabel(ylabel)
    plt.show()

def regress(target, predictors):
    df1 = pd.concat([target, predictors], axis=1, join='inner')
    df2 = df1.dropna()
    target1 = df2.iloc[:, 0]
    predictors1 = df2.iloc[:, 1:]
    predictors1 = sm.add_constant(predictors1)
    model = sm.OLS(target1, predictors1).fit()
    print(model.summary())

# Step up method:

# regress(df3['PRICE'], df3['BATHRM']) # 0
# regress(df3['PRICE'], df3['HF_BATHRM']) # 0
# regress(df3['PRICE'], df3['ROOMS']) # 0.001
# regress(df3['PRICE'], df3['BEDRM']) # 0.002
# regress(df3['PRICE'], df3['AYB']) # 0.003
# regress(df3['PRICE'], df3['YR_RMDL']) # 0.001
# regress(df3['PRICE'], df3['EYB']) # 0.002
# regress(df3['PRICE'], df3['GBA']) # 0.361   ------------------
# regress(df3['PRICE'], df3['BLDG_NUM']) # 0
# regress(df3['PRICE'], df3['KITCHENS']) # 0.002
# regress(df3['PRICE'], df3['FIREPLACES']) # 0.001
# regress(df3['PRICE'], df3['LANDAREA']) # 0
# regress(df3['PRICE'], df3['CENSUS_TRACT']) # 0.005

# regress(df3['PRICE'], df3[['GBA', 'BATHRM']]) # 0.374
# regress(df3['PRICE'], df3[['GBA', 'HF_BATHRM']]) # 0.373
# regress(df3['PRICE'], df3[['GBA', 'ROOMS']]) # 0.369
# regress(df3['PRICE'], df3[['GBA', 'BEDRM']]) # 0.0.362
# regress(df3['PRICE'], df3[['GBA', 'AYB']]) # 0.369
# regress(df3['PRICE'], df3[['GBA', 'YR_RMDL']]) # 0.411   -------------
# regress(df3['PRICE'], df3[['GBA', 'EYB']]) # 0.383
# regress(df3['PRICE'], df3[['GBA', 'BLDG_NUM']]) # 0.364
# regress(df3['PRICE'], df3[['GBA', 'KITCHENS']]) # 0.380
# regress(df3['PRICE'], df3[['GBA', 'FIREPLACES']]) # 0.408
# regress(df3['PRICE'], df3[['GBA', 'LANDAREA']]) # 0.367
# regress(df3['PRICE'], df3[['GBA', 'CENSUS_TRACT']]) # 0.391

# regress(df3['PRICE'], df3[['GBA', 'YR_RMDL', 'BATHRM']]) # 0.420
# regress(df3['PRICE'], df3[['GBA', 'YR_RMDL', 'HF_BATHRM']]) # 0.423
# regress(df3['PRICE'], df3[['GBA', 'YR_RMDL', 'ROOMS']]) # 0.417
# regress(df3['PRICE'], df3[['GBA', 'YR_RMDL', 'BEDRM']]) # 0.413
# regress(df3['PRICE'], df3[['GBA', 'YR_RMDL', 'AYB']]) # 0.426
# regress(df3['PRICE'], df3[['GBA', 'YR_RMDL', 'EYB']]) # 0.482 --------------
# regress(df3['PRICE'], df3[['GBA', 'YR_RMDL', 'BLDG_NUM']]) # 0.414
# regress(df3['PRICE'], df3[['GBA', 'YR_RMDL', 'KITCHENS']]) # 0.426
# regress(df3['PRICE'], df3[['GBA', 'YR_RMDL', 'FIREPLACES']]) # 0.460
# regress(df3['PRICE'], df3[['GBA', 'YR_RMDL', 'LANDAREA']]) # 0.417
# regress(df3['PRICE'], df3[['GBA', 'YR_RMDL', 'CENSUS_TRACT']]) # 0.439

# regress(df3['PRICE'], df3[['GBA', 'YR_RMDL', 'EYB', 'BATHRM']]) # 0.485
# regress(df3['PRICE'], df3[['GBA', 'YR_RMDL', 'EYB', 'HF_BATHRM']]) # 0.486
# regress(df3['PRICE'], df3[['GBA', 'YR_RMDL', 'EYB', 'ROOMS']]) # 0.486
# regress(df3['PRICE'], df3[['GBA', 'YR_RMDL', 'EYB', 'BEDRM']]) # 0.484
# regress(df3['PRICE'], df3[['GBA', 'YR_RMDL', 'EYB', 'AYB']]) # 0.515 -----------
# regress(df3['PRICE'], df3[['GBA', 'YR_RMDL', 'EYB', 'BLDG_NUM']]) # 0.485
# regress(df3['PRICE'], df3[['GBA', 'YR_RMDL', 'EYB', 'KITCHENS']]) # 0.489
# regress(df3['PRICE'], df3[['GBA', 'YR_RMDL', 'EYB', 'FIREPLACES']]) # 0.411
# regress(df3['PRICE'], df3[['GBA', 'YR_RMDL', 'EYB', 'LANDAREA']]) # 0.488
# regress(df3['PRICE'], df3[['GBA', 'YR_RMDL', 'EYB', 'CENSUS_TRACT']]) # 0.494

# Best time of the year to buy or sell

def count_sales_month(df):
    result = {}
    for i in df.index:
        date = df.get_value(i, 'SALEDATE')
        if type(date) == str:
            match = re.search('([0-9]{4})-([0-9]{2})-[0-9]{2}', date)
            if match:
                month = int(match.group(2))
                if month in result:
                    result[month] += 1
                else:
                    result[month] = 1
    return result

def price_sales_month(df):
    result = {}
    for i in df.index:
        date = df.get_value(i, 'SALEDATE')
        price = df.get_value(i, 'PRICE')
        if type(date) == str and np.isnan(price) == False:
            match = re.search('([0-9]{4})-([0-9]{2})-[0-9]{2}', date)
            if match:
                month = int(match.group(2))
                if month in result:
                    result[month] += price
                else:
                    result[month] = price
    return result

def average_sales_month(price, count):
    result = {}
    for i in range(12):
        result[i+1] = price[i+1]/ count[i+1]
    return result

def histogram(dict, title, xlabel, ylabel):
    plt.bar(dict.keys(), dict.values())
    plt.title(title)
    plt.xlabel(xlabel)
    plt.ylabel(ylabel)
    plt.show()

average_month = average_sales_month(price_sales_month(df3), count_sales_month(df3)) # price
histogram(average_month, "Average price per month", 'Month', "Average price ($)")

total_sales_month = count_sales_month(df3)
histogram(total_sales_month, "Total sales per month", "Month", "Number of sales")

def count_sales_month_last5years(df):
    result = {}
    for i in df.index:
        date = df.get_value(i, 'SALEDATE')
        if type(date) == str:
            match = re.search('([0-9]{4})-([0-9]{2})-[0-9]{2}', date)
            if match:
                year = int(match.group(1))
                month = int(match.group(2))
                if year > 2013:
                    if month in result:
                        result[month] += 1
                    else:
                        result[month] = 1
    return result

def price_sales_month_last5years(df):
    result = {}
    for i in df.index:
        date = df.get_value(i, 'SALEDATE')
        price = df.get_value(i, 'PRICE')
        if type(date) == str and np.isnan(price) == False:
            match = re.search('([0-9]{4})-([0-9]{2})-[0-9]{2}', date)
            if match:
                year = int(match.group(1))
                if year > 2013:
                    month = int(match.group(2))
                    if month in result:
                        result[month] += price
                    else:
                        result[month] = price
    return result

average_month_last5years = average_sales_month(price_sales_month_last5years(df3), count_sales_month_last5years(df3))
histogram(average_month_last5years, "Average price per month (last 5 years)", 'Month', "Average price ($)")

# Significant differences in the medians of the 4 conditions in terms of price

excellent = df3[df3['CNDTN'] == "Excellent"]
very_good = df3[df3['CNDTN'] == "Very Good"]
good = df3[df3['CNDTN'] == "Good"]
average = df3[df3['CNDTN'] == "Average"]

priceexcellent = excellent['PRICE'].dropna()
priceverygood = very_good['PRICE'].dropna()
pricegood = good['PRICE'].dropna()
priceaverage = average['PRICE'].dropna()

def mean_medians(df):
    # mean and median for every condition
    meanexcellent = excellent['PRICE'].mean()       #mean = 1247995.20
    meanverygood = very_good['PRICE'].mean()        #mean = 945585.00
    meangood = good['PRICE'].mean()                 #mean = 655149.30
    meanaverage = average['PRICE'].mean()           #mean = 375583.61
    medianexcellent = excellent['PRICE'].median()   #median = 763744.0
    medianverygood = very_good['PRICE'].median()    #median = 677347.0
    mediangood = good['PRICE'].median()             #median = 565000.0
    medianaverage = average['PRICE'].median()       #median = 284500.0
    print(medianexcellent)
    print(medianverygood)
    print(mediangood)
    print(medianaverage)
    print(meanexcellent)
    print(meanverygood)
    print(meangood)
    print(meanaverage)

def box_plot(data, min, max, title, ylabel):
    plt.boxplot(data, notch=True, patch_artist=True, labels=['Excellent', 'Very good', 'Good', 'Average'])
    axis = plt.gca()
    axis.set_ylim([min, max])
    plt.title(title)
    plt.xlabel("Condition")
    plt.ylabel(ylabel)
    plt.show()

def compare(x, y, test):
    if (test == "kruskall"):
        print(scipy.stats.kruskal(x,y))

prices = [priceexcellent, priceverygood, pricegood, priceaverage]
box_plot(prices, 0, 20000000, "Conditions differences in terms of price", "Price (mln $)")
box_plot(prices, 0, 1500000, "Conditions differences in terms of price (zoom)", "Price ($)")

print("-"*90, "\nSignificant differences in the medians of the 4 conditions in terms of price\n")
compare(priceexcellent, priceverygood, "kruskall")     #Kruskall-Wallis pvalue = 0.22              ---> No significant difference
compare(priceexcellent, pricegood, "kruskall")         #Kruskall-Wallis pvalue = 2.34*10^-27       ---> Significant difference
compare(priceexcellent, priceaverage, "kruskall")      #Kruskall-Wallis pvalue = 7.835*10^-180     ---> Significant difference
compare(priceverygood, pricegood, "kruskall")          #Kruskall-Willis pvalue = 4.87 * 10^-170    ---> Significant difference
compare(priceverygood, priceaverage, "kruskall")       #Kruskall-Willis pvalue = 0                 ---> Significant difference
compare(pricegood, priceaverage, "kruskall")           #Kruskall-Willis pvalue = 0                 ---> Significant difference

# Style that sells the most
# print(set(df3['STYLE']))
style1 = df3[df3['STYLE'] == '1 Story']
style2 = df3[df3['STYLE'] == '2 Story']
style3 = df3[df3['STYLE'] == '3 Story']
style4 = df3[df3['STYLE'] == '4 Story']
style5 = df3[df3['STYLE'] == 'Bi-Level']
style6 = df3[df3['STYLE'] == '1.5 Story Fin']
style7 = df3[df3['STYLE'] == 'Split Foyer']
style8 = df3[df3['STYLE'] == 'Outbuildings']
style9 = df3[df3['STYLE'] == '4.5 Story Fin']
style10 = df3[df3['STYLE'] == '3.5 Story Fin']
style11 = df3[df3['STYLE'] == 'Default']
style12 = df3[df3['STYLE'] == 'Split Level']
style13 = df3[df3['STYLE'] == '2.5 Story Fin']


def count_style(df):
    sale_num = df['SALE_NUM']
    return sale_num.sum()

style1_size = count_style(style1)
style2_size = count_style(style2)
style3_size = count_style(style3)
style4_size = count_style(style4)
style5_size = count_style(style5)
style6_size = count_style(style6)
style7_size = count_style(style7)
style8_size = count_style(style8)
style9_size = count_style(style9)
style10_size = count_style(style10)
style11_size = count_style(style11)
style12_size = count_style(style12)
style13_size = count_style(style13)


def bar_chart(x, y, title, xlabel, ylabel):
    plt.bar(x, y)
    plt.title(title)
    plt.xlabel(xlabel)
    plt.ylabel(ylabel)
    plt.show()

labels = ['1 St', '2 St', '3 St', '4 St', 'Bi-lev', 'Bi-1.5', 'Sp foy', '2.5 St', '4.5 St', '3.5 St', 'Def','Outb' , 'Sp lev']
sizes = [style1_size, style2_size, style3_size, style4_size, style5_size, style6_size, style7_size, style13_size, style9_size, style10_size,
         style11_size, style8_size, style12_size]
bar_chart(labels, sizes, 'Sales of the 13 finished styles', 'Finished styles', 'Number of sales')


def count_style_last5year(df, s):
    result = 0
    for i in df.index:
        date = df.get_value(i, 'SALEDATE')
        style = df.get_value(i, 'STYLE')
        if style == s:
            if type(date) == str:
                match = re.search('([0-9]{4})-([0-9]{2})-[0-9]{2}', date)
                if match:
                    year = int(match.group(1))
                    if year > 2013:
                        result += 1
    return result


style1_last5 = count_style_last5year(df3, '1 Story')
style2_last5 = count_style_last5year(df3, '2 Story')
style3_last5 = count_style_last5year(df3, '3 Story')
style4_last5 = count_style_last5year(df3, '4 Story')
style5_last5 = count_style_last5year(df3, 'Bi-Level')
style6_last5 = count_style_last5year(df3, 'Bi-1.5 Story Fin')
style7_last5 = count_style_last5year(df3, 'Split Foyer')
style8_last5 = count_style_last5year(df3, 'OutBuildings')
style9_last5 = count_style_last5year(df3, '4.5 Story Fin')
style10_last5 = count_style_last5year(df3, '3.5 Story Fin')
style11_last5 = count_style_last5year(df3, 'Default')
style12_last5 = count_style_last5year(df3, 'Split Level')
style13_last5 = count_style_last5year(df3, '2.5 Story Fin')

sizes_last5 = [style1_last5, style2_last5, style3_last5, style4_last5, style5_last5, style6_last5, style7_last5, style8_last5,
               style9_last5, style10_last5, style11_last5, style12_last5, style13_last5]

bar_chart(labels, sizes_last5, 'Sales of the 13 finished styles since 2014', 'Finished styles', 'Number of sales')
