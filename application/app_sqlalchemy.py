# TO RUN: streamlit run app_sqlalchemy.py

# This is the main app file. This uses Streamlit, which is a python based library, to create the UI. 
# This file is heart of the application. Open the file for furthur understanding and to see the comments.
# TO RUN the application enter **streamlit run app_sqlalchemy.py** in the terminal from the directory this project resides.

# importing the necessary libraries
import streamlit as st
import pickle
from PIL import Image
import pandas as pd
import urllib
import numpy as np
from sqlalchemy.orm import sessionmaker
from sqlalchemy import func
from database_engine import engine
import seaborn as sns
import matplotlib.pyplot as plt
# importing the objects of the tables in the database
from models import AvgRatingCount
from models import Ratings
from models import Links
from models import UsersByGenre
from models import MoviesNew
# importing required user defined functions for this application
from similar_to_users_better import similar_to_user
from recommending_a_movie import recommendation_movie
from svd_clustering_knn import nearest_neighbours_similar
from svd_clustering_knn import svd_on_usersgerne
from svd_clustering_knn import clustering_kmeans
from pagination_in_streamlit import paged_list_using_session
from top_movies_by_genre import top_movies_genre

import warnings
warnings.filterwarnings('ignore')

# Initialize connection.
# Uses st.experimental_singleton to only run once.
@st.experimental_singleton
def load_session():
    Session = sessionmaker(bind=engine)
    session = Session()
    return session

# This method gets the text for the opening page from the readme file of this project's repository in my github
@st.cache(show_spinner=False)
def get_file_content_as_string(path):
    url = 'https://raw.githubusercontent.com/vk18mishra/Movielens-Misc-Project/main/' + path
    response = urllib.request.urlopen(url)
    return response.read().decode("utf-8")

@st.experimental_memo
def make_nice_plot(X, labels):
    st.write("Making the plot showing clusters\n")
    # sns.set(rc={'figure.figsize':(15,10)})

    fig = plt.figure(figsize=(15, 10))
    # fig, ax = plt.subplots(figsize=(width, height))
    # Create a scatter plot with the x and y values of your data, using the 'hue' parameter to color the points based on their cluster labels
    sns.scatterplot(x=X[:, 0], y=X[:, 1], hue=labels, data=X, s=10)

    # Add a legend to the plot
    plt.legend(title='Cluster')

    # Show the plot
    st.pyplot(fig)


