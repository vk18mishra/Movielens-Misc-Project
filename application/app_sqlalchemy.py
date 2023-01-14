# TO RUN: streamlit run app_sqlalchemy.py

# This is the main app file. This uses Streamlit, which is a python based library, to create the UI. 
# This file is heart of the application. Open the file for furthur understanding and to see the comments.
# TO RUN the application enter **streamlit run app_sqlalchemy.py** in the terminal from the directory this project resides.

# importing the necessary libraries
import streamlit as st
import pickle
from PIL import Image
import pandas as pd
import plotly.graph_objects as go
import urllib
import numpy as np
from sqlalchemy.orm import sessionmaker
from sqlalchemy import func
from database_engine import engine
from stqdm import stqdm
# importing the objects of the tables in the database
from models import Movies
from models import AvgRatingCount
from models import Ratings
from models import Links

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


# Getting all the rows from the ratings table/object where movieId is equal to movieId passed as the arguement (mId)
def ratings_in_chunks_movieId(mId, session):
        same_movie_ratings = pd.read_sql(session.query(Ratings.userId, Ratings.movieId, Ratings.rating).filter(Ratings.movieId == mId).statement, session.bind)
        return same_movie_ratings



# This function is for getting the similarity score between 2 ratings. It's used in the 
# "Similar Users - Better but Slower" part/page of the application
def get_points(rating_1, rating_2):
    diff = abs(rating_1-rating_2)
    if(diff == 0):
        pts = 10
    elif(diff > 0 and diff <= 0.5):
        pts = 8
    elif(diff > 0.5 and diff <= 1.0):
        pts = 6
    elif(diff > 1.0 and diff <= 1.5):
        pts = 5
    elif(diff > 1.5 and diff <= 2.0):
        pts = 4
    elif(diff > 2.0 and diff <= 2.5):
        pts = 3
    elif(diff > 2.5 and diff <= 3.0):
        pts = 2
    elif(diff > 3.0 and diff <= 3.5):
        pts = 1
    elif(diff > 3.5):
        pts = 0
    return(pts)



# This is the function which gets the top 10 similar users according to the similarity scores - Better but Slower Approach
def similar_to_user(uId, session):
    simialar_rating_df = pd.DataFrame(columns=['userId', 'rating'])
    mi = 0
    st.markdown("\nGetting all the movies rated by given user. Be Patient....\n")
    ratings = pd.read_sql(session.query(Ratings.userId, Ratings.movieId, Ratings.rating).filter(Ratings.userId == uId).statement, session.bind)
    st.markdown("\nSearching for all the users, who have rated the same movies as User:\n\n")
    for mId in stqdm(ratings['movieId'].values):
        mi = mi + 1
        same_movie_ratings_mId = ratings_in_chunks_movieId(mId, session)
        simialar_rating_df = pd.concat([simialar_rating_df, same_movie_ratings_mId])
    grouped_multiple = simialar_rating_df.groupby(['userId'])
    per_50 = np.floor((len(ratings)/100)*50)
    grouped_multiple = grouped_multiple.filter(lambda x: len(x) > per_50)
    grouped_multiple = grouped_multiple.groupby(['userId'])
    holy_grail = pd.DataFrame(columns=['userId', 'similarity'])
    st.markdown("\nNow getting similarity scores on all those users:\n\n")
    for uIds in stqdm(grouped_multiple.groups.keys()):
        if(uId == uIds):
            continue
        df_uId = grouped_multiple.get_group(uIds)
        n = 0
        cum_pts = 0
        for mId in df_uId.values:
            our_rating = ratings.loc[ratings['movieId'] == mId[2]]
            pts = get_points(our_rating.iloc[0]['rating'], df_uId.iloc[n]['rating'])
            n = n + 1
            cum_pts = cum_pts + pts

        holy_grail.loc[len(holy_grail.index)] = [uIds, cum_pts]
    return (holy_grail.nlargest(11, 'similarity'))



