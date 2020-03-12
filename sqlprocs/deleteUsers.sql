DELIMITER //
DROP PROCEDURE IF EXISTS insertUser //

CREATE PROCEDURE deleteUser(IN p_username VARCHAR(50))
BEGIN
	DELETE FROM images WHERE username=p_username;
	DELETE FROM users WHERE username=p_username; 
END //
DELIMITER ;
