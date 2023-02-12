# This function is used for recommeding a movie to the user based on his/her preferred genre
# This works by getting the top 10 similar users using the "faster approach" method. 
import pandas as pd
from stqdm import stqdm
import streamlit as st
import numpy as np
from models import Ratings
from models import MoviesNew
from models import Links

# Then we recommend a movie not seen previously by our user, and in their preferred genre,
# using these top similar users watched movies.
def recommendation_movie(top10_similar_users, movies_watched, uId, session, genre):
    flag = 0
    st.markdown("\nGetting a movie that top 10 users similar to you have watched but you haven't...\n\n")
    for uIds in stqdm(top10_similar_users.userId.values):
        if(uIds == uId):
            continue
        movies_userI = pd.read_sql(session.query(Ratings.userId, Ratings.movieId, Ratings.rating).filter(Ratings.userId == uIds).statement, session.bind)
        movies_userI = movies_userI.sort_values(by='rating', ascending=False)
        for movies_uI in movies_userI.values:
            if((movies_uI[1] not in movies_watched)):
                movie_title_link = pd.read_sql(session.query(MoviesNew, Links).filter(MoviesNew.movieId == Links.movieId).filter(MoviesNew.__table__.c[genre].like(1)).filter(MoviesNew.movieId == movies_uI[1]).statement, session.bind)
                genre_mv = movie_title_link['movieId'].values
                if(len(genre_mv) > 0):
                    # if(genre1 in genre_mv[0].lower()):
                    flag = 1
                    break
        if(flag == 1):
            break
    if(flag == 1):
        movie_title_link['imdbId'] = 'https://www.imdb.com/title/tt' + movie_title_link['imdbId'].astype(str)
        movie_title_link.drop(movie_title_link.columns.difference(['movieId','title', genre, 'imdbId']), 1, inplace=True)
        # movie_title_link = movie_title_link.drop(['movieId_1', 'tmdbId'], axis=1)
        movie_title_link.columns = ['Movie Id', 'Movie Title', genre, 'IMDB Link']
        return movie_title_link
    else:
        movie_title_link = pd.DataFrame(columns = ['Movie Id', 'Movie Title', genre, 'IMDB Link'])
        return movie_title_link