# This is the function which gets the top 10 similar users according to the 
# number of movies in common and difference in average rating from the input userId - Faster Approach
def similar_to_user_faster(uId, session):
    simialar_rating_df = pd.DataFrame(columns=['userId', 'rating'])
    mi = 0
    st.markdown("\nGetting all the movies rated by given user. Be Patient....\n")
    ratings = pd.read_sql(session.query(Ratings.userId, Ratings.movieId, Ratings.rating).filter(Ratings.userId == uId).statement, session.bind)
    st.markdown("\nSearching for all the users, who have rated the same movies as User...\n\n")
    for mId in stqdm(ratings['movieId'].values):
        mi = mi + 1
        same_movie_ratings_mId = ratings_in_chunks_movieId(mId, session)
        simialar_rating_df = pd.concat([simialar_rating_df, same_movie_ratings_mId])
    grouped_multiple = simialar_rating_df.groupby('userId') \
       .agg(num_commom_movies=('userId', 'size'), diff_in_mean_rating=('rating', 'mean')) \
       .reset_index()
    
    mean_our_user = ratings['rating'].mean()
    grouped_multiple['diff_in_mean_rating'] = grouped_multiple['diff_in_mean_rating'] - mean_our_user
    grouped_multiple['diff_in_mean_rating'] = grouped_multiple['diff_in_mean_rating'].abs()
    grouped_multiple = grouped_multiple.sort_values(by=['num_commom_movies', 'diff_in_mean_rating'], ascending=[False, True])

    return (grouped_multiple.head(11), ratings['movieId'].values)


