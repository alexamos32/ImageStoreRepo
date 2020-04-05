DROP TABLE IF EXISTS images;
CREATE TABLE images (
  imageId    INT             NOT NULL         AUTO_INCREMENT,
  description  varchar(255)    DEFAULT NULL,
  path       varchar(255)    DEFAULT NULL,
  owner      INT             NOT NULL         REFERENCES users(userId),
  fileType   VARCHAR(5)      NOT NULL,
  PRIMARY KEY (imageId)
);
