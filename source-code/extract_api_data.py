import requests
import json
import csv

apiKey = "" #apiKey goes here. Get from OpenTripMaps API website

#change cities list here to get what you need. Right now it only works for US cities
cities = ['San Francisco']
#cities = ['San Antonio', 'San Diego', 'San Jose', 'Seattle', 'St. Louis', 'Tampa', 'Tucson', 'Virginia', 'Washington', 'Wichita']
#cities = ['New York City', 'Oklahoma', 'Omaha', 'Palm Springs', 'Philadelphia', 'Phoenix', 'Pittsburg', 'Portland', 'Sacramento', 'Salt Lake']
#cities = ['Las Vegas', 'Lake Havasu', 'Los Angeles', 'Louisville', 'Memphis', 'Miami', 'Milwaukee', 'Minneapolis', 'Nashville', 'New Orleans']
#cities = ['Dallas', 'Denver', 'Detroit', 'El Paso', 'Fairbanks', 'Fresno', 'Houston', 'Indianapolis', 'Jacksonville', 'Kansas City']
#cities = ['Albuquerque', 'Anchorage', 'Atlanta', 'Austin', 'Baltimore', 'Boise', 'Boston', 'Charlotte', 'Chicago', 'Columbus']


#top 100 cities from https://www.delicious.com.au/travel/international/gallery/100-cities-deserve-place-travel-bucket-list/o4lzlr69
#cities = [['Seattle', 'US']]
#cities = [['Paris', 'FR'], ['Rio de Janeiro', 'BR'], ['New York', 'US'], ['Rome', 'IT'], ['London', 'GB'], ['Tokyo', 'JP'], ['Lisbon', 'PT'], ['Barcelona', 'ES'], ['Honolulu', 'US'], ['Istanbul', 'TR']]
#['Chicago', 'US'], ['Miami', 'US'], ['Seattle', 'US'], 
coordinates = []

for city in cities:
    city_name = city.replace(" ", "%20")
    country_code = 'US'
    #city_name = city[0].replace(" ", "%20")
    #country_code = city[1]
    url = 'https://api.opentripmap.com/0.1/en/places/geoname?name='+city_name+'&country='+country_code+'&apikey='+apiKey
    response = requests.get(url)

    # Check if the response was successful (i.e., status code 200)
    if response.status_code == 200:
        # Extract the JSON data from the response
        data = json.loads(response.text)
        
        # Access and process the data as needed
        city_coord = []
        city_coord.append(data['lon'])
        city_coord.append(data['lat'])
        coordinates.append(city_coord)
    else:
        # If the response was not successful, print an error message
        print('Error: API returned status code', response.status_code)
print(coordinates)


#get top 10 object ids for each city
all_object_ids = []
for coordinate in coordinates:
    url = ('https://api.opentripmap.com/0.1/en/places/radius?radius=10000&lon='+str(coordinate[0])
           +'&lat='+str(coordinate[1])+'&kinds=cultural%2Chistorical_places%2Cmonuments_and_memorials%2Cnatural%2Csport&rate=3&format'
           +'=json&limit=10&apikey='+apiKey)
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
print(all_object_ids)


#get descriptions for each object
descriptions = []

for city in all_object_ids:
    city_descriptions = []
    for object_id in city: 
        url = 'https://api.opentripmap.com/0.1/en/places/xid/'+ str(object_id)+'?apikey='+apiKey
        response = requests.get(url)

        # Check if the response was successful (i.e., status code 200)
        if response.status_code == 200:
            # Extract the JSON data from the response
            data = json.loads(response.text)
            
            # Access and process the data as needed
            city_descriptions.append(data['wikipedia_extracts']['text'])
        else:
            # If the response was not successful, print an error message
            print('Error: API returned status code', response.status_code)
    descriptions.append(city_descriptions)
#print(descriptions)


#------------------------------------------------------------------------------
#Store data in CSV file

# Open a new CSV file for writing
with open('api_data.csv', mode='a', newline='') as file:
    # Create a CSV writer object
    writer = csv.writer(file)

    # Write a header row
    #writer.writerow(['City', 'Descriptions'])

    # Write some data rows
    for city in range(len(cities)):
        writer.writerow([cities[city], descriptions[city]])
