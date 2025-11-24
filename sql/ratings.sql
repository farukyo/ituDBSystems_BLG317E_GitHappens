CREATE TABLE ratings (
    titleId VARCHAR(20),
    averageRating DECIMAL(3,1), -- 5.7, 8.1 gibi değerler için
    numVotes INT
);

LOAD DATA LOCAL INFILE 'C:/Users/faruk/Desktop/Code/ituDBSystems_BLG317E_GitHappens/data/ratings.csv'
INTO TABLE ratings
FIELDS TERMINATED BY ',' 
ENCLOSED BY '"' 
LINES TERMINATED BY '\r\n'
IGNORE 1 LINES
(titleId, averageRating, numVotes)