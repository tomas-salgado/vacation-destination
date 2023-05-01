import json
import os
from flask import Flask, render_template, request
from flask_cors import CORS
from helpers.MySQLDatabaseHandler import MySQLDatabaseHandler
import nltk
import ast
from sklearn.preprocessing import normalize
from sklearn.feature_extraction.text import TfidfVectorizer
from scipy.sparse.linalg import svds
import pandas as pd
import numpy as np

# ROOT_PATH for linking with all your files. 
# Feel free to use a config.py or settings.py with a global export variable
# os.environ['ROOT_PATH'] = os.path.abspath(os.path.join("..",os.curdir))

# # These are the DB credentials for your OWN MySQL
# # Don't worry about the deployment credentials, those are fixed
# # You can use a different DB name if you want to
# MYSQL_USER = "root"
# MYSQL_USER_PASSWORD = "L&83ksh!3"
# MYSQL_PORT = 3306
# MYSQL_DATABASE = "kardashiandb"

# mysql_engine = MySQLDatabaseHandler(MYSQL_USER,MYSQL_USER_PASSWORD,MYSQL_PORT,MYSQL_DATABASE)

# # Path to init.sql file. This file can be replaced with your own file for testing on localhost, but do NOT move the init.sql file
# mysql_engine.load_file_into_db('.././vacation-destination/init.sql') #may need to add path to init.sql as parameter here

app = Flask(__name__)
CORS(app)


# metadata
def main(query):
    # construct data
    files = ['api_data_usacomp.csv', 'api_data_5+mil.csv', 'api_data_2_5_mil.csv', 'api_data_1_2_mil.csv',
             'api_data_250_500k.csv']#, 'api_data_100_250k.csv']
    df = pd.DataFrame()
    for file in files:
        data = pd.read_csv(file, names=['City', 'Longitude', 'Latitude', 'Ratings', 
                                             'ObjectNames', 'Description'])
        df = pd.concat([df, data], axis=0)
    df = df[df['Description'] != '[]']
    df.reset_index(inplace=True)
    p = df['Description']

    # cosine similarity 
    vectorizer = TfidfVectorizer(stop_words = 'english', max_df = .7, min_df = 1)
    td_matrix = vectorizer.fit_transform([x for x in df['Description']])
    td_matrix_np = td_matrix.toarray()
    td_matrix_np = normalize(td_matrix_np)
    docs_compressed, s, words_compressed = svds(td_matrix, k=100)
    words_compressed = words_compressed.transpose()
    docs_compressed_normed = normalize(docs_compressed)
    word_to_index = vectorizer.vocabulary_
    index_to_word = {i:t for t,i in word_to_index.items()}

    data = []
    # driver code
    query = input("Type a query: ")
    # query = "beaches"
    query = vectorizer.transform([query]).toarray()
    query_vec = normalize(np.dot(query, words_compressed)).squeeze()
    def closest_cities_to_query(query_vec_in, k = 5):
        sims = docs_compressed_normed.dot(query_vec_in)
        asort = np.argsort(-sims)[:k+1]
        return [(i, df['City'][i], sims[i]) for i in asort[1:]]

    for i, city, sim in closest_cities_to_query(query_vec):
        if sim != 0:
            objects_str = df['ObjectNames'][i]
            descr_str = df['Description'][i]
            ratings_str = df['Ratings'][i]
            objects = ast.literal_eval(objects_str)
            descriptions = ast.literal_eval(descr_str)
            description_sims = [normalize(np.dot(vectorizer.transform([i]).toarray(), words_compressed)).squeeze() 
                                for i in descriptions]
            description_sims = [i.dot(query_vec) for i in description_sims]
            idx = np.argpartition(description_sims, max(-len(description_sims),-5))[-5:]
            ratings = ast.literal_eval(ratings_str)
            ratings = [int(ratings[i][0]) for i in range(len(ratings))]

            top_objects = [objects[i] for i in idx]
            top_obj_descriptions = [descriptions[i] for i in idx]
            rating_score = int(np.mean(ratings)/3*100)

            print(city) 
            print('Similarity Score: ', sim)
            print("Popularity Score: ", rating_score)
            print('Top Attractions: ')
            print("{}".format(top_objects))
        else:
            print('No Matches Found!')

        data.append({'a': city, 'b': top_objects[i]})
#         print(top_5[i], '- Top Attractions:', objects[np.argmax(ratings)])
    print(json.dumps([data]))
    return json.dumps(data)


@app.route("/")
def home():
    return render_template('base.html',title="sample html")


@app.route("/episodes")
def episodes_search():
    text = request.args.get("title")
    return main(text)


#app.run(debug=True)

