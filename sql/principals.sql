CREATE TABLE principals (
    titleId VARCHAR(20),
    ordering INT,
    personId VARCHAR(20),
    category VARCHAR(100), -- 'cinematographer' gibi uzun olabiliyor
    job VARCHAR(255),      -- 'director of photography' gibi, '0' gelebiliyor
    characters TEXT        -- JSON formatında ["Self"] geliyor, uzun olabilir
);


LOAD DATA LOCAL INFILE 'C:/Users/faruk/Desktop/Code/ituDBSystems_BLG317E_GitHappens/data/principals.csv'
INTO TABLE principals
FIELDS TERMINATED BY ',' 
ENCLOSED BY '"' 
LINES TERMINATED BY '\r\n'
IGNORE 1 LINES
(titleId, ordering, personId, category, @v_job, @v_characters)
SET 
    -- 'job' ve 'characters' metin olsa da veride boşluk yerine '0' kullanılmış.
    -- Bunları temizlemezsek veritabanında karakter adı "0" olarak kalır.
    job = NULLIF(@v_job, '0'),
    characters = NULLIF(@v_characters, '0');