# This function is used for recommeding a movie to the user based on his/her preferred genre
# This works by getting the top 10 similar users using the "faster approach" method. 
# Then we recommend a movie not seen previously by our user, and in their preferred genre,
# using these top similar users watched movies.
def recommendation_movie(top10_similar_users, movies_watched, uId, session, genre, genre1):
    flag = 0
    st.markdown("\nGetting a movie that top 10 users similar to you have watched but you haven't...\n\n")
    for uIds in stqdm(top10_similar_users.userId.values):
        if(uIds == uId):
            continue
        movies_userI = pd.read_sql(session.query(Ratings.userId, Ratings.movieId, Ratings.rating).filter(Ratings.userId == uIds).statement, session.bind)
        movies_userI = movies_userI.sort_values(by='rating', ascending=False)
        for movies_uI in movies_userI.values:
            if((movies_uI[1] not in movies_watched)):
                movie_title_link = pd.read_sql(session.query(Movies, Links).filter(Movies.movieId == Links.movieId).filter(func.lower(Movies.genres).like(genre)).filter(Movies.movieId == movies_uI[1]).statement, session.bind)
                genre_mv = movie_title_link['genres'].values
                if(len(genre_mv) > 0):
                    if(genre1 in genre_mv[0].lower()):
                        flag = 1
                        break
        if(flag == 1):
            break
    if(flag == 1):
        movie_title_link['imdbId'] = 'https://www.imdb.com/title/tt' + movie_title_link['imdbId'].astype(str)
        movie_title_link = movie_title_link.drop(['movieId_1', 'tmdbId'], axis=1)
        movie_title_link.columns = ['Movie Id', 'Movie Title', 'Genres', 'IMDB Link']
        return movie_title_link
    else:
        movie_title_link = pd.DataFrame(columns = ['Movie Id', 'Movie Title', 'Genres', 'IMDB Link'])
        return movie_title_link



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
                                     "Top 10 Most Similar Users(Faster Version)", "Top 10 Most Similar Users(Slower Version)",
                                     "Recommend a Movie", "See README File"])
    
    
    
    # For going back to the homepage
    if app_mode_main == "Show instructions":
        st.sidebar.success('Choose the preferred option from the dropdown')
    
    
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
            data = pd.read_sql(session.query(Movies, Links).filter(Movies.movieId == Links.movieId).filter(func.lower(Movies.title).like(title_alc)).statement, session.bind)
            
            # preparing this returned data to show clickable links
            data['imdbId'] = 'https://www.imdb.com/title/tt' + data['imdbId'].astype(str)
            data = data.drop(['genres', 'movieId_1', 'tmdbId'], axis=1)
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
            if(N_tot>10):
                # N = 10
                if "page" not in st.session_state:
                    st.session_state.page = 0
                last_page = len(data) // N

                # Add a next button and a previous button

                prev, _ ,next = st.columns([4, 15, 4])

                if next.button("Next"):

                    if st.session_state.page + 1 > last_page:
                        st.session_state.page = 0
                    else:
                        st.session_state.page += 1

                if prev.button("Previous"):

                    if st.session_state.page - 1 < 0:
                        st.session_state.page = last_page
                    else:
                        st.session_state.page -= 1

                # Get start and end indices of the next page of the dataframe
                start_idx = st.session_state.page * N 
                end_idx = (1 + st.session_state.page) * N

                # Index into the sub dataframe
                sub_df = data.iloc[start_idx:end_idx]

                fig = go.Figure(
                    data=[
                        go.Table(
                            columnwidth = [0.5,0.8,0.5],
                            header=dict(
                                values=[f"<b>{i}</b>" for i in sub_df.columns.to_list()],
                                fill_color='pink'
                                ),
                            cells=dict(
                                values=sub_df.transpose()
                                )
                            )
                        ]
                    )
                st.plotly_chart(fig, use_container_width=True)
            # If total matches is less than or equal to 10 then just show them normally on one page
            elif(N_tot<=10):
                fig = go.Figure(
                    data=[
                        go.Table(
                            columnwidth = [0.5,0.8,0.5],
                            header=dict(
                                values=[f"<b>{i}</b>" for i in data.columns.to_list()],
                                fill_color='pink'
                                ),
                            cells=dict(
                                values=data.transpose()
                                )
                            )
                        ]
                    )
                st.plotly_chart(fig, use_container_width=True)
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
        data = pd.read_sql(session.query(Movies, Links).filter(Movies.movieId == Links.movieId).statement, session.bind)

        # preparing this returned data to show clickable links
        data['imdbId'] = 'https://www.imdb.com/title/tt' + data['imdbId'].astype(str)
        data = data.drop(['genres', 'movieId_1', 'tmdbId'], axis=1)
        data.columns = ['Movie Id', 'Movie Title', 'IMDB Link']
        # method to create clickable hyperlinks
        def create_link(url:str) -> str:
            return f'''<a href="{url}">🔗</a>'''

        data['IMDB Link'] = [create_link(url) for url in data["IMDB Link"]]


        # Starting Pagination for our lists of movies
        last_page = len(data) // N

        # Add a next button and a previous button

        prev, _ ,next = st.columns([4, 15, 4])

        if next.button("Next"):

            if st.session_state.page + 1 > last_page:
                st.session_state.page = 0
            else:
                st.session_state.page += 1

        if prev.button("Previous"):

            if st.session_state.page - 1 < 0:
                st.session_state.page = last_page
            else:
                st.session_state.page -= 1

        # Get start and end indices of the next page of the dataframe
        start_idx = st.session_state.page * N 
        end_idx = (1 + st.session_state.page) * N

        # Index into the sub dataframe
        sub_df = data.iloc[start_idx:end_idx]

        fig = go.Figure(
            data=[
                go.Table(
                    columnwidth = [0.5,0.8,0.5],
                    header=dict(
                        values=[f"<b>{i}</b>" for i in sub_df.columns.to_list()],
                        fill_color='pink'
                        ),
                    cells=dict(
                        values=sub_df.transpose()
                        )
                    )
                ]
            )
        st.plotly_chart(fig, use_container_width=True)
    
    
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

        # Getting the wordcloud/circlify image based on these genres. This was created in the Super Bonus subtask.
        # Please refer Super Bonus subtask for how it was made.
        circlify_wordcloud_genres = Image.open('circlify_wordcloud_genres.jpg')

        # drop down to select the genre
        genre = st.selectbox(
            'Choose a genre from the dropdown',
            list_genres)

        st.write('You selected:', genre)
        st.markdown('\n\n')

        genre = genre.lower()
        genre = '%'+genre+'%'
        
        # Main Query to get the top 10 movies in the selected genre using AvgRatingCount and Movies table.
        data = pd.read_sql(session.query(Movies, AvgRatingCount).filter(func.lower(Movies.genres).like(genre)).filter(Movies.movieId == AvgRatingCount.movieId).statement, session.bind)
        
        data = data.drop('movieId_1', axis=1)
        arr = data.values
        data = pd.DataFrame(arr[np.lexsort((-arr[:, 3], -arr[:, 4]))])
        data.columns = ['Movie Id', 'Movie Title', 'Genres', 'Average Rating', 'Total Ratings']
        st.dataframe(data.head(10), width=2000)

        st.image(circlify_wordcloud_genres, caption='Genres and their frequency (generated by circlify)')   
    
    
    # Application page for showing "Top 10 Most Similar Users(Slower Version)"
    elif app_mode_main == "Top 10 Most Similar Users(Slower Version)":
        readme_text.empty()
        st.header('Get Top 10 Most Similar Users, along with their similarity scores, according to given userId - - Better but Slower Version')
        st.markdown('\n\n')
        
        # Text box for Getting the userId
        uId = st.text_input('Enter a User Id between (1 <= userId <= 162541)', '0')
        # If userId is in range/valid - Our task starts
        if(int(uId) >= 1 and int(uId) <= 162541):
            st.write('You\'re looking for top 10 similar users for: ', uId)
            top10_similar_users = similar_to_user(uId, session)
            st.markdown('\n')
            st.header('Finally... the wait is over. Below are the top 10 most similar users:')
            st.dataframe(top10_similar_users)
        # If userId is out of range/invalid
        else:
            st.header("Please enter a userId within range.")
    
    
    # Application page for showing "Top 10 Most Similar Users(Faster Version)"
    elif app_mode_main == "Top 10 Most Similar Users(Faster Version)":
        readme_text.empty()
        st.header('Get Top 10 Most Similar Users, based on number of common movies and difference in mean rating, to given userId - - Faster Version')
        st.markdown('\n\n')
        
        # Text box for Getting the userId
        uId = st.text_input('Enter a User Id between (1 <= userId <= 162541)', '0')
        # If userId is in range/valid - Our task starts
        if(int(uId) >= 1 and int(uId) <= 162541):
            st.write('You\'re looking for top 10 similar users for: ', uId)
            top10_similar_users, notImportant = similar_to_user_faster(uId, session)
            st.markdown('\n')
            st.header('Finally... the wait is over. Below are the top 10 most similar users:')
            st.caption("**_First_ _row_ _has_ _num_ _movies_ _rated_ _by_ _input_ _user_**")
            st.dataframe(top10_similar_users)
        # If userId is out of range/invalid
        else:
            st.header("Please enter a userId within range.")
    
    
    # Application page for "Recommending a Movie"
    elif app_mode_main == "Recommend a Movie":
        readme_text.empty()
        st.header('Movie Recommendation to a user based on their preferred Genre and what similar users have watched')
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

        genre = genre.lower()
        genre1 = genre
        genre = '%'+genre+'%'
        
        st.markdown('\n\n')
        # Text box for Getting the userId
        uId = st.text_input('Enter a User Id between (1 <= userId <= 162541)', '0')
        
        # If userId is in range/valid - Our task starts
        if(int(uId) >= 1 and int(uId) <= 162541):
            st.write('You\'re looking for top 10 similar users for: ', uId)
            top10_similar_users , movies_watched = similar_to_user_faster(uId, session)
            recommended_movie = recommendation_movie(top10_similar_users.head(11), movies_watched, uId, session, genre, genre1)
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