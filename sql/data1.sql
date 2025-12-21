SET GLOBAL local_infile = 1;

-- !!! önemli ayar değişikliği yapın ki tüm rowları işleyebilelim !!!
-- •  Üst menüden Edit -> Preferences (Mac kullanıyorsan MySQLWorkbench -> Preferences) kısmına git.
-- •  Sol menüden SQL Editor seçeneğine tıkla.
-- •  Sağ tarafta DBMS connection read timeout interval (in seconds) ayarını göreceksin. Orada 30 yazar.
-- •  O sayıyı 600 (10 dakika) veya 6000 yap.
-- •  OK de ve Workbench'i kapatıp tekrar aç.

-- -----genres table – genres.csv------

CREATE TABLE genres ( 
genreId INT PRIMARY KEY, 
genreName VARCHAR(255), 
description TEXT 
);

LOAD DATA LOCAL INFILE 
'genres.csv'
INTO TABLE genres 
FIELDS TERMINATED BY ',' 
ENCLOSED BY '"' 
LINES TERMINATED BY '\n' 
IGNORE 1 ROWS 
(genreId, genreName, description);















-- **** çatı tablo ***
-- *moviesId – seriesId- titleId bağlantısı için gerekli 

CREATE TABLE all_titles ( 
titleId VARCHAR(20) PRIMARY KEY 
);

LOAD DATA LOCAL INFILE 
'/Users/ceydanurakalin/Desktop/son hali hazır datalar/movies.csv'
INTO TABLE all_titles 
FIELDS TERMINATED BY ',' 
ENCLOSED BY '"' 
LINES TERMINATED BY '\n' 
IGNORE 1 ROWS
(titleId, @dummy, @dummy, @dummy, @dummy, @dummy, @dummy);

LOAD DATA LOCAL INFILE 
'/Users/ceydanurakalin/Desktop/son hali hazır datalar/series.csv'
INTO TABLE all_titles 
FIELDS TERMINATED BY ',' 
ENCLOSED BY '"' 
LINES TERMINATED BY '\n' 
IGNORE 1 ROWS
(titleId, @dummy, @dummy, @dummy, @dummy, @dummy, @dummy, @dummy);

-- ** movieId ve seriesId birleşimleri principles.titleId olmalı
-- ** movie.genreId kaldırıldı ara yeni tablo oluşturuldu moviesgenre


-- -----movies – movies.csv ------

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

-- **ara tablo**

CREATE TABLE Movie_Genres ( 
movieId VARCHAR(20), 
genreId INT, 

PRIMARY KEY (movieId, genreId), 
FOREIGN KEY (movieId) REFERENCES Movies(movieId) 
ON DELETE CASCADE, 

FOREIGN KEY (genreId) REFERENCES Genres(genreId) 
ON DELETE CASCADE 
);

-- **geçici tablo**

CREATE TABLE temp_movies_load ( 
movieId VARCHAR(20), 
titleType VARCHAR(50), 
movieTitle VARCHAR(512), 
isAdult VARCHAR(10), 
startYear VARCHAR(10), 
runtimeMinutes VARCHAR(10), 
genres_string TEXT 
);


LOAD DATA LOCAL INFILE 
'movies.csv'
INTO TABLE temp_movies_load
FIELDS TERMINATED BY ',' 
ENCLOSED BY '"' 
LINES TERMINATED BY '\n'
IGNORE 1 ROWS
(movieId, titleType, movieTitle, isAdult, startYear, runtimeMinutes, genres_string);

INSERT INTO Movies (movieId, movieTitle, titleType, startYear, runtimeMinutes, isAdult) SELECT 
movieId, 
movieTitle, 
titleType, 
NULLIF(startYear, '\\N'), 
NULLIF(runtimeMinutes, '\\N'), 
IF(isAdult = '1', TRUE, FALSE) 
FROM temp_movies_load;

INSERT IGNORE INTO Movie_Genres (movieId, genreId)
WITH RECURSIVE genre_split AS (
    -- 1. Adım: İlk parçayı al (Base Case)
    SELECT 
        movieId,
        SUBSTRING_INDEX(genres_string, ',', 1) AS genreId_raw,
        SUBSTRING(genres_string, LENGTH(SUBSTRING_INDEX(genres_string, ',', 1)) + 2) AS remainder
    FROM temp_movies_load
    WHERE genres_string IS NOT NULL AND genres_string != '' AND genres_string NOT LIKE '%\\N%'
    
    UNION ALL
    
    -- 2. Adım: Kalan parçaları döngüyle al (Recursive Case)
    SELECT 
        movieId,
        SUBSTRING_INDEX(remainder, ',', 1),
        SUBSTRING(remainder, LENGTH(SUBSTRING_INDEX(remainder, ',', 1)) + 2)
    FROM genre_split
    WHERE remainder != ''
)
-- 3. Adım: Temizle ve kaydet
SELECT movieId, CAST(genreId_raw AS UNSIGNED) 
FROM genre_split
WHERE genreId_raw != '';



