DROP TABLE IF EXISTS users;
CREATE TABLE users (
  userId           INT             NOT NULL    AUTO_INCREMENT,
  name  varchar(50)    NOT NULL,
  username varchar(30) NOT NULL,
  password varchar(30) NOT NULL,
  PRIMARY KEY (userId)
);

DELIMITER //
DROP PROCEDURE IF EXISTS addUser//
CREATE DEFINER=`root`@`localhost` PROCEDURE `addUser`(
    IN p_name VARCHAR(50),
    IN p_username VARCHAR(30),
    IN p_password VARCHAR(30)
)
BEGIN
    if ( select exists (select 1 from users where u_username = p_username) ) THEN
     
        select 'Username Exists !!';
     
    ELSE
     
        insert into users
        (
            u_name,
            u_username,
            u_password
        )
        values
        (
            p_name,
            p_username,
            p_password
        );
     
    END IF;
END//
DELIMITER ;
