-- =============================================
-- SERIES TABLE
-- =============================================

-- Ana tablo
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

-- Ara tablo (Many-to-Many ilişki)
CREATE TABLE Series_Genres ( 
    seriesId VARCHAR(20), 
    genreId INT, 

    PRIMARY KEY (seriesId, genreId), 

    FOREIGN KEY (seriesId) REFERENCES Series(seriesId) 
    ON DELETE CASCADE, 

    FOREIGN KEY (genreId) REFERENCES Genres(genreId) 
    ON DELETE CASCADE 
);

-- Geçici tablo (veri yükleme için)
CREATE TABLE temp_series_load ( 
    seriesId VARCHAR(20), 
    titleType VARCHAR(50), 
    seriesTitle VARCHAR(512), 
    isAdult VARCHAR(10), 
    startYear VARCHAR(10), 
    runtimeMinutes VARCHAR(10),
    genres_string TEXT
);

-- CSV'den geçici tabloya yükle
LOAD DATA LOCAL INFILE 'series.csv'
INTO TABLE temp_series_load
FIELDS TERMINATED BY ','
ENCLOSED BY '"'
LINES TERMINATED BY '\n'
IGNORE 1 ROWS
(seriesId, titleType, seriesTitle, isAdult, startYear, runtimeMinutes, genres_string);

-- Hata alırsan INSERT INTO Series'den önce bu komutu çalıştır:
-- INSERT IGNORE INTO all_titles (titleId)
-- SELECT seriesId 
-- FROM temp_series_load
-- WHERE seriesId IS NOT NULL AND seriesId != '';

-- Geçici tablodan ana tabloya aktar
INSERT INTO Series (seriesId, seriesTitle, titleType, startYear, runtimeMinutes, isAdult)
SELECT 
    seriesId, 
    seriesTitle, 
    titleType, 
    NULLIF(startYear, '\\N'), 
    NULLIF(runtimeMinutes, '\\N'),
    IF(isAdult = '1', TRUE, FALSE)
FROM temp_series_load;

-- Genre ilişkilerini ara tabloya ekle (recursive CTE ile virgülle ayrılmış değerleri parse et)
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

-- Geçici tabloyu sil
DROP TABLE temp_series_load;
