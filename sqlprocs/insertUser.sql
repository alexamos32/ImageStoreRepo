DELIMITER //
DROP PROCEDURE IF EXISTS insertUser //

CREATE PROCEDURE insertUser(IN p_username VARCHAR(50))
BEGIN
    INSERT INTO users(username) VALUES (p_username);
END //
DELIMITER ;