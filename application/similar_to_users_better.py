import pandas as pd
from stqdm import stqdm
import streamlit as st
import numpy as np
from models import Ratings
from sqlalchemy.orm import sessionmaker
from database_engine import engine


# Initialize connection.
# Uses st.experimental_singleton to only run once.
@st.experimental_singleton
def load_session():
    Session = sessionmaker(bind=engine)
    session = Session()
    return session

# This is the function which gets the top 10 similar users according to the similarity scores - Better but Slower Approach
@st.experimental_memo
def similar_to_user(uId):
    # Starting SQLALchemy session
    session = load_session()
    
    simialar_rating_df = pd.DataFrame(columns=['userId', 'movieId', 'rating'])
    mi = 0
    st.markdown("""\n- _Getting all the movies rated by given user..._\n""")
    ratings = pd.read_sql(session.query(Ratings.userId, Ratings.movieId, Ratings.rating).filter(Ratings.userId == uId).statement, session.bind)
    st.markdown("""\n- _Searching for all the users, who have rated the same movies as User:_\n\n""")
    for mId in stqdm(ratings['movieId'].values):
        mi = mi + 1
        same_movie_ratings_mId = pd.read_sql(session.query(Ratings.userId, Ratings.movieId, Ratings.rating).filter(Ratings.movieId == mId).statement, session.bind)
        simialar_rating_df = pd.concat([simialar_rating_df, same_movie_ratings_mId])
    grouped_multiple = simialar_rating_df.groupby(['userId'])
    per_80 = np.floor((len(ratings)/100)*80)
    grouped_multiple = grouped_multiple.filter(lambda x: len(x) > per_80)
    grouped_multiple = grouped_multiple.groupby(['userId'])
    holy_grail = pd.DataFrame(columns=['userId', 'similarity'])
    st.markdown("""\n- _Now getting similarity scores on all those users:_\n\n""")
    for uIds in stqdm(grouped_multiple.groups.keys()):
        if(uId == uIds):
            continue
        df_uId = grouped_multiple.get_group(uIds)
        n = 0
        cum_pts = 0
        for mId in df_uId.values:
            our_rating = ratings.loc[ratings['movieId'] == mId[1]]
            # This function is for getting the similarity score between 2 ratings. It's used in the 
            # "Similar Users - Better but Slower" part/page of the application
            diff = abs(our_rating.iloc[0]['rating']-df_uId.iloc[n]['rating'])
            pts = (5.0 - diff)
            n = n + 1
            cum_pts = cum_pts + pts

        holy_grail.loc[len(holy_grail.index)] = [str(uIds), cum_pts]
    return (holy_grail.nlargest(11, 'similarity'))