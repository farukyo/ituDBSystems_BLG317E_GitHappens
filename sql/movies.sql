CREATE TABLE movies (
    movieId VARCHAR(20),
    titleType VARCHAR(20),
    primaryTitle VARCHAR(500),
    isAdult INT,
    startYear INT,
    runtimeMinutes INT,
    genre VARCHAR(20)
);

LOAD DATA LOCAL INFILE 'C:/Users/faruk/Desktop/Code/ituDBSystems_BLG317E_GitHappens/data/movies.csv'
INTO TABLE movies
FIELDS TERMINATED BY ',' 
ENCLOSED BY '"' 
LINES TERMINATED BY '\r\n'
IGNORE 1 LINES
(movieId, titleType, primaryTitle, isAdult, @v_startYear, @v_runtimeMinutes, genres)
SET 
    startYear = NULLIF(@v_startYear, '0'),
    runtimeMinutes = NULLIF(@v_runtimeMinutes, '0');