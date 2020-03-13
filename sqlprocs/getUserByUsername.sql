DELIMITER //
DROP PROCEDURE IF EXISTS getUserByUsername//

CREATE PROCEDURE getUserByUsername(IN p_username VARCHAR(50))
BEGIN
    SELECT * FROM users WHERE username = p_username;
END //
DELIMITER ;