DROP TABLE temp_movies_load;



-- ---- series – series.csv ----
CREATE TABLE series ( 
seriesId VARCHAR(20) PRIMARY KEY, 
seriesTitle VARCHAR(512) NOT NULL, 
titleType VARCHAR(50), 
startYear INT, 
endYear INT, 
runtimeMinutes INT, 
isAdult BOOLEAN, 

CONSTRAINT fk_series_parent FOREIGN KEY (seriesId) REFERENCES all_titles(titleId) 
ON DELETE CASCADE ON UPDATE CASCADE 
);

-- **ara tablo**

CREATE TABLE Series_Genres ( 
seriesId VARCHAR(20), 
genreId INT, 

PRIMARY KEY (seriesId, genreId), 

FOREIGN KEY (seriesId) REFERENCES Series(seriesId) 
ON DELETE CASCADE, 

FOREIGN KEY (genreId) REFERENCES Genres(genreId) 
ON DELETE CASCADE 
);

-- **geçici tablo**

CREATE TABLE temp_series_load ( 
seriesId VARCHAR(20), 
titleType VARCHAR(50), 
seriesTitle VARCHAR(512), 
isAdult VARCHAR(10), 
startYear VARCHAR(10), 
runtimeMinutes VARCHAR(10),
genres_string TEXT
);

LOAD DATA LOCAL INFILE 
'series.csv'
INTO TABLE temp_series_load
FIELDS TERMINATED BY ','
ENCLOSED BY '"'
LINES TERMINATED BY '\n'
IGNORE 1 ROWS
(seriesId, titleType, seriesTitle, isAdult, startYear, runtimeMinutes, genres_string);

-- **hata alırsan insert into series den önce aşağıdaki komutu çalıştır
INSERT IGNORE INTO all_titles (titleId)
SELECT seriesId 
FROM temp_series_load
WHERE seriesId IS NOT NULL AND seriesId != '';


INSERT INTO Series (seriesId, seriesTitle, titleType, startYear, runtimeMinutes, isAdult)
SELECT 
    seriesId, 
    seriesTitle, 
    titleType, 
    NULLIF(startYear, '\\N'), 
    NULLIF(runtimeMinutes, '\\N'),
    IF(isAdult = '1', TRUE, FALSE)
FROM temp_series_load;


INSERT IGNORE INTO Series_Genres (seriesId, genreId)
WITH RECURSIVE genre_split AS (
    -- 1. Adım: İlk parçayı al (Base Case)
    SELECT 
        seriesId,
        SUBSTRING_INDEX(genres_string, ',', 1) AS genreId_raw,
        SUBSTRING(genres_string, LENGTH(SUBSTRING_INDEX(genres_string, ',', 1)) + 2) AS remainder
    FROM temp_series_load
    WHERE genres_string IS NOT NULL AND genres_string != '' AND genres_string NOT LIKE '%\\N%'
    
    UNION ALL
    
    -- 2. Adım: Kalan parçaları döngüyle al (Recursive Case)
    SELECT 
        seriesId,
        SUBSTRING_INDEX(remainder, ',', 1),
        SUBSTRING(remainder, LENGTH(SUBSTRING_INDEX(remainder, ',', 1)) + 2)
    FROM genre_split
    WHERE remainder != ''
)
-- 3. Adım: Temizle ve kaydet
SELECT seriesId, CAST(genreId_raw AS UNSIGNED) 
FROM genre_split
WHERE genreId_raw != '';



DROP TABLE temp_series_load;















-- ---- episode – episodes.csv -----

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


LOAD DATA LOCAL INFILE 
'episodes.csv'
INTO TABLE Episode
FIELDS TERMINATED BY ','
ENCLOSED BY '"'
LINES TERMINATED BY '\n'
IGNORE 1 ROWS
(episodeId, @dummy_type, epTitle, @dummy_adult, @dummy_startyear, @dummy_endyear, runtimeMinutes, @dummy_genres, seriesId, seNumber, epNumber);






















