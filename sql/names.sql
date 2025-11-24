CREATE TABLE names (
    nameId VARCHAR(20),
    primaryName VARCHAR(100),
    birthYear INT,
    deathYear INT,
    profession VARCHAR(255), -- "actor,producer" gibi veriler için
    knownTitles VARCHAR(500) -- "tt001,tt002,tt003..." gibi uzun listeler için
);

-- 2. Veriyi Yükleme
LOAD DATA LOCAL INFILE 'C:/Users/faruk/Desktop/Code/ituDBSystems_BLG317E_GitHappens/data/names.csv'
INTO TABLE names
FIELDS TERMINATED BY ',' 
ENCLOSED BY '"' 
LINES TERMINATED BY '\r\n'
IGNORE 1 LINES
(nameId, primaryName, birthYear, deathYear, profession, knownTitles)
