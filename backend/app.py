import json
import os
from flask import Flask, render_template, request
from flask_cors import CORS
from helpers.MySQLDatabaseHandler import MySQLDatabaseHandler
import nltk
from nltk import wordpunct_tokenize
from nltk.stem import PorterStemmer
from nltk.corpus import stopwords
import pandas as pd
import numpy as np

# ROOT_PATH for linking with all your files. 
# Feel free to use a config.py or settings.py with a global export variable
os.environ['ROOT_PATH'] = os.path.abspath(os.path.join("..",os.curdir))

# These are the DB credentials for your OWN MySQL
# Don't worry about the deployment credentials, those are fixed
# You can use a different DB name if you want to
MYSQL_USER = "root"
MYSQL_USER_PASSWORD = "L&83ksh!3"
MYSQL_PORT = 3306
MYSQL_DATABASE = "kardashiandb"

mysql_engine = MySQLDatabaseHandler(MYSQL_USER,MYSQL_USER_PASSWORD,MYSQL_PORT,MYSQL_DATABASE)

# Path to init.sql file. This file can be replaced with your own file for testing on localhost, but do NOT move the init.sql file
mysql_engine.load_file_into_db('.././vacation-destination/init.sql') #may need to add path to init.sql as parameter here

app = Flask(__name__)
CORS(app)

# if stopwords fails make sure it's been downloaded
nltk.download('stopwords')

def tokenize_str(string, tok_method, stemmer, stoplist):
    toks = wordpunct_tokenize(string)
    toks = [w for w in toks if w not in stoplist]
    toks = [stemmer.stem(w) for w in toks]
    toks = [w.lower() for w in toks if w.isalpha()]
    return toks


def city_word_indices(df, tok_method, stemmer, stops):
    desc = df['Description']
    all_toks = set()
    n_rows = len(desc)
    city_word_dic = {}
    for i in range(n_rows):
        toks = tokenize_str(desc[i], wordpunct_tokenize, stemmer, stops)
        tokset = toks
        all_toks = all_toks.union(tokset)
        city_word_dic[df['City'][i]] = toks
    all_toks = list(all_toks)
    all_toks.sort()
    cities = df['City'].tolist()
    cities.sort()
    city_index = dict(zip(cities, list(range(n_rows))))
    city_rev_index = dict(zip(list(range(n_rows)), cities))
    word_index = dict(zip(all_toks, list(range(len(all_toks)))))
    
    return city_index, city_rev_index, word_index, city_word_dic


# construct term-doc matrix
def td_matrix(df, city_index, city_rev_index, word_index, city_word_dic, 
              num_cities=None, num_words=None):
    if num_cities == None: 
        num_cities = len(city_index)

    if num_words == None: 
        num_words = len(word_index)

    td_matrix = np.zeros(shape=(num_cities, num_words))
    cities = df['City'].tolist()
    for city in cities:
        for word in city_word_dic[city]:
            td_matrix[city_index[city]][word_index[word]] += 1
    td_matrix = (td_matrix.T / np.linalg.norm(td_matrix, axis=1)).T
    return td_matrix, num_words, word_index


def process_query(query, td_matrix, city_rev_index, tok_method, stemmer, stops, num_words, word_index, num_results=2):
    query = tokenize_str(query, tok_method, stemmer, stops)
    qvec = np.zeros(num_words)
    for word in query:
        if word in word_index:
            qvec[word_index[word]] += 1
    np.seterr(invalid='ignore')
    qvec = qvec / np.linalg.norm(qvec)
    sim = td_matrix @ qvec
    top_k = (-sim).argsort()[:num_results]
    top_k = [city_rev_index[k] for k in top_k]
    return top_k 


# metadata
def main(query):
    df = pd.read_csv('./api_data.csv', names=['City', 'Description'])
    stoplist = set(stopwords.words('english'))
    ps = PorterStemmer()

    # driver code
    city_index, city_rev_index, word_index, city_word_dic = city_word_indices(df, wordpunct_tokenize, ps, stoplist)
    td_mat, num_words, word_index = td_matrix(df, city_index, city_rev_index, word_index, city_word_dic)
    top_2 = process_query(query, td_mat, city_rev_index, wordpunct_tokenize, ps, stoplist, num_words, word_index)
    print(top_2)
    data = {'a': top_2[0]}, {'a': top_2[1]}
    #print(type(dic))
    print(json.dumps([data]))
    return json.dumps(data)


# Sample search, the LIKE operator in this case is hard-coded, 
# but if you decide to use SQLAlchemy ORM framework, 
# there's a much better and cleaner way to do this
def sql_search(episode):
    query_sql = f"""SELECT * FROM episodes WHERE LOWER( title ) LIKE '%%{episode.lower()}%%' limit 10"""
    keys = ["id","title","descr"]
    data = mysql_engine.query_selector(query_sql)
    print(json.dumps([dict(zip(keys,i)) for i in data]))
    return json.dumps([dict(zip(keys,i)) for i in data])

@app.route("/")
def home():
    return render_template('base.html',title="sample html")

@app.route("/episodes")
def episodes_search():
    text = request.args.get("title")
    #return sql_search(text)
    return main(text)

#app.run(debug=True)
