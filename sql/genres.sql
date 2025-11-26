-- =============================================
-- GENRES TABLE
-- =============================================

CREATE TABLE genres ( 
    genreId INT PRIMARY KEY, 
    genreName VARCHAR(255), 
    description TEXT 
);

LOAD DATA LOCAL INFILE 'genres.csv'
INTO TABLE genres 
FIELDS TERMINATED BY ',' 
ENCLOSED BY '"' 
LINES TERMINATED BY '\n' 
IGNORE 1 ROWS 
(genreId, genreName, description);