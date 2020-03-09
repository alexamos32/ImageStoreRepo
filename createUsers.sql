DROP TABLE IF EXISTS users;
CREATE TABLE users (
  userId           INT             NOT NULL    AUTO_INCREMENT,
  username varchar(50) NOT NULL,
  PRIMARY KEY (userId)
);
