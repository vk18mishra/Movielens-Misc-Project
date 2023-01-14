# Readme File for MovieLens Database Application Project

Following is the necessary information explaining different files and their working towards this project.


# Files

##  app_sqlalchemy.py

This is the main app file. This uses Streamlit, which is a python based library, to create the UI. This file is heart of the application. Open the file for furthur understanding and to see the comments.
TO RUN the application enter **streamlit run app_sqlalchemy.py** in the terminal from the directory this project resides.

## database_engine.py

This contains the connection string for our database, which is, MySQL.
Change this file appropriately when using your own database. 

## models .py

This file imports the MySQL Tables into python as Objects using SQLAlchemy.
There are 4 Tables:
1. Movies : Object named "Movies" for 'movies' table in the database
2. Links : Object named "Links" for 'links' table in the databasev
3. Ratings : Object named "Ratings" for 'ratings' table in the database
4. AvgRatingCount : Object named "AvgRatingCount" for 'avg_rating_count' table in the database. Table made from joining Movies and Links. It contains Average Rating and Rating Count for each MovieId. 

## make_rating_df_partitioning.py

This file makes the 'rating_df.pkl' file which contains Average Rating and Rating Count for each MovieId. Now this pkl file is used to load 'avg_rating_count' table in the database, of which 'AvgRatingCount' object is made of. It uses Movies and Ratings object to do that.
This file only needs to be executed in case of an update in the 'ratings' table.

## rating_df.pkl

Actual Pickle file made from above file. Now this file and its data can be loaded into the database in the 'avg_rating_count' table.

## df_genres_main.pkl

It's a small pickle file containing just the list of all the genres.

##  circlify_wordcloud_genres.jpg

It's an circlify image(kind of like a wordcloud) showing number of movies in each genre. This image is displayed on the "Top 10 Movies by Genre" page of the application.

##  creation_time_rating_df.png

It's a screenshot showing how much time it took to make the 'rating_df.pkl' file using 'make_rating_df_partitioning.py' file.
NOTE: It was run on the Core i5 Windows Machine with just 4 GB of RAM.

##  .streamlit/secrets.toml

It contains the database credentials like a connection string. It is used by the streamlit for making the connection of it's own for rendering the UI.
NOTE : It should always be inside the folder named '.streamlit' under the working directory i.e. all the other application files. And it should be of the same name as 'secrets.toml'.
NOTE : Update Database connection variables according to the one you are using.

##  requirements.txt

It contains the required python libraries needed to be installed in order to test and play with this application.

##  __pycache__/

Just a folder containing the compiled/cached python files (above files). It's not important, it just helps to run the application a little faster. You can delete it if you want. Though your Python Interpreter will create it again, when you run the application.