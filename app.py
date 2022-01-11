import pandas as pd
import flask
import difflib
from nltk.corpus import stopwords
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import linear_kernel
from wordcloud import WordCloud, STOPWORDS

result = pd.read_csv("model.csv")
result = result.drop_duplicates(subset=['title'])
result = result[50000:]
#result1 = result.loc[result['genre'] == TARGET_GENRE]
result1 = result.reset_index(drop=True)
result1["description"] = result1["description"].fillna("")
result1["processed_desc1"] = result1["processed_desc1"].fillna("")

app = flask.Flask(__name__, template_folder='templates')

#full_text = list(train['description'].values) #+ list(test['Phrase'].values)
#vectorizer = TfidfVectorizer (max_features=2500, ngram_range=(1, 3), min_df=7, max_df=0.8, stop_words=stopwords.words('english'))
#vectorizer.fit_transform(full_text).toarray()
#vectorizer.fit_transform(full_text)
#train_vectorized = vectorizer.transform(train['description'])
#test_vectorized = vectorizer.transform(test['description'])

stopwords_list = STOPWORDS.union(set(['Games', 'the', 'to', 'will', 'make', 'play', 'level', 'get', 'use', 
                                      "samsung", "Samsung", "galaxy", "Galaxy", "xiaomi", "pixel", "google", 
                                      'game', "games", "list", "and", "for", "price", "quot", "it", 'we', 'don', 
                                      'you', 'ce', 'hasn', 'sa', 'do', 'som', 'can']))
        # Some words which might indicate a certain sentiment are kept via a whitelist
vectorizer= TfidfVectorizer(max_features = 2500, ngram_range=(1,2), min_df=7, max_df=0.8, 
                            stop_words=stopwords_list)

#Construct the required TF-IDF matrix by applying the fit_transform method on the overview feature
overview_matrix = vectorizer.fit_transform(result1["processed_desc1"])
similarity_matrix = linear_kernel(overview_matrix,overview_matrix)
#games index mapping
mapping = pd.Series(result1.index,index = result1["title"])
# Compute the cosine similarity matrix
cosine_sim = linear_kernel(overview_matrix,overview_matrix)

def get_recommendations(app, cosine_sim=cosine_sim):
    
    idx = mapping[app]
    #get similarity values with other games
    #similarity_score is the list of index and similarity matrix
    similarity_score = list(enumerate(cosine_sim[idx]))
    #sort in descending order the similarity score of game inputted with all the other games
    similarity_score = sorted(similarity_score, key=lambda x: x[1], reverse=True)
    # Get the scores of the 15 most similar games. Ignore the first game.
    similarity_score = similarity_score[1:25]
    #return game names using the mapping series
    result_indices = [i[0] for i in similarity_score]
    
    result_score = [i[1] for i in similarity_score]
    
    result2 = result1.iloc[result_indices]
    result2["score"] = result_score
    #return (result1.iloc[result_indices])
    return result2


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
            for i in range(len(result_final)):
                names.append(result_final.iloc[i][0])
                dates.append(result_final.iloc[i][1])

            return flask.render_template('positive.html',movie_names=names,movie_date=dates,search_name=m_name)

if __name__ == '__main__':
    app.run()
