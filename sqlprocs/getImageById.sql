DELIMITER //
DROP PROCEDURE IF EXISTS getImageById //

CREATE PROCEDURE getImageById(IN p_owner INT, IN p_imageId INT)
BEGIN
    SELECT * FROM images 
        WHERE owner = p_owner
        AND imageId = p_imageId;
END//
DELIMITER ;