DELIMITER //
DROP PROCEDURE IF EXISTS insertProfileImage //

CREATE PROCEDURE insertProfileImage(IN p_userId INT, IN p_profileType varchar(5))
BEGIN
    UPDATE users SET profileImage=1 , profileType=p_profileType WHERE userId = p_userId;

END //
DELIMITER ;
