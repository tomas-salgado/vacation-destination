import csv
from collections import defaultdict


def csv_to_diction(csv_file_path):
    with open(csv_file_path, 'r') as csv_file:
        reader = csv.DictReader(csv_file)
        temp_dict = {}
        for row in reader:
            temp_dict[row['CITY']] = row['ANN']

    return temp_dict


def csv_to_diction_crime(csv_file_path):
    with open(csv_file_path, 'r') as csv_file:
        reader = csv.DictReader(csv_file)
        crime_dict = {}
        for row in reader:
            crime_dict[row['communityname']] = row['ViolentCrimesPerPop']
        return crime_dict


my_csv_to_dict = csv_to_diction('city_temperature.csv')
my_csvcrime = csv_to_diction_crime('crime_data_.csv')


def avg_temps(from_csv_dict):
    temp_acc = defaultdict(list)
    for City, AvgTemperature in from_csv_dict.items():
        temp_acc[City].append(AvgTemperature)

    avg_temperatures = {}
    for City, AvgTemperature in temp_acc.items():
        avg_temperature = sum(AvgTemperature) / len(AvgTemperature)
        avg_temperatures[City] = avg_temperature

    return avg_temperatures


def find_closest_temps(avg_temp, input_temp):
    temp_diff = {city: abs(temperature - input_temp)
                 for city, temperature in avg_temp.items()}
    cities_sorted = sorted(temp_diff.keys(),
                           key=lambda city: temp_diff[city])
    return [(city, avg_temp[city]) for city in cities_sorted]


def calculate_city_scores(api_scores, temp_data):
    # Find the closest temperatures for each city
    closest_temps = find_closest_temps(temp_data, input_temp)

   # Process the query and get the top cities
    query = input("Type a query: ")
    top_k = process_query(query, td_mat, city_rev_index,
                          wordpunct_tokenize, ps, stops)

    # Calculate the city scores for the top cities
    city_scores = {}
    for city in top_k:
        api_score = api_scores[city]
        temp_score = closest_temps[city]
        city_scores[city] = api_score**2 + api_score / \
            len(api_scores) + temp_score / len(closest_temps)

    final_ranking = sorted(city_scores.items(),
                           key=lambda x: x[1], reverse=True)
    return final_ranking


# API scores format should be as below as an example
api_scores = {
    'City 1': 0.87,
    'City 2': 0.75,
    'City 3': 0.67
}


# Temperature data should be as below as an example
temp_data = {
    'City 1': .7,
    'City 2': 0.6,
    'City 3': 0.46
}


# Calculate the city scores
city_scores = calculate_city_scores(api_scores, temp_data)


# Print the city scores
print(city_scores)


# def main():
#     find_closest_temps(my_csv_to_dict, 40)
