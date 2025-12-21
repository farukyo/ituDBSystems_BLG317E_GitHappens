---- ek data düzenlemeleri –-
-- Profession normalize etmek için

-- # bckup 

CREATE TABLE profession_backup AS
SELECT * FROM profession;

-- # profession sözlük tablosu oluştur

CREATE TABLE profession_dictionary (
    id INT AUTO_INCREMENT PRIMARY KEY,
    name VARCHAR(255) UNIQUE
);

-- # mevcutları sözlüğe taşı

INSERT IGNORE INTO profession_dictionary (name)
WITH RECURSIVE profession_split AS (
    SELECT
        professionId,
        TRIM(SUBSTRING_INDEX(professionName, ',', 1)) AS profession,
        SUBSTRING(professionName, LENGTH(SUBSTRING_INDEX(professionName, ',', 1)) + 2) AS remainder
    FROM profession
    WHERE professionName IS NOT NULL
      AND professionName != ''
      AND professionName NOT LIKE '%\\N%'

    UNION ALL

    SELECT
        professionId,
        TRIM(SUBSTRING_INDEX(remainder, ',', 1)),
        SUBSTRING(remainder, LENGTH(SUBSTRING_INDEX(remainder, ',', 1)) + 2)
    FROM profession_split
    WHERE remainder != ''
)
SELECT DISTINCT profession
FROM profession_split
WHERE profession != '';




-- # profession_assignments tablosu 

CREATE TABLE profession_assignments (
    peopleId VARCHAR(20),
    profession_dict_id INT,

    PRIMARY KEY (peopleId, profession_dict_id),

    FOREIGN KEY (peopleId)
        REFERENCES people(peopleId)
        ON DELETE CASCADE
        ON UPDATE CASCADE,

    FOREIGN KEY (profession_dict_id)
        REFERENCES profession_dictionary(id)
        ON DELETE CASCADE
        ON UPDATE CASCADE
);

-- # bağlantıları aktar 

INSERT IGNORE INTO profession_assignments (peopleId, profession_dict_id)
WITH RECURSIVE profession_split AS (
    SELECT
        p.peopleId,
        TRIM(SUBSTRING_INDEX(pr.professionName, ',', 1)) AS profession,
        SUBSTRING(
            pr.professionName,
            LENGTH(SUBSTRING_INDEX(pr.professionName, ',', 1)) + 2
        ) AS remainder
    FROM people p
    JOIN profession pr ON p.professionId = pr.professionId
    WHERE pr.professionName IS NOT NULL
      AND pr.professionName != ''
      AND pr.professionName NOT LIKE '%\\N%'

    UNION ALL

    SELECT
        peopleId,
        TRIM(SUBSTRING_INDEX(remainder, ',', 1)),
        SUBSTRING(
            remainder,
            LENGTH(SUBSTRING_INDEX(remainder, ',', 1)) + 2
        )
    FROM profession_split
    WHERE remainder != ''
)
SELECT 
    ps.peopleId,
    d.id
FROM profession_split ps
JOIN profession_dictionary d
  ON d.name = ps.profession
WHERE ps.profession != '';




-- # control 

SELECT p.primaryName, d.name
FROM people p
JOIN profession_assignments pa ON p.peopleId = pa.peopleId
JOIN profession_dictionary d ON pa.profession_dict_id = d.id
LIMIT 20;




-- # update people table and delete profession table

ALTER TABLE people DROP FOREIGN KEY people_ibfk_1;
ALTER TABLE people DROP COLUMN professionId;

DROP TABLE profession;


-- # if you are sure about everything fine than delete backup

DROP TABLE profession_backup;


-- # for user score new column added 

ALTER TABLE users
ADD score INT DEFAULT 0;
