-- =============================================
-- PROFESSION TABLE 
-- =============================================

CREATE TABLE profession ( 
    professionId INT PRIMARY KEY AUTO_INCREMENT, 
    professionName VARCHAR(255) UNIQUE 
);

-- Geçici tablo (unique profession name tutmak için)
CREATE TABLE raw_professions ( 
    temp_professionName VARCHAR(500) 
);

-- names.csv'den profession verilerini çek
LOAD DATA LOCAL INFILE 'names.csv' 
INTO TABLE raw_professions 
FIELDS TERMINATED BY ',' 
ENCLOSED BY '"' 
LINES TERMINATED BY '\n' 
IGNORE 1 ROWS 
(@dummy1, @dummy2, @dummy3, @dummy4, temp_professionName, @dummy5);

-- Unique profession'ları ana tabloya aktar
INSERT IGNORE INTO profession (professionName) 
SELECT DISTINCT temp_professionName 
FROM raw_professions 
WHERE temp_professionName IS NOT NULL 
AND temp_professionName != '\\N' 
AND temp_professionName != '';

-- Geçici tabloyu sil
DROP TABLE raw_professions;


-- =============================================
-- PEOPLE TABLE (names.csv'den oluşturulur)
-- =============================================

-- Geçici tablo (professionId eşleşebilsin diye)
CREATE TABLE temp_people_load ( 
    peopleId VARCHAR(20), 
    primaryName VARCHAR(255), 
    birthYear VARCHAR(10), 
    deathYear VARCHAR(10), 
    professionString VARCHAR(500), 
    knownTitles TEXT 
);

-- names.csv'den geçici tabloya yükle
LOAD DATA LOCAL INFILE 'names.csv' 
INTO TABLE temp_people_load 
FIELDS TERMINATED BY ',' 
ENCLOSED BY '"' 
LINES TERMINATED BY '\n' 
IGNORE 1 ROWS 
(peopleId, primaryName, birthYear, deathYear, professionString, knownTitles);

-- Ana tablo
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

-- Geçici tablodan ana tabloya aktar 
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

-- Geçici tabloyu sil
DROP TABLE temp_people_load;
