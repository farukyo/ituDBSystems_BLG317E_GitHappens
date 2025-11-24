SELECT * FROM githappens.genres;

CREATE TABLE genres (
    genreId INT PRIMARY KEY,
    genre VARCHAR(50),
    description VARCHAR(100)
);

LOAD DATA LOCAL INFILE 'C:/Users/faruk/Desktop/Code/ituDBSystems_BLG317E_GitHappens/data/genres.csv'
INTO TABLE genres
FIELDS TERMINATED BY ',' 
ENCLOSED BY '"' 
LINES TERMINATED BY '\r\n'
IGNORE 1 LINES
(genreId, genre, description)