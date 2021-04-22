# Written by Nandi Moksnes 2021-04
##Usage limits https://www.renewables.ninja/documentation
##Anonymous users are limited to a maximum of 5 requests per day.
##To increase this limit to 50 per hour, please register for a free user account on renewable.ninja
import time
import csv
import os
import sys
import geopandas as gpd
import pandas as pd
import subprocess

### Parameters setting##
token = 'ed519952eff7850cece8c746347fee2d068ab988' #add your token for API from your own log in on Renewable Ninja
time_zone_offset = 3 #Kenya is UTC + 3hours to adjust for the time zone
######

def project_vector(vectordata):
    print(vectordata)
    gdf = gpd.read_file(vectordata)
    gdf_wgs84 = gdf.to_crs(4326)

    return(gdf_wgs84)

#Make CSV files for the download loop
def csv_make(coordinates):

    coordinates['lon'] = coordinates.geometry.apply(lambda p: p.x)
    coordinates['lat'] = coordinates.geometry.apply(lambda p: p.y)
    print(coordinates)
    df = pd.DataFrame(coordinates)
    wind = pd.DataFrame(index=df.index, columns=(['name', 'lat', 'lon', 'from', 'to', 'dataset', 'capacity', 'height', 'turbine']))
    wind["name"] = df ["pointid"]
    wind["lat"] = df["lat"]
    wind["lon"] = df["long"]
    wind["from"] = "01/01/2016"
    wind["to"] = "31/12/2016"
    wind["dataset"] = "merra2"
    wind["capacity"] = 1
    wind["height"] = 55
    wind["turbine"] = "Vestas+V42+600"
    solar = pd.DataFrame(index=df.index, columns=(['name', 'lat', 'lon', 'from', 'to', 'dataset', 'capacity', 'system_loss', 'tracking', 'tilt', 'azim']))
    solar["name"] = df ["pointid"]
    solar["lat"] = df["lat"]
    solar["lon"] = df["long"]
    solar["from"] = "01/01/2016"
    solar["to"] = "31/12/2016"
    solar["dataset"] = "merra2"
    solar["capacity"] = 1
    solar["system_loss"] = 0.1
    solar["tracking"] = 0
    solar["tilt"] = 35
    solar["azim"] = 180

    #Make wind csv-files
    i = 0
    while i < len(wind.index+6):
        temp = []
        for x in range(i,i+6):
            if x <=len(wind.index):
                currentLine = list(wind.iloc[[x]].iloc[0])
                temp.append(currentLine)
        fields = ['name', 'lat', 'lon', 'from', 'to', 'dataset', 'capacity', 'height', 'turbine']
        rows = temp
        with open("temp/wind_%i-%i.csv" %(i, i+6), 'w') as f:
            write = csv.writer(f)
            write.writerow(fields)
            write.writerows(rows)
        i += 6

    #Make solar csv-files
    j = 0
    while j < len(solar.index):
        temp = []
        for x in range(j,j+6):
            if x <=len(solar.index+6):
                currentLine = list(solar.iloc[[x]].iloc[0])
                temp.append(currentLine)
        fields = ['name', 'lat', 'lon', 'from', 'to', 'dataset', 'capacity', 'system_loss', 'tracking', 'tilt', 'azim']
        rows = temp
        with open("temp/solar%i-%i.csv" %(j, j+6), 'w') as f:
            write = csv.writer(f)
            write.writerow(fields)
            write.writerows(rows)
        j += 6

def download(path):
    files = [os.path.join(dp, f) for dp, dn, filenames in os.walk(path) for f in filenames if
               os.path.splitext(f)[1] == '.csv']
    j = 0
    max_hour =3601
    start_hour = time.time()
    while True:

        print("looping...")
        remaining_hour = max_hour + start_hour - time.time()
        print("%s seconds remaining" % int(remaining_hour))

        if remaining_hour <= 0:
            break

        count = 0
        max = 50
        start = time.time()
        while True:

            type = "wind"
            current = os.getcwd()
            type(current)
            ### Do other stuff, it won't be blocked
            time.sleep(0.1)
            print("looping...")

            ### This will be updated every loop
            remaining = max + start - time.time()
            #print("%s seconds remaining" % int(remaining))

            ### Countdown finished, ending loop
            if remaining <= 0:
                break
            #"C:/Users/nandi/Box Sync/PhD/Paper 3-OSeMOSYS 40x40/GIS_python_build/GEOSeMOSYS_reprod/GEOSeMOSYS_Kenya/src"
            while count <1:
                i=0
                csvfiles = path +"/wind_%i-%i.csv" %(i,i+6)
                csvfilesout = path +"/wind_%i-%i_out.csv" %(i,i+6)
                print(csvfiles)
                subprocess.call('C:/TPFAPPS/R/R-4.0.1/bin/RScript GEOSeMOSYS_download.r %s'+ token +" "+type+" "+ csvfiles+" "+csvfilesout %(current), shell=True )
                count +=1
        time.sleep(59)
        j+=1

if __name__ == "__main__":
    shapefile, path= sys.argv[1],sys.argv[2]
    coordinates = project_vector(shapefile)
    csv = csv_make(coordinates)

    down = download(path)

