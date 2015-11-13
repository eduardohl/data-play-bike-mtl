# coding: utf-8
import pandas as pd
import matplotlib.pyplot as plt
from datetime import datetime

# Setting Chart config
plt.rcParams["figure.figsize"] = (20,5)

# Loading CSV data
df2009 = pd.read_csv('data/2009.csv').dropna(how='all', axis=1)
df2010 = pd.read_csv('data/2010.csv').dropna(how='all', axis=1)
df2011 = pd.read_csv('data/2011.csv').dropna(how='all', axis=1)
df2012 = pd.read_csv('data/2012.csv').dropna(how='all', axis=1)
df2013 = pd.read_csv('data/2013.csv').dropna(how='all', axis=1)

# Adding indexation by datetime
df2009['Date'] = pd.to_datetime(df2009['Date'], format="%d %m %Y")
df2010['Date'] = pd.to_datetime(df2010['Date'], format="%d %m %Y")
df2011['Date'] = pd.to_datetime(df2011['Date'], format="%d %m %Y")
df2012['Date'] = pd.to_datetime(df2012['Date'], format="%d/%m/%Y")
df2013['Date'] = pd.to_datetime(df2013['Date'], format="%d/%m/%Y")

# Concatenating all the loaded data in a single DF
full = pd.concat([df2009,df2010,df2011,df2012,df2013])
full = full.set_index('Date')
full = full.fillna(0)

# Cleaning up whitespaces in the dataset and casting entries to float type where needed
full['Berri'] = full['Berri'].map(lambda x : float(str(x).replace(" ", "")))
full['Brebeuf'] = full['Brebeuf'].map(lambda x : float(str(x).replace(" ", "")))
full['Cote-Sainte-Catherine'] = full['Cote-Sainte-Catherine'].map(lambda x : float(str(x).replace(" ", "")))
full['Maisonneuve 1'] = full['Maisonneuve 1'].map(lambda x : float(str(x).replace(" ", "")))
full['Maisonneuve 2'] = full['Maisonneuve 2'].map(lambda x : float(str(x).replace(" ", "")))
full['Pierre-Dupuy'] = full['Pierre-Dupuy'].map(lambda x : float(str(x).replace(" ", "")))
full['Rachel'] = full['Rachel'].map(lambda x : float(str(x).replace(" ", "")))
full['Saint-Urbain'] = full['Saint-Urbain'].map(lambda x : float(str(x).replace(" ", "")))
full['du Parc'] = full['du Parc'].map(lambda x : float(str(x).replace(" ", "")))

# Function that plots each station agg by year
def plotStation(source, station_name):
    plt.clf()
    station = source[station_name].to_frame()
    station = station.resample('MS', how='sum', closed='left', kind='timestamp')
    for idx, (key, grp) in enumerate(station.groupby(station.index.year, axis=0)):
        plt.plot(grp, label=key)
    plt.xticks(range(12), ['Jan','Feb','Mar','Apr','Mai','Jun','Jul','Aug','Sep','Oct','Nov','Dec'])
    plt.legend(loc='best')  
    plt.grid()
    plt.savefig('output/' + station_name + '.png', dpi=300, bbox_inches='tight')

# Plot each station
station_names=['Berri','Brebeuf','Cote-Sainte-Catherine','Maisonneuve 1','Maisonneuve 2','du Parc','Pierre-Dupuy','Rachel','Saint-Urbain','Totem-Laurier']
for st in station_names:
    plotStation(full,st)

#Register Totals Sum (https://dataplaysite.wordpress.com/2015/11/09/3/)
totals_sum = full.groupby(full.index.year).sum()
totals_sum.index.name='Year'
totals_sum = totals_sum.transpose()
totals_sum['Total'] = totals_sum.sum(axis=1)
totals_sum = totals_sum.sort(['Total'],ascending=[0])
totals_sum.to_csv('output/sums.csv')