def main():
    # Starting SQLALchemy session
    session = load_session()
    # Getting the content for the homepage from the github
    readme_text = st.markdown(get_file_content_as_string("README.md"))
    
    # making the sidebar for showing and selecting between different application pages/operations
    st.sidebar.title("What to do")
    
    # These are the operations that our application will perform
    app_mode_main = st.sidebar.selectbox("Choose The Application Mode",
                                    ["Show instructions",
                                     "List of Movies", "Search movie by title or release year", "Top 10 Movies by genre",
                                     "Top 10 Most Similar Users(Better Version)",
                                     "Clustering Similar Users - Kmeans++", "Similar Users using KNN", 
                                     "Recommend a Movie - Using Clustering", "See README File"])
    
    
    
    # For going back to the homepage
    if app_mode_main == "Show instructions":
        st.sidebar.success('Choose the preferred option from the dropdown')
    
    
    elif app_mode_main == "Similar Users using KNN":
        readme_text.empty()
        st.header("Get top 10 Similar Users using KNN")
        # Text box for Getting the userId
        uId = st.text_input('Enter a User Id between (1 <= userId <= 162541), except 72314(outlier userId)', '0')
        # If userId is in range/valid - Our task starts
        if(int(uId) >= 1 and int(uId) <= 162541):
            st.write("Loading UsersByGenre in memory\n")
            main_df_copy = pd.read_sql(session.query(UsersByGenre).order_by(UsersByGenre.userId.asc()).statement, session.bind)
            # Outlier
            main_df_copy.drop(main_df_copy.iloc[72314].name,  inplace=True)
            X = svd_on_usersgerne(main_df_copy)
            similar_ui = nearest_neighbours_similar(X, main_df_copy, uId)
            
            # CSS to inject contained in a string
            hide_table_row_index = """
                        <style>
                        thead tr th:first-child {display:none}
                        tbody th {display:none}
                        </style>
                        """

            # Inject CSS with Markdown
            st.markdown(hide_table_row_index, unsafe_allow_html=True)
            
            st.write("""- _Printing the 10 nearest neighbours (first row is the user itself)_\n""")
            st.table(similar_ui)
        else:
            st.write("Input a valid UserID")
        
    
    elif app_mode_main == "Clustering Similar Users - Kmeans++":
        readme_text.empty()
        st.header('Clustering Similar Users - Kmeans++')
        st.write("Loading UsersByGenre in memory\n")
        main_df_copy = pd.read_sql(session.query(UsersByGenre).order_by(UsersByGenre.userId.asc()).statement, session.bind)
        # Outlier
        main_df_copy.drop(main_df_copy.iloc[72314].name,  inplace=True)
        # have to remove userId
        del main_df_copy['userId']
        X = svd_on_usersgerne(main_df_copy)
        labels = clustering_kmeans(X)
        make_nice_plot(X, labels)
    
    # Page for "Searching movie by title or release year" part of our application
    elif app_mode_main == "Search movie by title or release year":
        readme_text.empty()
        st.header('Search movie by title or release year')
        st.markdown('\n\n')
        
        # Getting the phrase the user wants to search for as a part of movie title or release year
        title = st.text_input('Enter a Movie title or year of release')
        # if something is inputted then our task starts
        if(len(title) > 0):
            st.write('You\'re looking for: ', title)
            title = title.lower()
            title_alc = "%{}%".format(title)
            
            # searching all the movie title matching the given phrase
            # Merging Links table as we want to show imdb links as well
            data = pd.read_sql(session.query(MoviesNew, Links).filter(MoviesNew.movieId == Links.movieId).filter(func.lower(MoviesNew.title).like(title_alc)).statement, session.bind)
            
            # preparing this returned data to show clickable links
            data['imdbId'] = 'https://www.imdb.com/title/tt' + data['imdbId'].astype(str)
            data.drop(data.columns.difference(['movieId','title', 'imdbId']), 1, inplace=True)
            # data = data.drop(['genres', 'movieId_1', 'tmdbId'], axis=1)
            data.columns = ['Movie Id', 'Movie Title', 'IMDB Link']
            
            # method to create the clickable hyperlinks and showing on our application 
            def create_link(url:str) -> str:
                return f'''<a href="{url}">🔗</a>'''

            # Creating clickable hyperlinks from imdbId of Links object
            data['IMDB Link'] = [create_link(url) for url in data["IMDB Link"]]
            N_tot = len(data.index)
            st.write(N_tot," Matching Results...")
            N = 10

            st.markdown('\n\n')
            st.header('Movies matching the given phrase')
            # This is an issue in streamlit - please try clearing cache and rerunning the application is nothing is shown as output
            st.markdown("**_If list is empty then try clearing cache (press c) and then rerun the app (press r)_**")

            # If total number of matches are greater than 10 then we divide them into pages with each containg 10
            paged_list_using_session(data, N, N_tot)
        # If nothing is entered then this is the output message
        else:
                st.markdown("Enter a valid phrase to search")
    
    
    
    # Application page for showing the list of the movies in form of pages, each containing 10 movies
    elif app_mode_main == "List of Movies":
        readme_text.empty()
        st.header('List of Movies with IMDB Link')
        st.markdown('\n\n')
        # Number of entries per screen
        N = 10

        # A variable to keep track of which product we are currently displaying
        if "page" not in st.session_state:
            st.session_state.page = 0

        # MAIN QUERY
        # Getting all the rows from the Movies table/object
        # Joining Links object as we want to show IMDB Link as well with each movie
        data = pd.read_sql(session.query(MoviesNew, Links).filter(MoviesNew.movieId == Links.movieId).statement, session.bind)

        # preparing this returned data to show clickable links
        data['imdbId'] = 'https://www.imdb.com/title/tt' + data['imdbId'].astype(str)
        data.drop(data.columns.difference(['movieId','title', 'imdbId']), 1, inplace=True)
        # data = data.drop(['genres', 'movieId_1', 'tmdbId'], axis=1)
        data.columns = ['Movie Id', 'Movie Title', 'IMDB Link']
        # method to create clickable hyperlinks
        def create_link(url:str) -> str:
            return f'''<a href="{url}">🔗</a>'''

        data['IMDB Link'] = [create_link(url) for url in data["IMDB Link"]]
        paged_list_using_session(data, N, len(data))
        
    
    # Application page for showing "Top 10 Movies by genre"
    elif app_mode_main == "Top 10 Movies by genre":
        readme_text.empty()
        st.header('Top 10 Movies by genre')
        st.markdown('\n\n')

        # getting the list of the genres
        with open('df_genres_main.pkl', 'rb') as f:
            df_genres_main = pickle.load(f)
        list_genres = []
        list_genres = df_genres_main['genre'].values
        # list_genres.insert(0,'No genre selected')
        list_genres = ['No genre selected'] + list(list_genres)

        # Getting the wordcloud/circlify image based on these genres. This was created in the Super Bonus subtask.
        # Please refer Super Bonus subtask for how it was made.
        circlify_wordcloud_genres = Image.open('circlify_wordcloud_genres.jpg')

        # drop down to select the genre
        genre = st.selectbox(
            'Choose a genre from the dropdown',
            list_genres)

        st.write('You selected:', genre)
        st.markdown('\n\n')

        if(genre != 'No genre selected'):
            top_movies_genre(genre)
        else:
            st.image(circlify_wordcloud_genres, caption='Genres and their frequency (generated by circlify)')   
    
    
    # Application page for showing "Top 10 Most Similar Users(Slower Version)"
    elif app_mode_main == "Top 10 Most Similar Users(Better Version)":
        readme_text.empty()
        st.header('Get Top 10 Most Similar Users, along with their similarity scores, according to given userId - - Better but Slower Version')
        st.markdown('\n\n')
        
        # Text box for Getting the userId
        uId = st.text_input('Enter a User Id between (1 <= userId <= 162541)', '0')
        # If userId is in range/valid - Our task starts
        if(int(uId) >= 1 and int(uId) <= 162541):
            st.write('You\'re looking for top 10 similar users for: ', uId)
            top10_similar_users = similar_to_user(uId)
            st.markdown('\n')
            st.header('Finally... the wait is over. Below are the top 10 most similar users:')
            
            # CSS to inject contained in a string
            hide_table_row_index = """
                        <style>
                        thead tr th:first-child {display:none}
                        tbody th {display:none}
                        </style>
                        """

            # Inject CSS with Markdown
            st.markdown(hide_table_row_index, unsafe_allow_html=True)
            
            st.table(top10_similar_users)
        # If userId is out of range/invalid
        else:
            st.header("Please enter a userId within range.")
    

    # Application page for "Recommending a Movie"
    elif app_mode_main == "Recommend a Movie - Using Clustering":
        readme_text.empty()
        st.header('Movie Recommendation to a user based on their preferred Genre and what similar users have watched - Using Clustering')
        st.markdown('\n')

        # getting the list of the genres
        with open('df_genres_main.pkl', 'rb') as f:
            df_genres_main = pickle.load(f)
        list_genres = []
        list_genres = df_genres_main['genre'].values
        
        # drop down to select the genre the user wants the recommendation from
        genre = st.selectbox(
            'Choose a genre from the dropdown',
            list_genres)

        st.write('You selected:', genre)
        st.markdown('\n\n')
        
        st.markdown('\n\n')
        # Text box for Getting the userId
        uId = st.text_input('Enter a User Id between (1 <= userId <= 162541)', '0')
        
        # If userId is in range/valid - Our task starts
        if(int(uId) >= 1 and int(uId) <= 162541):
            st.write('You\'re looking for top 10 similar users for: ', uId)
            
            st.write("Clustering the Users to get top 10 most similar users:\n")
            main_df_copy = pd.read_sql(session.query(UsersByGenre).order_by(UsersByGenre.userId.asc()).statement, session.bind)
            # Outlier
            main_df_copy.drop(main_df_copy.iloc[72314].name,  inplace=True)
            X = svd_on_usersgerne(main_df_copy)
            similar_ui = nearest_neighbours_similar(X, main_df_copy, uId)
            st.markdown("\nGetting all the movies rated by given user.\n")
            ratings = pd.read_sql(session.query(Ratings.userId, Ratings.movieId, Ratings.rating).filter(Ratings.userId == uId).statement, session.bind)
            movies_watched = ratings['movieId'].values
            recommended_movie = recommendation_movie(similar_ui, movies_watched, uId, session, genre)
            st.markdown('\n')
            
            if(len(recommended_movie) >= 1):
                st.header('Finally... the wait is over. Recommended movie is:')
                def make_clickable(link):
                    # target _blank to open new window
                    # extract clickable text to display for your link
                    text = "IMDB Link"
                    return f'<a target="_blank" href="{link}">{text}</a>'

                # IMDB Link is the column with hyperlinks
                recommended_movie['IMDB Link'] = recommended_movie['IMDB Link'].apply(make_clickable)
                recommended_movie = recommended_movie.to_html(escape=False)
                
                # CSS to inject contained in a string
                hide_table_row_index = """
                            <style>
                            thead tr th:first-child {display:none}
                            tbody th {display:none}
                            </style>
                            """

                # Inject CSS with Markdown
                st.markdown(hide_table_row_index, unsafe_allow_html=True)
                
                st.write(recommended_movie, unsafe_allow_html=True)
            else:
                st.header("Couldn't find one suiting your specific taste. Sorry for disappointment. Maybe try a different genre.")
        # If userId is out of range/invalid
        else:
            st.header("Please enter a userId within range.")
    
    
    # Application page for showing the README file for this application
    elif app_mode_main == "See README File":
        readme_text.empty()
        st.markdown(get_file_content_as_string("README_main.md"))
        

# Calling the main() function
if __name__ == "__main__":
    main()
    
    
# References:
# Show Hyperlinks in Streamlit: https://discuss.streamlit.io/t/display-urls-in-dataframe-column-as-a-clickable-hyperlink/743/5
# Pagination in Streamlit: https://gist.github.com/ElisonSherton/0136e8054777e159bd7d387a870e91ed