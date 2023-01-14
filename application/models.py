# This file imports the MySQL Tables into python as Objects using SQLAlchemy.
# There are 4 Tables:
# 1. Movies : For movies.csv
# 2. Links : For links.csv
# 3. Ratings : For ratings.csv
# 4. AvgRatingCount : Table made from joining Movies and Links. It contains Average Rating and Rating Count for each MovieId. 

from sqlalchemy import *
from sqlalchemy.ext.declarative import declarative_base
from database_engine import engine

# Connecting to Database Engine through importing and using database_engine.py
Base = declarative_base(engine)

# Creating Object named "Movies" for 'movies' table in the database
class Movies(Base):
    """
    fields: movieId, title, genres
    """
    __tablename__ = 'movies'
    __table_args__ = {'autoload': True}

# Creating Object named "Links" for 'links' table in the database
class Links(Base):
    """
    fields: movieId, imdbId, tmdbId
    """
    __tablename__ = 'links'
    __table_args__ = {'autoload': True}

# Creating Object named "Ratings" for 'ratings' table in the database
class Ratings(Base):
    """
    fields: userId, movieId, rating
    """
    __tablename__ = 'ratings'
    __table_args__ = {'autoload': True}

# Creating Object named "AvgRatingCount" for 'avg_rating_count' table in the database
class AvgRatingCount(Base):
    """
    fields: movieId, rating, rating_count
    """
    __tablename__ = 'avg_rating_count'
    __table_args__ = {'autoload': True}