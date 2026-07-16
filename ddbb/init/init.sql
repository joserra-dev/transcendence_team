-- PostgreSQL database dump
--

SET statement_timeout = 0;
SET lock_timeout = 0;
SET idle_in_transaction_session_timeout = 0;
SET client_encoding = 'UTF8';
SET standard_conforming_strings = on;
SELECT pg_catalog.set_config('search_path', '', false);
SET check_function_bodies = false;
SET xmloption = content;
SET client_min_messages = warning;
SET row_security = off;

-- Eliminar restricciones existentes si las hay (Limpieza limpia)
ALTER TABLE IF EXISTS ONLY public.chat_messages DROP CONSTRAINT IF EXISTS chat_messages_sender_id_fkey;
ALTER TABLE IF EXISTS ONLY public.chat_messages DROP CONSTRAINT IF EXISTS chat_messages_company_id_fkey;
ALTER TABLE IF EXISTS ONLY public.space DROP CONSTRAINT IF EXISTS space_id_parking_fkey;
ALTER TABLE IF EXISTS ONLY public.profiles DROP CONSTRAINT IF EXISTS profiles_user_id_fkey;
ALTER TABLE IF EXISTS ONLY public.profiles DROP CONSTRAINT IF EXISTS profiles_company_id_fkey;
ALTER TABLE IF EXISTS ONLY public.parking DROP CONSTRAINT IF EXISTS parking_id_company_fkey;
ALTER TABLE IF EXISTS ONLY public.invoice_sequences DROP CONSTRAINT IF EXISTS invoice_sequences_id_company_fkey;
ALTER TABLE IF EXISTS ONLY public.booking DROP CONSTRAINT IF EXISTS booking_id_user_fkey;
ALTER TABLE IF EXISTS ONLY public.booking DROP CONSTRAINT IF EXISTS booking_id_space_fkey;
ALTER TABLE IF EXISTS ONLY public.parking_blocked_day DROP CONSTRAINT IF EXISTS parking_blocked_day_id_parking_fkey;
ALTER TABLE IF EXISTS ONLY public.space_blocked_day DROP CONSTRAINT IF EXISTS space_blocked_day_id_space_fkey;

DROP TABLE IF EXISTS public.space_blocked_day;
DROP TABLE IF EXISTS public.parking_blocked_day;
DROP TABLE IF EXISTS public.chat_messages;
DROP TABLE IF EXISTS public.booking;
DROP TABLE IF EXISTS public.space;
DROP TABLE IF EXISTS public.parking;
DROP TABLE IF EXISTS public.profiles;
DROP TABLE IF EXISTS public.invoice_sequences;
DROP TABLE IF EXISTS public.company;
DROP TABLE IF EXISTS public.users;
DROP TYPE IF EXISTS public.userrole;

--
-- Tipo: userrole
--
CREATE TYPE public.userrole AS ENUM (
    'USER',
    'ADMIN',
    'SUPER_ADMIN'
);
ALTER TYPE public.userrole OWNER TO defaultdb_user;

SET default_tablespace = '';
SET default_table_access_method = heap;

--
-- Tabla: users
--
CREATE TABLE public.users (
    id bigint NOT NULL PRIMARY KEY,
    email character varying(255) NOT NULL UNIQUE,
    pass_user character varying(255),
    is_verified boolean NOT NULL,
    verification_token character varying(255) UNIQUE,
    reset_password_token character varying(255) UNIQUE,
    reset_password_expires timestamp without time zone,
    password_reset_verified boolean NOT NULL
);
ALTER TABLE public.users OWNER TO defaultdb_user;

CREATE SEQUENCE public.users_id_seq START WITH 1 INCREMENT BY 1 NO MINVALUE NO MAXVALUE CACHE 1;
ALTER SEQUENCE public.users_id_seq OWNER TO defaultdb_user;
ALTER SEQUENCE public.users_id_seq OWNED BY public.users.id;
ALTER TABLE ONLY public.users ALTER COLUMN id SET DEFAULT nextval('public.users_id_seq'::regclass);

