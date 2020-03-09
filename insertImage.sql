DELIMITER //
DROP PROCEDURE IF EXISTS insertImage //

CREATE PROCEDURE insertImage(IN p_description VARCHAR(255), IN p_path VARCHAR(255), IN p_owner INT )
BEGIN
    INSERT INTO images(description, owner) VALUES (p_description, p_owner);
    SET @lastId = LAST_INSERT_ID();
    set @imPath = CONCAT(p_path,"/",CAST(@lastId AS CHAR));
    UPDATE images
        SET path = @imPath
    WHERE imageId = @lastId;
END //
DELIMITER ;
