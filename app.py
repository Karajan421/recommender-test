
import flask
import difflib
import pandas as pd
from sklearn.feature_extraction.text import CountVectorizer
from sklearn.metrics.pairwise import cosine_similarity

app = flask.Flask(__name__, template_folder='templates')

df2 = pd.read_csv('appstore_full_infos2.csv')
#df2 = df2[95000:]
df2 = df2.reset_index(drop=True)
#df2["description"] = df2["description"].fillna("")
#df2["processed_desc1"] = df2["processed_desc1"].fillna("")

count = CountVectorizer(stop_words='english')

count_matrix = count.fit_transform(df2['processed_desc'])

cosine_sim2 = cosine_similarity(count_matrix, count_matrix)

#df2 = df2.reset_index()
indices = pd.Series(df2.index, index=df2['App_Name'])
all_titles = [df2['App_Name'][i] for i in range(len(df2['App_Name']))]

def get_recommendations(title) :
    cosine_sim = cosine_similarity(count_matrix, count_matrix)
    idx = indices[title]
    sim_scores = list(enumerate(cosine_sim[idx]))
    sim_scores = sorted(sim_scores, key=lambda x: x[1], reverse=True)
    sim_scores = sim_scores[1:11]
    movie_indices = [i[0] for i in sim_scores]
    tit = df2['App_Name'].iloc[movie_indices]
    dat = df2['AppStore_Url'].iloc[movie_indices]
    rat = df2['Average_User_Rating'].iloc[movie_indices]
    rev = df2['Reviews'].iloc[movie_indices]
    des = df2['description'].iloc[movie_indices]
    
    return_df = pd.DataFrame(columns=['Title','Link', 'Rating', 'Reviews', 'Description'])
    return_df['Title'] = tit
    return_df['Link'] = dat
    return_df['Rating'] = rat
    return_df['Reviews'] = rev
    return_df['Description'] = des
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
