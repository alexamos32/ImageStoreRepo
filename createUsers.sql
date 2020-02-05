DROP TABLE IF EXISTS users;
CREATE TABLE users (
  userId           INT             NOT NULL    AUTO_INCREMENT,
  name  varchar(50)    NOT NULL,
  username varchar(30) NOT NULL,
  password varchar(30) NOT NULL,
  PRIMARY KEY (userId)
);