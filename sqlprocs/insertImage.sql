DELIMITER //
DROP PROCEDURE IF EXISTS insertImage //

CREATE PROCEDURE insertImage(IN p_description VARCHAR(255), IN p_path VARCHAR(255), IN p_owner INT, IN p_filetype VARCHAR(5) )
BEGIN
    INSERT INTO images(description, owner, filetype) VALUES (p_description, p_owner, p_filetype);
    SET @lastId = LAST_INSERT_ID();
    set @imPath = CONCAT(p_path,"/",CAST(@lastId AS CHAR(3)));
    UPDATE images
        SET path = @imPath
    WHERE imageId = @lastId;
    SELECT * FROM images WHERE imageId=@lastId;
END //
DELIMITER ;
