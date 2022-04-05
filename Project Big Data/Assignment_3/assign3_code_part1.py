"""
We truthfully declare:
- to have contributed approximately equally to this assignment [if this is not true, modify this sentence to disclose individual contributions so we can grade accordingly]
- that we have neither helped other students nor received help from other students
- that we provided references for all code that is not our own

Dragos Pop d.pop@student.vu.nl
Jimmy Gijsel c.j.l.n.gijsel@student.vu.nl
"""

"""
This template is meant as a guideline. Feel free to add new functions.
Remember to use descriptive variable names and to keep functions concise and readable.
"""
import pandas as pd
import scipy.stats
import warnings
import matplotlib.pyplot as plt
import pylab
import statsmodels.api as sm

warnings.simplefilter(action='ignore', category=FutureWarning)

"""
The main() function is called when template_week_3.py is run from the command line.
It is a good place to define the logic of the data flow (for example, reading, transforming, analyzing, visualizing).
"""
def read_data(sleepdatafile, surveydatafile):
    sleep_df = pd.read_csv(sleepdatafile, header=0, index_col=0)
    survey_df = pd.read_csv(surveydatafile, header=0, index_col=0)

    col_names = ['ID', 'group', 'delay_nights', 'delay_time', 'sleep_time']
    df1 = pd.DataFrame(columns=col_names)
    df1 = df1.set_index('ID')

    def get_group(id, df):
        return df.get_value(id, 'Condition')

    def get_delay_nights(id, df):
        result = 0
        for i in range(1, 13):
            name = 'Day ' + str(i) + ' Bedtime Difference Time (sec)'
            bedtime_difference = df.get_value(id, name)
            if bedtime_difference > 0:
                result += 1
        return result

    def get_delay_time(id, df):
        total_delayed_time = 0
        observations = 0
        for i in range(1, 13):
            name = 'Day ' + str(i) + ' Bedtime Difference Time (sec)'
            bedtime_difference = df.get_value(id, name)
            if str(bedtime_difference) != 'nan':
                observations += 1
                if bedtime_difference > 0:
                    total_delayed_time += bedtime_difference

        if observations != 0:
            return round(total_delayed_time/observations)
        else:
            return pd.NaT

    def get_sleep_time(id, df):
        total_time = 0
        observations = 0
        for i in range(1,13):
            name = 'Day ' + str(i) + ' In Bed Time (sec)'
            bedtime = df.get_value(id, name)
            if str(bedtime) != 'nan':
                observations += 1
                total_time += bedtime
        if observations != 0:
            return round(total_time / observations)
        else:
            return pd.NaT

    for i in sleep_df.index:
        df1 = df1.append(pd.Series({'group': get_group(i, sleep_df), 'delay_nights': get_delay_nights(i, sleep_df),
                                'delay_time': get_delay_time(i, sleep_df), 'sleep_time': get_sleep_time(i, sleep_df)}, name=i))

    df2 = pd.concat([df1, survey_df], axis=1, join='inner')
    df3 = df2.dropna()
    return df3


def correlate(x, y, test_type):
    if test_type == 'pearson':
        return scipy.stats.pearsonr(x, y)
    if test_type == 'kendall':
        return scipy.stats.kendalltau(x, y)

def is_normal(group, significance_level):
    p_value = scipy.stats.shapiro(group)[1]
    if p_value > significance_level:
        return True
    else:
        return False

def compare(x, y, significance_level):
    if is_normal(x, significance_level) and is_normal(y, significance_level):
        print("t-test was chosen because both groups, experimental and control, are normal distributed accordingly according to Shapiro-Wilk test")
        print(scipy.stats.ttest_ind(x,y))
    else:
        print("Wilcoxon rank-sum test was chosen because not both groups are normal distributed accordingly according to Shapiro-Wilk test")
        print(scipy.stats.ranksums(x,y))
        # print(scipy.stats.mannwhitneyu(x, y))

def regress(target, predictors):
    predictors = sm.add_constant(predictors)
    model = sm.OLS(target, predictors).fit()
    return model.summary()

"""
Tip: create one function per visualization, and call those functions from the main visualize() function.
"""

def scatter_plot(x, y, title, xlabel, ylabel):
    plt.scatter(x, y)
    plt.title(title)
    plt.xlabel(xlabel)
    plt.ylabel(ylabel)
    plt.show()

def qqnorm(data, title, ylabel):
    scipy.stats.probplot(data, dist='norm', plot=pylab)
    pylab.title(title)
    pylab.ylabel(ylabel)
    pylab.show()

def box_plot(x, y, titlex, titley, min, max):
    plt.subplot(1,2,1)
    plt.boxplot(x)
    plt.title(titlex)
    plt.ylim(min, max)
    plt.subplot(1, 2, 2)
    plt.boxplot(y)
    plt.title(titley)
    plt.ylim(min, max)
    plt.show()