--
-- Tabla: company
--
CREATE TABLE public.company (
    id integer NOT NULL PRIMARY KEY,
    name character varying(50) NOT NULL,
    cif character varying(15),
    tbai_enabled boolean NOT NULL,
    tbai_software_license character varying(100)
);
ALTER TABLE public.company OWNER TO defaultdb_user;

CREATE SEQUENCE public.company_id_seq AS integer START WITH 1 INCREMENT BY 1 NO MINVALUE NO MAXVALUE CACHE 1;
ALTER SEQUENCE public.company_id_seq OWNER TO defaultdb_user;
ALTER SEQUENCE public.company_id_seq OWNED BY public.company.id;
ALTER TABLE ONLY public.company ALTER COLUMN id SET DEFAULT nextval('public.company_id_seq'::regclass);

--
-- Tabla: parking
--
CREATE TABLE public.parking (
    id bigint NOT NULL PRIMARY KEY,
    id_company integer NOT NULL,
    name character varying(100) NOT NULL,
    province character varying(255),
    municipality character varying(255),
    isactive boolean,
    web_parking character varying(255),
    telephone character varying(255),
    email character varying(255),
    contact_person character varying(255),
    has_electricity boolean,
    has_waste_disposal boolean,
    has_vip_spots boolean,
    tbai_serie_facturacion character varying(20),
    latitude double precision,
    longitude double precision,
    description character varying(255)
);
ALTER TABLE public.parking OWNER TO defaultdb_user;

CREATE SEQUENCE public.parking_id_seq START WITH 1 INCREMENT BY 1 NO MINVALUE NO MAXVALUE CACHE 1;
ALTER SEQUENCE public.parking_id_seq OWNER TO defaultdb_user;
ALTER SEQUENCE public.parking_id_seq OWNED BY public.parking.id;
ALTER TABLE ONLY public.parking ALTER COLUMN id SET DEFAULT nextval('public.parking_id_seq'::regclass);

--
-- Tabla: space
--
CREATE TABLE public.space (
    id bigint NOT NULL PRIMARY KEY,
    id_parking bigint NOT NULL,
    name character varying(50),
    isvip boolean,
    has_electr boolean,
    status character varying(1),
    price double precision
);
ALTER TABLE public.space OWNER TO defaultdb_user;

CREATE SEQUENCE public.space_id_seq START WITH 1 INCREMENT BY 1 NO MINVALUE NO MAXVALUE CACHE 1;
ALTER SEQUENCE public.space_id_seq OWNER TO defaultdb_user;
ALTER SEQUENCE public.space_id_seq OWNED BY public.space.id;
ALTER TABLE ONLY public.space ALTER COLUMN id SET DEFAULT nextval('public.space_id_seq'::regclass);

--
-- Tabla: invoice_sequences
--
CREATE TABLE public.invoice_sequences (
    id integer NOT NULL PRIMARY KEY,
    id_company integer NOT NULL,
    serie character varying(20) NOT NULL,
    last_number integer NOT NULL,
    CONSTRAINT _company_serie_uc UNIQUE (id_company, serie)
);
ALTER TABLE public.invoice_sequences OWNER TO defaultdb_user;

CREATE SEQUENCE public.invoice_sequences_id_seq AS integer START WITH 1 INCREMENT BY 1 NO MINVALUE NO MAXVALUE CACHE 1;
ALTER SEQUENCE public.invoice_sequences_id_seq OWNER TO defaultdb_user;
ALTER SEQUENCE public.invoice_sequences_id_seq OWNED BY public.invoice_sequences.id;
ALTER TABLE ONLY public.invoice_sequences ALTER COLUMN id SET DEFAULT nextval('public.invoice_sequences_id_seq'::regclass);

--
-- Tabla: profiles
--
CREATE TABLE public.profiles (
    id bigint NOT NULL PRIMARY KEY,
    user_id bigint NOT NULL UNIQUE,
    company_id integer,
    dni character varying(255),
    name character varying(255) NOT NULL,
    last_name character varying(255),
    birth_day date NOT NULL,
    avatar character varying(500),
    role public.userrole NOT NULL
    --iban character varying(34),
    --metodo_pago character varying(50),
    --tarjeta character varying(50)
);
ALTER TABLE public.profiles OWNER TO defaultdb_user;

