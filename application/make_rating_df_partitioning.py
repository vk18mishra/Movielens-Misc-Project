# This file makes the 'rating_df.pkl' file which contains Average Rating and Rating Count 
# for each MovieId. Now this pkl file is used to load 'avg_rating_count' table in the database, 
# of which 'AvgRatingCount' object is made of. It uses Movies and Ratings object to do that.
# This file only needs to be executed in case of an update in the 'ratings' table.



from models import Ratings
from sqlalchemy import and_, or_, not_
from sqlalchemy import func
import pandas as pd
from tqdm import tqdm
from models import Ratings
from models import Movies
from sqlalchemy.orm import sessionmaker
from database_engine import engine
from sqlalchemy import MetaData

def load_session():
    Session = sessionmaker(bind=engine)
    session = Session()
    return session

def ratings_in_chunks_movieId(mId, session):
        ratings = pd.read_sql(session.query(Ratings.movieId, Ratings.rating).filter(Ratings.movieId == mId).statement, session.bind)
        avg_rating = ratings['rating'].mean()
        rating_cnt = len(ratings)
        dict_rating = {'movieId':mId, 'rating':avg_rating, 'rating_count':rating_cnt}
        return dict_rating

def get_max_min_movieId(session):
    movie_max_min = pd.read_sql(session.query(func.max(Movies.movieId), func.min(Movies.movieId)).statement, session.bind)
    max_mId = movie_max_min.iloc[0]['max_1']
    min_mId = movie_max_min.iloc[0]['min_1']
    mIds = pd.read_sql(session.query(Movies.movieId).statement, session.bind)
    mId_list = list(mIds['movieId'])
    return (max_mId, min_mId, mId_list)



def avgrating_count_by_movie(max_mId, min_mId, mId_list, session):
    dict_rating_list = []
    mi = 0
    print("Finding Average Rating and Rating Count for each movieId: ")
    for mId in tqdm(mId_list):
        mi = mi + 1
        dict_rating = ratings_in_chunks_movieId(mId, session)
        dict_rating_list.append(dict_rating)
    rating_df = pd.DataFrame(dict_rating_list, columns = ['movieId', 'rating', 'rating_count'])
    return (rating_df)

session = load_session()
max_mId, min_mId, mId_list = get_max_min_movieId(session)
rating_df = avgrating_count_by_movie(max_mId, min_mId, mId_list, session)
rating_df.to_pickle("./rating_df.pkl")

