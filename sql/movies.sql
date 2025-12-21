-- =============================================
-- MOVIES TABLE
-- =============================================

-- Ana tablo
CREATE TABLE movies ( 
    movieId VARCHAR(20) PRIMARY KEY, 
    movieTitle VARCHAR(512) NOT NULL, 
    titleType VARCHAR(50), 
    startYear INT, 
    runtimeMinutes INT, 
    isAdult BOOLEAN,

    CONSTRAINT fk_movies_parent FOREIGN KEY (movieId) REFERENCES all_titles(titleId) 
    ON DELETE CASCADE ON UPDATE CASCADE 
);

-- Ara tablo 
CREATE TABLE Movie_Genres ( 
    movieId VARCHAR(20), 
    genreId INT, 

    PRIMARY KEY (movieId, genreId), 
    
    FOREIGN KEY (movieId) REFERENCES Movies(movieId) 
    ON DELETE CASCADE, 

    FOREIGN KEY (genreId) REFERENCES Genres(genreId) 
    ON DELETE CASCADE 
);

-- Geçici tablo
CREATE TABLE temp_movies_load ( 
    movieId VARCHAR(20), 
    titleType VARCHAR(50), 
    movieTitle VARCHAR(512), 
    isAdult VARCHAR(10), 
    startYear VARCHAR(10), 
    runtimeMinutes VARCHAR(10), 
    genres_string TEXT 
);

-- CSV'den geçici tabloya yükle
LOAD DATA LOCAL INFILE 'movies.csv'
INTO TABLE temp_movies_load
FIELDS TERMINATED BY ',' 
ENCLOSED BY '"' 
LINES TERMINATED BY '\n'
IGNORE 1 ROWS
(movieId, titleType, movieTitle, isAdult, startYear, runtimeMinutes, genres_string);

-- Geçici tablodan ana tabloya aktar
INSERT INTO Movies (movieId, movieTitle, titleType, startYear, runtimeMinutes, isAdult) 
SELECT 
    movieId, 
    movieTitle, 
    titleType, 
    NULLIF(startYear, '\\N'), 
    NULLIF(runtimeMinutes, '\\N'), 
    IF(isAdult = '1', TRUE, FALSE) 
FROM temp_movies_load;

-- Genre ilişkilerini ara tabloya ekle 
INSERT IGNORE INTO Movie_Genres (movieId, genreId)
WITH RECURSIVE genre_split AS (
    --  İlk parçayı al 
    SELECT 
        movieId,
        SUBSTRING_INDEX(genres_string, ',', 1) AS genreId_raw,
        SUBSTRING(genres_string, LENGTH(SUBSTRING_INDEX(genres_string, ',', 1)) + 2) AS remainder
    FROM temp_movies_load
    WHERE genres_string IS NOT NULL AND genres_string != '' AND genres_string NOT LIKE '%\\N%'
    
    UNION ALL
    
    -- Kalan parçaları döngüyle al (Recursive Case)
    SELECT 
        movieId,
        SUBSTRING_INDEX(remainder, ',', 1),
        SUBSTRING(remainder, LENGTH(SUBSTRING_INDEX(remainder, ',', 1)) + 2)
    FROM genre_split
    WHERE remainder != ''
)
--  Temizle ve kaydet
SELECT movieId, CAST(genreId_raw AS UNSIGNED) 
FROM genre_split
WHERE genreId_raw != '';

-- Geçici tabloyu sil
DROP TABLE temp_movies_load;