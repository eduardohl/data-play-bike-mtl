# coding: utf-8
import pandas as pd
import matplotlib.pyplot as plt

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