#Generating correlations by year(https://dataplaysite.wordpress.com/2015/11/10/bike-paths-correlation/)
for year in range(2009, 2014):
    full[datetime(year,1,1):datetime(year,12,31)].pct_change().corr().to_csv('output/' + str(year) + '_corr.csv', float_format='%3.3f')

#Generating totals by weekday(https://dataplaysite.wordpress.com/2015/11/10/test/)
full_weekday = full.copy()
full_weekday['weekday'] = full_weekday.index.dayofweek
#Monday is 0 and Sunday is 6
full_weekday.groupby('weekday').sum().to_csv('output/total_weekday.csv', float_format='%3.3f')

#Extracting weather data from climate data(https://dataplaysite.wordpress.com/2015/11/13/canada-weatherclimate-data/)
def cleanWeatherCsv(fileName):
    weather = pd.read_csv(fileName, header=23, encoding="ISO-8859-1")
    weather.columns = ['Date','Y','M','D','Quality',"MaxTempC","MaxTempFlag","MinTempC","MinTempFlag",
                       "MeanTempC","MeanTempFlag","HeatDegDaysC","HeatDegDaysFlag","CoolDegDaysC",
                       "CoolDegDaysFlag","TotalRainmm","TotalRainFlag","TotalSnowcm","TotalSnowFlag","TotalPrecipmm",
                       "TotalPrecipFlag","SnowonGrndcm","SnowonGrndFlag","DirofMaxGust10sdeg","DirofMaxGustFlag",
                       "SpdofMaxGustkmh","SpdofMaxGustFlag"]
    weather = weather[['Date',"MeanTempC","TotalPrecipmm","SpdofMaxGustkmh"]]
    weather['Date'] = pd.to_datetime(weather['Date'], format="%Y-%m-%d")
    weather = weather.set_index('Date')
    weather[['MeanTempC']] = weather[['MeanTempC']].fillna(method='ffill')
    weather[['TotalPrecipmm']] = weather[['TotalPrecipmm']].fillna(0)
    weather['SpdofMaxGustkmh'] = weather['SpdofMaxGustkmh'].apply(lambda x:float(str(x).replace('<','')))
    return weather

full_weather = []
for fileName in ['data/eng-daily-01012009-12312009.csv',
                 'data/eng-daily-01012010-12312010.csv',
                 'data/eng-daily-01012011-12312011.csv',
                 'data/eng-daily-01012012-12312012.csv',
                 'data/eng-daily-01012013-12312013.csv']:
    full_weather.append(cleanWeatherCsv(fileName))
full_weather = pd.concat(full_weather)

rainmm = full_weather['TotalPrecipmm']
windkmh = full_weather['SpdofMaxGustkmh']
tempC = full_weather['MeanTempC']
bike_total_day = pd.DataFrame(full.sum(axis=1),columns=['BikeCount'])

def plotWeatherComparison(startDate, endDate, climate):
    axes = bike_total_day[startDate:endDate].plot()
    climate[startDate:endDate].plot(ax=axes, secondary_y=True, kind='area', color='teal', alpha=0.3, stacked=False)
    fig = axes.get_figure()
    fig.savefig('output/weather_comparison_' + climate.name + '_' + startDate.strftime("%Y%m%d") + '_' + endDate.strftime("%Y%m%d") + '.png')

plotWeatherComparison(datetime(2010,1,1),datetime(2010,6,30), tempC)
plotWeatherComparison(datetime(2010,7,31),datetime(2010,12,31), tempC)
plotWeatherComparison(datetime(2010,1,1),datetime(2010,6,30), rainmm)
plotWeatherComparison(datetime(2010,7,31),datetime(2010,12,31), rainmm)
plotWeatherComparison(datetime(2010,1,1),datetime(2010,6,30), windkmh)
plotWeatherComparison(datetime(2010,7,31),datetime(2010,12,31), windkmh)
