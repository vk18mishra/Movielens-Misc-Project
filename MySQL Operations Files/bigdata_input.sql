LOAD DATA INFILE 'C:/ProgramData/MySQL/MySQL Server 8.0/Uploads/ratings.csv' INTO TABLE movielens_db.ratings
FIELDS TERMINATED BY ',' 
ENCLOSED BY '"' 
LINES TERMINATED BY '\r\n'
IGNORE 1 LINES
(@vuserId, @vmovieId, @vrating, @vtimestamp)
SET
userId = NULLIF(@vuserId,''),
movieId = NULLIF(@vmovieId,''),
rating = NULLIF(@vrating,''),
timestamp = NULLIF(@vtimestamp,'') ;