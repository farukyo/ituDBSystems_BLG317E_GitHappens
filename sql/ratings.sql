-- =============================================
-- RATINGS TABLE
-- =============================================

CREATE TABLE ratings ( 
    ratingId INT PRIMARY KEY AUTO_INCREMENT, 
    titleId VARCHAR(20) NOT NULL, 
    averageRating DECIMAL(3, 1), 
    numVotes INT, 

    FOREIGN KEY (titleId) REFERENCES all_titles(titleId) 
    ON DELETE CASCADE ON UPDATE CASCADE 
);

LOAD DATA LOCAL INFILE 'ratings.csv' 
INTO TABLE ratings 
FIELDS TERMINATED BY ',' 
ENCLOSED BY '"' 
LINES TERMINATED BY '\n'
IGNORE 1 ROWS 
(titleId, averageRating, numVotes);