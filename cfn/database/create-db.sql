
BEGIN;

CREATE TABLE company (
                         id VARCHAR(36) NOT NULL,
                         name VARCHAR(30) NOT NULL,
                         type VARCHAR(10),
                         siret VARCHAR(14),
                         address VARCHAR(300),
                         zip_code VARCHAR(10),
                         country_code VARCHAR(2),
                         phone_number VARCHAR(20),
                         email VARCHAR(64) NOT NULL,
                         contact_fname VARCHAR(20),
                         contact_lname VARCHAR(20),
                         url VARCHAR(128),
                         arn_key VARCHAR(12),
                         offer VARCHAR(10) NOT NULL,
                         max_zone INTEGER NOT NULL,
                         deleted BOOLEAN NOT NULL,
                         creation_dt TIMESTAMP WITHOUT TIME ZONE NOT NULL,
                         activation_dt TIMESTAMP WITHOUT TIME ZONE NOT NULL,
                         deletion_dt TIMESTAMP WITHOUT TIME ZONE,
                         PRIMARY KEY (id),
                         UNIQUE (name),
                         UNIQUE (email)
);


CREATE TABLE room (
                      id VARCHAR(10) NOT NULL,
                      description VARCHAR(30) NOT NULL,
                      company_id VARCHAR(36) NOT NULL,
                      deleted BOOLEAN NOT NULL,
                      creation_dt TIMESTAMP WITHOUT TIME ZONE NOT NULL,
                      activation_dt TIMESTAMP WITHOUT TIME ZONE NOT NULL,
                      deletion_dt TIMESTAMP WITHOUT TIME ZONE,
                      PRIMARY KEY (id),
                      FOREIGN KEY(company_id) REFERENCES company (id) ON DELETE CASCADE
);


CREATE TABLE zone (
                      id VARCHAR(10) NOT NULL,
                      description VARCHAR(30) NOT NULL,
                      room_id VARCHAR(10) NOT NULL,
                      deleted BOOLEAN NOT NULL,
                      creation_dt TIMESTAMP WITHOUT TIME ZONE NOT NULL,
                      activation_dt TIMESTAMP WITHOUT TIME ZONE NOT NULL,
                      deletion_dt TIMESTAMP WITHOUT TIME ZONE,
                      PRIMARY KEY (id),
                      FOREIGN KEY(room_id) REFERENCES room (id) ON DELETE CASCADE
);


CREATE TABLE visit (
                       id BIGSERIAL NOT NULL,
                       company_id VARCHAR(36) NOT NULL,
                       room_id VARCHAR(10) NOT NULL,
                       zone_id VARCHAR(10) NOT NULL,
                       visitor_id VARCHAR(15),
                       phone_number VARCHAR(20),
                       fname VARCHAR(30),
                       lname VARCHAR(30),
                       visit_datetime TIMESTAMP WITHOUT TIME ZONE NOT NULL,
                       PRIMARY KEY (id),
                       FOREIGN KEY(company_id) REFERENCES company (id),
                       FOREIGN KEY(room_id) REFERENCES room (id),
                       FOREIGN KEY(zone_id) REFERENCES zone (id)
);


CREATE TABLE visit_histo (
                             id BIGINT NOT NULL,
                             company_id VARCHAR(36) NOT NULL,
                             room_id VARCHAR(10) NOT NULL,
                             zone_id VARCHAR(10) NOT NULL,
                             visitor_id BYTEA,
                             phone_number BYTEA,
                             visit_datetime TIMESTAMP WITHOUT TIME ZONE NOT NULL,
                             creation_dt TIMESTAMP WITHOUT TIME ZONE NOT NULL,
                             PRIMARY KEY (id),
                             FOREIGN KEY(company_id) REFERENCES company (id),
                             FOREIGN KEY(room_id) REFERENCES room (id),
                             FOREIGN KEY(zone_id) REFERENCES zone (id)
);


COMMIT;