-- -----profession– names.csv------

-- ** geçici bir tablo oluşturmalıyız ki unique professionname tutalım -raw_professions
-- ** arama yaparken where like % kullanılmalı 

CREATE TABLE profession ( 
professionId INT PRIMARY KEY AUTO_INCREMENT, 
professionName VARCHAR(255) UNIQUE 
);

CREATE TABLE raw_professions ( 
temp_professionName VARCHAR(500) 
);

LOAD DATA LOCAL INFILE 
'names.csv' 
INTO TABLE raw_professions 
FIELDS TERMINATED BY ',' 
ENCLOSED BY '"' 
LINES TERMINATED BY '\n' 
IGNORE 1 ROWS 
(@dummy1, @dummy2, @dummy3, @dummy4, temp_professionName, @dummy5);

INSERT IGNORE INTO profession (professionName) 
SELECT DISTINCT temp_professionName 
FROM raw_professions 
WHERE temp_professionName IS NOT NULL 
AND temp_professionName != '\\N' 
AND temp_professionName != '';

DROP TABLE raw_professions;
















-- -----people – names.csv------

-- *** geçici tablo – professionId eşleşebilsin diye***

CREATE TABLE temp_people_load ( 
peopleId VARCHAR(20), 
primaryName VARCHAR(255), 
birthYear VARCHAR(10), 
deathYear VARCHAR(10), 
professionString VARCHAR(500), 
knownTitles TEXT 
);

LOAD DATA LOCAL INFILE 
'names.csv' 
INTO TABLE temp_people_load 
FIELDS TERMINATED BY ',' 
ENCLOSED BY '"' 
LINES TERMINATED BY '\n' 
IGNORE 1 ROWS 
(peopleId, primaryName, birthYear, deathYear, professionString, knownTitles);


CREATE TABLE people ( 
peopleId VARCHAR(20) PRIMARY KEY,
primaryName VARCHAR(255) NOT NULL, 
birthYear INT, 
deathYear INT, 
professionId INT, 

FOREIGN KEY (professionId) 
REFERENCES profession(professionId) 
ON DELETE SET NULL ON UPDATE CASCADE 
);


INSERT INTO people (peopleId, primaryName, birthYear, deathYear, professionId)
SELECT 
    t.peopleId,
    t.primaryName,
   
    NULLIF(t.birthYear, '\\N'),
    NULLIF(t.deathYear, '\\N'),
    p.professionId
FROM 
    temp_people_load t
LEFT JOIN 
    profession p ON t.professionString = p.professionName;



DROP TABLE temp_people_load;


-- ---- ratings – ratings.csv ---- 

CREATE TABLE ratings ( 
ratingId INT PRIMARY KEY AUTO_INCREMENT, 
titleId VARCHAR(20) NOT NULL, 
averageRating DECIMAL(3, 1), 
numVotes INT, 

FOREIGN KEY (titleId) REFERENCES all_titles(titleId) 
ON DELETE CASCADE ON UPDATE CASCADE 
);

LOAD DATA LOCAL INFILE 
'ratings.csv' 
INTO TABLE ratings 
FIELDS TERMINATED BY ',' 
ENCLOSED BY '"' 
LINES TERMINATED BY '\n'
IGNORE 1 ROWS 
(titleId, averageRating, numVotes);



-- ---- principals – principals.csv ---

-- ** bileşik anahtar atadık 

CREATE TABLE principals ( 
titleId VARCHAR(20) NOT NULL, 	
peopleId VARCHAR(20) NOT NULL, 
category VARCHAR(50), 
job VARCHAR(255), 
characters TEXT, 

PRIMARY KEY (titleId, peopleId), 

FOREIGN KEY (titleId) REFERENCES all_titles(titleId) 
ON DELETE CASCADE ON UPDATE CASCADE, 

FOREIGN KEY (peopleId) REFERENCES people(peopleId) 
ON DELETE CASCADE ON UPDATE CASCADE 
);



LOAD DATA LOCAL INFILE 
'principals.csv' 
INTO TABLE principals 
FIELDS TERMINATED BY ',' 
ENCLOSED BY '"' 
LINES TERMINATED BY '\n' 
IGNORE 1 ROWS (titleId, @dummy_ordering, peopleId, category, job, characters) 
SET job = NULLIF(job, '\\N'), characters = NULLIF(characters, '\\N');


























