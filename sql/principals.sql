-- =============================================
-- PRINCIPALS TABLE
-- Bileşik anahtar (composite key) kullanıldı
-- =============================================

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

LOAD DATA LOCAL INFILE 'principals.csv' 
INTO TABLE principals 
FIELDS TERMINATED BY ',' 
ENCLOSED BY '"' 
LINES TERMINATED BY '\n' 
IGNORE 1 ROWS 
(titleId, @dummy_ordering, peopleId, category, job, characters) 
SET job = NULLIF(job, '\\N'), characters = NULLIF(characters, '\\N');