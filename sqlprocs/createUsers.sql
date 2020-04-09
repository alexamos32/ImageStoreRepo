DROP TABLE IF EXISTS users;
CREATE TABLE users (
  userId           INT             NOT NULL    AUTO_INCREMENT,
  username varchar(50) NOT NULL,
  profileImage BOOLEAN       DEFAULT 0,
  profileType VARCHAR(5)     DEFAULT NULL,
  PRIMARY KEY (userId)
);
