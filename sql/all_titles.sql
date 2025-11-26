-- =============================================
-- ALL_TITLES TABLE (Çatı Tablo)
-- movieId – seriesId – titleId bağlantısı için gerekli
-- =============================================

CREATE TABLE all_titles ( 
    titleId VARCHAR(20) PRIMARY KEY 
);

-- Movies verilerini yükle
LOAD DATA LOCAL INFILE 'movies.csv'
INTO TABLE all_titles 
FIELDS TERMINATED BY ',' 
ENCLOSED BY '"' 
LINES TERMINATED BY '\n' 
IGNORE 1 ROWS
(titleId, @dummy, @dummy, @dummy, @dummy, @dummy, @dummy);

-- Series verilerini yükle
LOAD DATA LOCAL INFILE 'series.csv'
INTO TABLE all_titles 
FIELDS TERMINATED BY ',' 
ENCLOSED BY '"' 
LINES TERMINATED BY '\n' 
IGNORE 1 ROWS
(titleId, @dummy, @dummy, @dummy, @dummy, @dummy, @dummy, @dummy);