CREATE SEQUENCE public.profiles_id_seq START WITH 1 INCREMENT BY 1 NO MINVALUE NO MAXVALUE CACHE 1;
ALTER SEQUENCE public.profiles_id_seq OWNER TO defaultdb_user;
ALTER SEQUENCE public.profiles_id_seq OWNED BY public.profiles.id;
ALTER TABLE ONLY public.profiles ALTER COLUMN id SET DEFAULT nextval('public.profiles_id_seq'::regclass);

--
-- Tabla: booking
--
CREATE TABLE public.booking (
    id bigint NOT NULL PRIMARY KEY,
    id_user bigint NOT NULL,
    id_space bigint NOT NULL,
    start_date date,
    end_date date,
    created_at timestamp without time zone,
    status character varying(1),
    rating numeric(2,0),
    license_plate character varying(15) NOT NULL,
    total_price double precision NOT NULL,
    invoice_serie character varying(20),
    invoice_number character varying(20),
    invoice_date date,
    tbai_id character varying(100),
    tbai_qr_code text
);
ALTER TABLE public.booking OWNER TO defaultdb_user;

CREATE SEQUENCE public.booking_id_seq START WITH 1 INCREMENT BY 1 NO MINVALUE NO MAXVALUE CACHE 1;
ALTER SEQUENCE public.booking_id_seq OWNER TO defaultdb_user;
ALTER SEQUENCE public.booking_id_seq OWNED BY public.booking.id;
ALTER TABLE ONLY public.booking ALTER COLUMN id SET DEFAULT nextval('public.booking_id_seq'::regclass);

--
-- Tabla: space_blocked_day
--
CREATE TABLE public.space_blocked_day (
    id bigint NOT NULL PRIMARY KEY,
    id_space bigint NOT NULL,
    day date NOT NULL,
    created_at timestamp without time zone DEFAULT CURRENT_TIMESTAMP,
    CONSTRAINT uq_space_blocked_day UNIQUE (id_space, day)
);
ALTER TABLE public.space_blocked_day OWNER TO defaultdb_user;

CREATE SEQUENCE public.space_blocked_day_id_seq START WITH 1 INCREMENT BY 1 NO MINVALUE NO MAXVALUE CACHE 1;
ALTER SEQUENCE public.space_blocked_day_id_seq OWNER TO defaultdb_user;
ALTER SEQUENCE public.space_blocked_day_id_seq OWNED BY public.space_blocked_day.id;
ALTER TABLE ONLY public.space_blocked_day ALTER COLUMN id SET DEFAULT nextval('public.space_blocked_day_id_seq'::regclass);


CREATE TABLE public.chat_messages (
    id bigint NOT NULL PRIMARY KEY,
    company_id integer NOT NULL,
    sender_id bigint NOT NULL,
    content text NOT NULL,
    is_read boolean DEFAULT false NOT NULL,
    created_at timestamp without time zone DEFAULT CURRENT_TIMESTAMP NOT NULL
);
ALTER TABLE public.chat_messages OWNER TO defaultdb_user;

CREATE SEQUENCE public.chat_messages_id_seq START WITH 1 INCREMENT BY 1 NO MINVALUE NO MAXVALUE CACHE 1;
ALTER SEQUENCE public.chat_messages_id_seq OWNER TO defaultdb_user;
ALTER SEQUENCE public.chat_messages_id_seq OWNED BY public.chat_messages.id;
ALTER TABLE ONLY public.chat_messages ALTER COLUMN id SET DEFAULT nextval('public.chat_messages_id_seq'::regclass);


--
-- DATA INSERTION (Sección de datos)
--

COPY public.company (id, name, cif, tbai_enabled, tbai_software_license) FROM stdin;
1	Hemen-go	B68064831	t	TBAI-HEMENGO-99882
2	hemen-go	B21520622	f	\N
\.

