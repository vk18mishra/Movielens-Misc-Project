import pandas as pd
import streamlit as st
from sqlalchemy.orm import sessionmaker
from database_engine import engine
from models import AvgRatingCount
from models import MoviesNew

# Initialize connection.
# Uses st.experimental_singleton to only run once.
@st.experimental_singleton
def load_session():
    Session = sessionmaker(bind=engine)
    session = Session()
    return session

@st.experimental_memo
def top_movies_genre(genre):
                # Starting SQLALchemy session
                session = load_session()
                
                data = pd.read_sql(session.query(MoviesNew, AvgRatingCount).filter(MoviesNew.__table__.c[genre] == 1).filter(MoviesNew.movieId == AvgRatingCount.movieId).statement, session.bind)
                
                # Main Query to get the top 10 movies in the selected genre using AvgRatingCount and Movies table.
                # data = pd.read_sql(session.query(MoviesNew, AvgRatingCount).filter(MoviesNew.__table__.c[genre].like(1)).filter(Movies.movieId == AvgRatingCount.movieId).statement, session.bind)
                # data2 = pd.read_sql(session.query(AvgRatingCount).statement, session.bind)
                # data = pd.merge(data1, data2, on='movieId',  how='inner')
                
                data.drop(data.columns.difference(['movieId','title', genre, 'rating', 'rating_count']), 1, inplace=True)
                # data = data.drop('movieId_1', axis=1)
                
                C = (data['rating'] * data['rating_count']).sum() / data['rating_count'].sum()
                
                WR_list = []
                for mv in range(len(data)):
                    R = float(data.iloc[[mv]].rating)
                    v = int(data.iloc[[mv]].rating_count)
                    m = 5000
                    WR = float((v / (v+m)) * R + (m / (v+m)) * C)
                    WR_list.append(WR)
                data['Bayesian_estimate'] = WR_list
                
                data = data.sort_values(by='Bayesian_estimate', ascending=False)
                data.columns = ['Movie Id', 'Movie Title', genre, 'Average Rating', 'Total Ratings', 'Bayesian Estimate']
                
                # CSS to inject contained in a string
                hide_table_row_index = """
                            <style>
                            thead tr th:first-child {display:none}
                            tbody th {display:none}
                            </style>
                            """

                # Inject CSS with Markdown
                st.markdown(hide_table_row_index, unsafe_allow_html=True)
                
                st.table(data.head(10))