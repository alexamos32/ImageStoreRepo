DELIMITER //
DROP PROCEDURE IF EXISTS getImages //

CREATE PROCEDURE getImages(IN userId INT)
BEGIN
    SELECT * FROM images 
        WHERE owner = userId;
END//
DELIMITER ;