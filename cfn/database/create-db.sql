
BEGIN;

CREATE TABLE public.company (
	id VARCHAR(36) NOT NULL, 
	name VARCHAR(50) NOT NULL, 
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
	encrypted_data_key bytea, 
	iv bytea, 
	offer VARCHAR(10) NOT NULL, 
	contractual_visit_per_month INTEGER NOT NULL, 
	cumulative_visit_per_month INTEGER NOT NULL, 
	visit_threshold_readched BOOLEAN NOT NULL, 
	max_zone INTEGER NOT NULL, 
	deleted BOOLEAN NOT NULL, 
	creation_dt TIMESTAMP WITHOUT TIME ZONE NOT NULL, 
	activation_dt TIMESTAMP WITHOUT TIME ZONE NOT NULL, 
	deletion_dt TIMESTAMP WITHOUT TIME ZONE, 
	PRIMARY KEY (id), 
	UNIQUE (email)
);

CREATE TABLE public.room (
	id varchar(10) NOT NULL,
	description varchar(30) NOT NULL,
	company_id varchar(36) NOT NULL,
	deleted bool NOT NULL,
	creation_dt timestamp NOT NULL,
	activation_dt timestamp NOT NULL,
	deletion_dt timestamp NULL,
	CONSTRAINT room_pkey PRIMARY KEY (id)
);
-- public.room foreign keys
ALTER TABLE public.room ADD CONSTRAINT room_company_id_fkey FOREIGN KEY (company_id) REFERENCES company(id) ON DELETE CASCADE;


CREATE TABLE public."zone" (
	id varchar(10) NOT NULL,
	description varchar(30) NOT NULL,
	room_id varchar(10) NOT NULL,
	deleted bool NOT NULL,
	creation_dt timestamp NOT NULL,
	activation_dt timestamp NOT NULL,
	deletion_dt timestamp NULL,
	CONSTRAINT zone_pkey PRIMARY KEY (id)
);
-- public."zone" foreign keys
ALTER TABLE public."zone" ADD CONSTRAINT zone_room_id_fkey FOREIGN KEY (room_id) REFERENCES room(id) ON DELETE CASCADE;


CREATE TABLE public.visit (
	id bigserial NOT NULL,
	company_id varchar(36) NOT NULL,
	room_id varchar(10) NOT NULL,
	zone_id varchar(10) NOT NULL,
	visit_datetime timestamp NOT NULL,
    visit_s_datetime timestamp NOT NULL,
    visit_e_datetime timestamp NOT NULL,
	visitor_id bytea NULL,
	phone_number bytea NULL,
	fname bytea NULL,
	lname bytea NULL,
	CONSTRAINT visit_pkey PRIMARY KEY (id)
);
-- public.visit foreign keys
ALTER TABLE public.visit ADD CONSTRAINT visit_company_id_fkey FOREIGN KEY (company_id) REFERENCES company(id);
ALTER TABLE public.visit ADD CONSTRAINT visit_room_id_fkey FOREIGN KEY (room_id) REFERENCES room(id);
ALTER TABLE public.visit ADD CONSTRAINT visit_zone_id_fkey FOREIGN KEY (zone_id) REFERENCES zone(id);


CREATE TABLE public.visit_histo (
	id bigserial NOT NULL,
	company_id varchar(36) NOT NULL,
	room_id varchar(10) NOT NULL,
	zone_id varchar(10) NOT NULL,
	visit_datetime timestamp NOT NULL,
    visit_s_datetime timestamp NOT NULL,
    visit_e_datetime timestamp NOT NULL,
	creation_dt timestamp NOT NULL,
	CONSTRAINT visit_histo_pkey PRIMARY KEY (id)
);
-- public.visit_histo foreign keys
ALTER TABLE public.visit_histo ADD CONSTRAINT visit_histo_company_id_fkey FOREIGN KEY (company_id) REFERENCES company(id);
ALTER TABLE public.visit_histo ADD CONSTRAINT visit_histo_room_id_fkey FOREIGN KEY (room_id) REFERENCES room(id);
ALTER TABLE public.visit_histo ADD CONSTRAINT visit_histo_zone_id_fkey FOREIGN KEY (zone_id) REFERENCES zone(id);

COMMIT;
