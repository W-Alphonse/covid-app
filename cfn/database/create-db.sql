BEGIN;

-- public.company definition

-- Drop table

-- DROP TABLE public.company;

CREATE TABLE public.company (
	id varchar(36) NOT NULL,
	"name" varchar(50) NOT NULL,
	"type" varchar(10) NULL,
	siret varchar(14) NULL,
	address varchar(300) NULL,
	zip_code varchar(10) NULL,
	country_code varchar(2) NULL,
	phone_number varchar(20) NULL,
	email varchar(64) NOT NULL,
	contact_fname varchar(20) NULL,
	contact_lname varchar(20) NULL,
	url varchar(128) NULL,
	offer varchar(10) NOT NULL,
	max_zone int4 NOT NULL,
	deleted bool NOT NULL,
	creation_dt timestamp NOT NULL,
	activation_dt timestamp NOT NULL,
	deletion_dt timestamp NULL,
	encrypted_data_key bytea NULL,
	iv bytea NULL,
	contractual_visitor_pmonth int4 NOT NULL,
	visit_on_last_count int4 NOT NULL,
	last_count_dt timestamp NOT NULL,
	visitor_on_last_count int4 NOT NULL,
	CONSTRAINT company_email_key UNIQUE (email),
	CONSTRAINT company_pkey PRIMARY KEY (id)
);


-- public.company_visit definition

-- Drop table

-- DROP TABLE public.company_visit;

CREATE TABLE public.company_visit (
	company_id varchar(36) NOT NULL,
	start_period_dt timestamp NOT NULL,
	period_type varchar(3) NOT NULL,
	visitor_count int4 NOT NULL,
	visit_count int4 NOT NULL,
	last_count_dt timestamp NOT NULL,
	creation_dt timestamp NOT NULL,
	CONSTRAINT company_visit_pkey PRIMARY KEY (company_id, start_period_dt, period_type)
);


-- public.room definition

-- Drop table

-- DROP TABLE public.room;

CREATE TABLE public.room (
	id varchar(10) NOT NULL,
	description varchar(30) NOT NULL,
	company_id varchar(36) NOT NULL,
	deleted bool NOT NULL,
	creation_dt timestamp NOT NULL,
	activation_dt timestamp NOT NULL,
	deletion_dt timestamp NULL,
	CONSTRAINT room_pkey PRIMARY KEY (id),
	CONSTRAINT room_company_id_fkey FOREIGN KEY (company_id) REFERENCES company(id) ON DELETE CASCADE
);


-- public."zone" definition

-- Drop table

-- DROP TABLE public."zone";

CREATE TABLE public."zone" (
	id varchar(10) NOT NULL,
	description varchar(30) NOT NULL,
	room_id varchar(10) NOT NULL,
	deleted bool NOT NULL,
	creation_dt timestamp NOT NULL,
	activation_dt timestamp NOT NULL,
	deletion_dt timestamp NULL,
	CONSTRAINT zone_pkey PRIMARY KEY (id),
	CONSTRAINT zone_room_id_fkey FOREIGN KEY (room_id) REFERENCES room(id) ON DELETE CASCADE
);


-- public.visit definition

-- Drop table

-- DROP TABLE public.visit;

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
	CONSTRAINT visit_pkey PRIMARY KEY (id),
	CONSTRAINT visit_company_id_fkey FOREIGN KEY (company_id) REFERENCES company(id),
	CONSTRAINT visit_room_id_fkey FOREIGN KEY (room_id) REFERENCES room(id),
	CONSTRAINT visit_zone_id_fkey FOREIGN KEY (zone_id) REFERENCES zone(id)
);


-- public.visit_histo definition

-- Drop table

-- DROP TABLE public.visit_histo;

CREATE TABLE public.visit_histo (
	id bigserial NOT NULL,
	company_id varchar(36) NOT NULL,
	room_id varchar(10) NOT NULL,
	zone_id varchar(10) NOT NULL,
	visit_datetime timestamp NOT NULL,
	visit_s_datetime timestamp NOT NULL,
	visit_e_datetime timestamp NOT NULL,
	creation_dt timestamp NOT NULL,
	visitor_id bytea NULL,
	phone_number bytea NULL,
	CONSTRAINT visit_histo_pkey PRIMARY KEY (id),
	CONSTRAINT visit_histo_company_id_fkey FOREIGN KEY (company_id) REFERENCES company(id),
	CONSTRAINT visit_histo_room_id_fkey FOREIGN KEY (room_id) REFERENCES room(id),
	CONSTRAINT visit_histo_zone_id_fkey FOREIGN KEY (zone_id) REFERENCES zone(id)
);
COMMIT;
