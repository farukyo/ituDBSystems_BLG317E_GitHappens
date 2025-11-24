CREATE TABLE crew (
    titleId VARCHAR(20),
    directors VARCHAR(100),
    writers VARCHAR(100)
);

LOAD DATA LOCAL INFILE 'C:/Users/faruk/Desktop/Code/ituDBSystems_BLG317E_GitHappens/data/crew.csv'
INTO TABLE crew
FIELDS TERMINATED BY ',' 
ENCLOSED BY '"' 
LINES TERMINATED BY '\r\n'
IGNORE 1 LINES
(titleId, @v_directors, @v_writers) -- Kontrol için değişkenlere alıyoruz
SET 
    directors = NULLIF(@v_directors, '0'), -- '0' gelirse NULL yap
    writers = NULLIF(@v_writers, '0');     -- '0' gelirse NULL yap
