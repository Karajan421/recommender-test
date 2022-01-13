import flask
import difflib
import pandas as pd
from sklearn.feature_extraction.text import CountVectorizer
from sklearn.metrics.pairwise import cosine_similarity
from sqlalchemy import create_engine
import sqlalchemy as db

app = flask.Flask(__name__, template_folder='templates')
df2 = pd.read_csv('./model/appstore_minimal_infos.csv')

count = CountVectorizer(stop_words='english')
count_matrix = count.fit_transform(df2['processed_desc'])
cosine_sim2 = cosine_similarity(count_matrix, count_matrix)

indices = pd.Series(df2.index, index=df2['App_Name'])
all_titles = [df2['App_Name'][i] for i in range(len(df2['App_Name']))]

def get_recommendations(title) :
    db_connection_str = 'mysql+pymysql://kp8bfsn35swe3v5b:ck2zrlkwnwzvdohh@ohunm00fjsjs1uzy.cbetxkdyhwsb.us-east-1.rds.amazonaws.com/guqmq0edurs4j7o9'
    db_connection = create_engine(db_connection_str)
    connection = db_connection.connect()
    metadata = db.MetaData()
    apps = db.Table('apps', metadata, autoload=True, autoload_with=db_connection)
    cosine_sim = cosine_similarity(count_matrix, count_matrix)
    idx = indices[title]
    sim_scores = list(enumerate(cosine_sim[idx]))
    sim_scores = sorted(sim_scores, key=lambda x: x[1], reverse=True)
    sim_scores = sim_scores[1:11]
    movie_indices = [i[0] for i in sim_scores]
    tit = df2['App_Name'].iloc[movie_indices]
   
    query = db.select([apps.columns.title, apps.columns.description]).where(apps.columns.title.in_(tit))
    ResultProxy = connection.execute(query)
    data = ResultProxy.fetchall()
    
    return_df = pd.DataFrame(columns=['Title','Link', 'Rating', 'Reviews', 'Description'])
    return_df['Title'] = tit
    titles = [i[0] for i in data]
    description = [i[1] for i in data]
    df = pd.DataFrame(titles, columns=['titles'])
    df["description"] = description
    return_df = df
    return return_df

# Set up the main route
@app.route('/', methods=['GET', 'POST'])

def main():
    if flask.request.method == 'GET':
        return(flask.render_template('index.html'))
            
    if flask.request.method == 'POST':
        m_name = flask.request.form['movie_name']
        m_name = m_name.title()
#        check = difflib.get_close_matches(m_name,all_titles,cutout=0.50,n=1)
        if m_name not in all_titles:
            return(flask.render_template('negative.html',name=m_name))
        else:
            result_final = get_recommendations(m_name)
            names = []
            dates = []
            rating =[]
            reviews = []
            description = []
            for i in range(len(result_final)):
                names.append(result_final.iloc[i][0])
                dates.append(result_final.iloc[i][1])
                rating.append(result_final.iloc[i][2])
                reviews.append(result_final.iloc[i][3])
                description.append(result_final.iloc[i][4])

            return flask.render_template('positive.html',movie_names=names,movie_date=dates,movie_rating=rating,movie_reviews = reviews,movie_description=description, search_name=m_name)

if __name__ == '__main__':
    app.run()
