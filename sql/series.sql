CREATE TABLE series (
    seriesId VARCHAR(20),
    titleType VARCHAR(20),
    primaryTitle VARCHAR(500),
    isAdult INT,
    startYear INT,
    endYear INT,
    runtimeMinutes INT,
    genres VARCHAR(20)
);

LOAD DATA LOCAL INFILE 'C:/Users/faruk/Desktop/Code/ituDBSystems_BLG317E_GitHappens/data/series.csv'
INTO TABLE series
FIELDS TERMINATED BY ',' 
ENCLOSED BY '"' 
LINES TERMINATED BY '\r\n'
IGNORE 1 LINES
(seriesId, titleType, primaryTitle, isAdult, startYear, endYear, runtimeMinutes, genres)
