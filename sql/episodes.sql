CREATE TABLE episodes (
    episodeId VARCHAR(20) PRIMARY KEY,
    titleType VARCHAR(20),
    primaryTitle VARCHAR(500),
    isAdult INT,
    startYear INT,
    endYear INT,
    runtimeMinutes INT,
    genre VARCHAR(20),
    seriesId VARCHAR(20),
    seasonNumber INT,
    episodeNumber INT
);


LOAD DATA LOCAL INFILE 'C:/Users/faruk/Desktop/Code/ituDBSystems_BLG317E_GitHappens/data/episodes.csv'
INTO TABLE episodes
FIELDS TERMINATED BY ',' 
ENCLOSED BY '"' 
LINES TERMINATED BY '\r\n'
IGNORE 1 LINES
(episodeId, titleType, primaryTitle, isAdult, @v_startYear, @v_endYear, @v_runtimeMinutes, genre, seriesId, @v_seasonNumber, @v_episodeNumber)
SET 
    startYear = NULLIF(@v_startYear, '0'),       -- 0 ise NULL yap
    endYear = NULLIF(@v_endYear, '0'),           -- 0 ise NULL yap
    runtimeMinutes = NULLIF(@v_runtimeMinutes, '0'), -- 0 ise NULL yap
    seasonNumber = NULLIF(@v_seasonNumber, '0'),             -- 0 ise NULL yap
   episodeNumber = NULLIF(@v_episodeNumber, '0');