DROP TABLE IF EXISTS images;
CREATE TABLE images (
  imageId    INT             NOT NULL         AUTO_INCREMENT,
  description  varchar(255)    DEFAULT NULL,
  path       varchar(255)    NOT NULL,   
  owner      INT             NOT NULL         REFERENCES users(userId),
  PRIMARY KEY (imageId)
);