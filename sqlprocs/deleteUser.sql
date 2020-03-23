DELIMITER //
DROP PROCEDURE IF EXISTS deleteUser//

CREATE PROCEDURE deleteUser(IN p_userId INT)
BEGIN
    DELETE FROM images  where owner=p_userId;
    DELETE FROM users where userId=p_userId;
END//
DELIMITER ;