COPY public.parking (id, id_company, name, province, municipality, isactive, web_parking, telephone, email, contact_person, has_electricity, has_waste_disposal, has_vip_spots, tbai_serie_facturacion, latitude, longitude, description) FROM stdin;
1	2	Parking La Galea beach	Bizkaia	Getxo	t	https://www.la-galea-caravaning.com	688745692	info@la-galea-caravaning.com	Mikel Basurko	t	t	t	GALEA26	43.3712	-3.0345	Estupendo parking frente a los acantalidados de La Galea.
2	2	Parking Zarautz Costa	Gipuzkoa	Zarautz	t	https://www.zarautz-camper.com	943123456	info@zarautz-camper.com	Ane Mendizabal	t	f	t	ZARAUTZ26	43.2844	-2.1691	Ubicación privilegiada en la costa vasca.
3	2	Parking Hondarribia Puerto	Gipuzkoa	Hondarribia	t	\N	943654321	info@hondarribia-parking.com	Iñaki Agirre	f	t	f	HONDA26	43.3789	-1.7925	Ubicado junto al puerto deportivo.
\.

COPY public.space (id, id_parking, name, isvip, has_electr, status, price) FROM stdin;
1	1	A1	t	t	0	25
2	1	A2	f	t	0	27.5
3	1	B1	f	f	0	20
4	2	C1	t	t	0	30
5	2	C2	f	t	0	22
6	3	D1	f	f	0	18
\.

-- Actualización manual de Secuencias
SELECT pg_catalog.setval('public.booking_id_seq', 1, false);
SELECT pg_catalog.setval('public.company_id_seq', 2, true);
SELECT pg_catalog.setval('public.invoice_sequences_id_seq', 1, false);
SELECT pg_catalog.setval('public.parking_id_seq', 3, true);
SELECT pg_catalog.setval('public.profiles_id_seq', 4, true);
SELECT pg_catalog.setval('public.space_id_seq', 6, true);
SELECT pg_catalog.setval('public.users_id_seq', 4, true);
SELECT pg_catalog.setval('public.chat_messages_id_seq', 1, false); -- Inicializada
SELECT pg_catalog.setval('public.space_blocked_day_id_seq', 1, false);

--
-- RELACIONES / CLAVES FORÁNEAS (Foreign Keys)
--

ALTER TABLE ONLY public.booking
    ADD CONSTRAINT booking_id_space_fkey FOREIGN KEY (id_space) REFERENCES public.space(id) ON DELETE CASCADE;

ALTER TABLE ONLY public.booking
    ADD CONSTRAINT booking_id_user_fkey FOREIGN KEY (id_user) REFERENCES public.users(id) ON DELETE CASCADE;

ALTER TABLE ONLY public.invoice_sequences
    ADD CONSTRAINT invoice_sequences_id_company_fkey FOREIGN KEY (id_company) REFERENCES public.company(id) ON DELETE CASCADE;

ALTER TABLE ONLY public.parking
    ADD CONSTRAINT parking_id_company_fkey FOREIGN KEY (id_company) REFERENCES public.company(id);

ALTER TABLE ONLY public.profiles
    ADD CONSTRAINT profiles_company_id_fkey FOREIGN KEY (company_id) REFERENCES public.company(id);

ALTER TABLE ONLY public.profiles
    ADD CONSTRAINT profiles_user_id_fkey FOREIGN KEY (user_id) REFERENCES public.users(id);

ALTER TABLE ONLY public.space
    ADD CONSTRAINT space_id_parking_fkey FOREIGN KEY (id_parking) REFERENCES public.parking(id) ON DELETE CASCADE;

ALTER TABLE ONLY public.space_blocked_day
    ADD CONSTRAINT space_blocked_day_id_space_fkey FOREIGN KEY (id_space) REFERENCES public.space(id) ON DELETE CASCADE;

-- Claves foráneas de chat_messages
ALTER TABLE ONLY public.chat_messages
    ADD CONSTRAINT chat_messages_company_id_fkey FOREIGN KEY (company_id) REFERENCES public.company(id);

ALTER TABLE ONLY public.chat_messages
    ADD CONSTRAINT chat_messages_sender_id_fkey FOREIGN KEY (sender_id) REFERENCES public.users(id) ON DELETE CASCADE;