-- =============================================
-- EPISODE TABLE
-- =============================================

CREATE TABLE Episode ( 
    episodeId VARCHAR(20) PRIMARY KEY, 
    seriesId VARCHAR(20) NOT NULL, 
    epNumber INT, 
    seNumber INT, 
    runtimeMinutes INT, 
    epTitle VARCHAR(512), 

    FOREIGN KEY (seriesId) 
    REFERENCES Series(seriesId) 
    ON DELETE CASCADE ON UPDATE CASCADE 
);

LOAD DATA LOCAL INFILE 'episodes.csv'
INTO TABLE Episode
FIELDS TERMINATED BY ','
ENCLOSED BY '"'
LINES TERMINATED BY '\n'
IGNORE 1 ROWS
(episodeId, @dummy_type, epTitle, @dummy_adult, @dummy_startyear, @dummy_endyear, runtimeMinutes, @dummy_genres, seriesId, seNumber, epNumber);