def visualize(df, control, experimental):
    scatter_plot(df['bp_scale'],df['delay_time'], 'Correlation bp_scale vs delay_time', 'bp_scale', 'delay_time')
    scatter_plot(df['age'],df['delay_time'], 'Correlation age vs delay_time', 'age', 'delay_time')
    scatter_plot(df['delay_time'],df['daytime_sleepiness'], 'Correlation delay_time vs daytime_sleepiness', 'delay_time', 'daytime_sleepiness')

    qqnorm(control['sleep_time'], 'Normal QQplot of control sleep_time', 'control sleep_time quantiles')
    qqnorm(experimental['sleep_time'], 'Normal QQplot of experimental sleep_time', 'experimental sleep_time_quantiles')

    box_plot(control['delay_time'], experimental['delay_time'], "Boxplot control delay_time",
             "Boxplot experimental delay_time", -100, 6000)
    box_plot(control['sleep_time'], experimental['sleep_time'], "Boxplot control sleep_time",
             "Boxplot experimental sleep_time", 22000, 36000)
    box_plot(control['delay_nights'], experimental['delay_nights'], "Boxplot control delay_nights",
             "Boxplot experimental delay_nights", -1, 13)

def main(sleepdatafile, surveydatafile):
    df = read_data(sleepdatafile, surveydatafile)
    # with pd.option_context('display.max_rows', None, 'display.max_columns', None):
    #     print(df)
    #  For printing the dataframe

    print("_"*60,"\n1. Correlations\n")
    print("\nBed procrastination scale and the mean time delaying bedtime:\n", correlate(df['bp_scale'],df['delay_time'], 'pearson'))
    print("\nAge and the mean time delaying bedtime:\n", correlate(df['age'],df['delay_time'], 'kendall'))
    print("\nMean time spent delaying bedtime and daytime sleepiness: \n", correlate(df['delay_time'],df['daytime_sleepiness'], 'pearson'))

    control = df[df['group'] == 0]
    experimental = df[df['group'] == 1]
    significance_level = 0.05

    print("_"*60,"\n2. Significant differences\n")
    print("delay_nights:")
    print(compare(control['delay_nights'], experimental['delay_nights'], significance_level)) # W = 0.07, p-value = 0.94
    # H0: control = experimental, p-value > significance level -> fail to reject H0: no significant differences
    print("\nsleep_time:")
    print(compare(control['sleep_time'], experimental['sleep_time'], significance_level)) # T = 0.37, p-value = 0.71
    # H0: mean(control) = mean(experimental), p-value > siginficance level -> fail to reject H0: no significant differences
    print("\ndelay_time")
    print(compare(control['delay_time'], experimental['delay_time'], significance_level)) # W = 1.92, p-value = 0.053
    # H0: control = experimental, p-value > significance level -> fail to reject H0: no significant differences

    print("_"*60,"\n4. Regression model\n")
    print(regress(df['delay_time'], df[['bp_scale', 'motivation']]))

    # Step up method
    # print(regress(df['delay_time'], df[['group']]))
    # print(regress(df['delay_time'], df[['delay_nights']]))
    # print(regress(df['delay_time'], df[['sleep_time']]))
    # print(regress(df['delay_time'], df[['gender']]))
    # print(regress(df['delay_time'], df[['age']]))
    # print(regress(df['delay_time'], df[['chronotype']]))
    # print(regress(df['delay_time'], df[['bp_scale']]))
    # print(regress(df['delay_time'], df[['motivation']]))
    # print(regress(df['delay_time'], df[['daytime_sleepiness']]))
    # print(regress(df['delay_time'], df[['self_reported_effectiveness']]))
    #
    # print(regress(df['delay_time'], df[['bp_scale', 'group']]))
    # print(regress(df['delay_time'], df[['bp_scale', 'delay_nights']]))
    # print(regress(df['delay_time'], df[['bp_scale', 'sleep_time']]))
    # print(regress(df['delay_time'], df[['bp_scale', 'gender']]))
    # print(regress(df['delay_time'], df[['bp_scale', 'age']]))
    # print(regress(df['delay_time'], df[['bp_scale', 'chronotype']]))
    # print(regress(df['delay_time'], df[['bp_scale', 'motivation']]))
    # print(regress(df['delay_time'], df[['bp_scale', 'daytime_sleepiness']]))
    # print(regress(df['delay_time'], df[['bp_scale', 'self_reported_effectiveness']]))

    visualize(df, control, experimental)


if __name__ == '__main__':
    main('hue_week_3.csv', 'hue_questionnaire.csv')
