DELIMITER //
DROP PROCEDURE IF EXISTS deleteImage //

CREATE PROCEDURE deleteImage(IN p_imageId INT)
BEGIN
    SELECT * FROM images
           WHERE imageId = p_imageId;

    DELETE FROM images where imageId = p_imageId;

END//
DELIMITER ;
