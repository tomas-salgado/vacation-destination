import requests
import json
import csv
import pandas as pd

apiKey = #apiKey goes here. Get from OpenTripMaps API website

#change cities list here to get what you need. Right now it only works for US cities
# cities = ['San Francisco']
#cities = ['San Antonio', 'San Diego', 'San Jose', 'Seattle', 'St. Louis', 'Tampa', 'Tucson', 'Virginia', 'Washington', 'Wichita']
#cities = ['New York City', 'Oklahoma', 'Omaha', 'Palm Springs', 'Philadelphia', 'Phoenix', 'Pittsburg', 'Portland', 'Sacramento', 'Salt Lake']
#cities = ['Las Vegas', 'Lake Havasu', 'Los Angeles', 'Louisville', 'Memphis', 'Miami', 'Milwaukee', 'Minneapolis', 'Nashville', 'New Orleans']
#cities = ['Dallas', 'Denver', 'Detroit', 'El Paso', 'Fairbanks', 'Fresno', 'Houston', 'Indianapolis', 'Jacksonville', 'Kansas City']
#cities = ['Albuquerque', 'Anchorage', 'Atlanta', 'Austin', 'Baltimore', 'Boise', 'Boston', 'Charlotte', 'Chicago', 'Columbus']

import os
current_directory = os.getcwd()
print(current_directory) 

df = pd.read_csv("C:/Users/ajita/Documents/CS4300/Untitled Folder/worldcities.csv")
# print(df.head())
df = df[(df['population'] < 250000) & (df['population'] >= 100000)]
df = df[df['iso3'] != 'USA']
cities = df['city_ascii'].tolist()

#top 100 cities from https://www.delicious.com.au/travel/international/gallery/100-cities-deserve-place-travel-bucket-list/o4lzlr69
# cities = [['Seattle', 'US']]
#cities = [['Paris', 'FR'], ['Rio de Janeiro', 'BR'], ['New York', 'US'], ['Rome', 'IT'], ['London', 'GB'], ['Tokyo', 'JP'], ['Lisbon', 'PT'], ['Barcelona', 'ES'], ['Honolulu', 'US'], ['Istanbul', 'TR']]
#['Chicago', 'US'], ['Miami', 'US'], ['Seattle', 'US'], 
coordinates = list(zip(df['lng'].tolist(), df['lat'].tolist()))
n_cities = len(cities)

# count1 = 0
# for city in cities:
#     print('grabbing coordinates for', city, str(int(count1/n_cities * 100)) + '%', 'complete')
#     city_name = city.replace(" ", "%20")
#     country_code = 'US'
#     #city_name = city[0].replace(" ", "%20")
#     #country_code = city[1]
#     url = 'https://api.opentripmap.com/0.1/en/places/geoname?name='+city_name+'&country='+country_code+'&apikey='+apiKey
#     response = requests.get(url)

#     # Check if the response was successful (i.e., status code 200)
#     if response.status_code == 200:
#         # Extract the JSON data from the response
#         data = json.loads(response.text)
        
#         # Access and process the data as needed
#         city_coord = []
#         city_coord.append(data['lon'])
#         city_coord.append(data['lat'])
#         coordinates.append(city_coord)
#     else:
#         # If the response was not successful, print an error message
#         print('Error: API returned status code', response.status_code)
#     count1 += 1
# # print(coordinates)
print("Grabbed coordinates")

#get top 50 object ids for each city
all_object_ids = []
count2 = 0
for coordinate in coordinates:
    print('grabbing objects:', str(int(count2/n_cities * 100)) + '%', 'complete')
    url = ('https://api.opentripmap.com/0.1/en/places/radius?radius=10000&lon='+str(coordinate[0])
           +'&lat='+str(coordinate[1])+'&kinds=cultural%2Chistorical_places%2Cmonuments_and_memorials%2Cnatural%2Csport&rate=3&format'
           +'=json&limit=50&apikey='+apiKey)
    response = requests.get(url)

    # Check if the response was successful (i.e., status code 200)
    if response.status_code == 200:
        # Extract the JSON data from the response
        data = json.loads(response.text)
        
        # Access and process the data as needed
        #print(data)
        object_ids = []
        for object in data:
            object_ids.append(object['xid'])

        all_object_ids.append(object_ids)
    else:
        # If the response was not successful, print an error message
        print('Error: API returned status code', response.status_code)
    count2 += 1
print('Grabbed Objects')

#get descriptions for each object
descriptions = []
ratings = []
names = []

for city in range(n_cities):
    city_descriptions = []
    object_names = []
    object_ratings = []
    for object_id in all_object_ids[city]: 
        url = 'https://api.opentripmap.com/0.1/en/places/xid/'+ str(object_id)+'?apikey='+apiKey
        response = requests.get(url)

        # Check if the response was successful (i.e., status code 200)
        if response.status_code == 200:
            # Extract the JSON data from the response
            data = json.loads(response.text)
            
            # Access and process the data as needed
            if 'wikipedia_extracts' in data:
                city_descriptions.append(data['wikipedia_extracts']['text'])
                object_names.append(data['name'])
                object_ratings.append(data['rate'])
        else:
            # If the response was not successful, print an error message
            print('Error: API returned status code', response.status_code)
    descriptions.append(city_descriptions)
    ratings.append(object_ratings)
    names.append(object_names)
    print("got descriptions for", cities[city], str(int(city/n_cities * 100)) + '%', 'complete')
#print(descriptions)


#------------------------------------------------------------------------------
#Store data in CSV file

# Open a new CSV file for writing
with open('C:/Users/ajita/Documents/CS4300/Untitled Folder/api_data_100_250k.csv', mode='a', newline='', encoding='utf-8') as file:
    # Create a CSV writer object
    writer = csv.writer(file)

    # Write a header row
    #writer.writerow(['City', 'Descriptions'])

    # Write some data rows
    for city in range(len(cities)):
        writer.writerow([cities[city], coordinates[city][0], coordinates[city][1], ratings[city], names[city], descriptions[city]])
