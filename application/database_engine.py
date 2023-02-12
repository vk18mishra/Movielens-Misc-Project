# This contains the connection string for our database, which is, MySQL.
# Change this file appropriately when using your own database. 

from sqlalchemy import create_engine

# Define the connection string
url = 'mysql+mysqldb://root:12081997@127.0.0.1/movielens_db'

# Create SQLALchemy Database Engine
engine = create_engine(url)