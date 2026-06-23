--
-- PostgreSQL database dump
--

\restrict uCZvhlVclujAFMgaFZdRaHi54HMi2Sqpn6tVGs7CQHdntJ2CqQtxqLMgA0ygrqh

-- Dumped from database version 15.18
-- Dumped by pg_dump version 15.18

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

ALTER TABLE IF EXISTS ONLY public.space DROP CONSTRAINT IF EXISTS space_id_parking_fkey;
ALTER TABLE IF EXISTS ONLY public.profiles DROP CONSTRAINT IF EXISTS profiles_user_id_fkey;
ALTER TABLE IF EXISTS ONLY public.profiles DROP CONSTRAINT IF EXISTS profiles_company_id_fkey;
ALTER TABLE IF EXISTS ONLY public.parking DROP CONSTRAINT IF EXISTS parking_id_company_fkey;
ALTER TABLE IF EXISTS ONLY public.invoice_sequences DROP CONSTRAINT IF EXISTS invoice_sequences_id_company_fkey;
ALTER TABLE IF EXISTS ONLY public.booking DROP CONSTRAINT IF EXISTS booking_id_user_fkey;
ALTER TABLE IF EXISTS ONLY public.booking DROP CONSTRAINT IF EXISTS booking_id_space_fkey;
ALTER TABLE IF EXISTS ONLY public.users DROP CONSTRAINT IF EXISTS users_verification_token_key;
ALTER TABLE IF EXISTS ONLY public.users DROP CONSTRAINT IF EXISTS users_reset_password_token_key;
ALTER TABLE IF EXISTS ONLY public.users DROP CONSTRAINT IF EXISTS users_pkey;
ALTER TABLE IF EXISTS ONLY public.users DROP CONSTRAINT IF EXISTS users_email_key;
ALTER TABLE IF EXISTS ONLY public.space DROP CONSTRAINT IF EXISTS space_pkey;
ALTER TABLE IF EXISTS ONLY public.profiles DROP CONSTRAINT IF EXISTS profiles_user_id_key;
ALTER TABLE IF EXISTS ONLY public.profiles DROP CONSTRAINT IF EXISTS profiles_pkey;
ALTER TABLE IF EXISTS ONLY public.parking DROP CONSTRAINT IF EXISTS parking_pkey;
ALTER TABLE IF EXISTS ONLY public.invoice_sequences DROP CONSTRAINT IF EXISTS invoice_sequences_pkey;
ALTER TABLE IF EXISTS ONLY public.company DROP CONSTRAINT IF EXISTS company_pkey;
ALTER TABLE IF EXISTS ONLY public.booking DROP CONSTRAINT IF EXISTS booking_pkey;
ALTER TABLE IF EXISTS ONLY public.invoice_sequences DROP CONSTRAINT IF EXISTS _company_serie_uc;
ALTER TABLE IF EXISTS public.users ALTER COLUMN id DROP DEFAULT;
ALTER TABLE IF EXISTS public.space ALTER COLUMN id DROP DEFAULT;
ALTER TABLE IF EXISTS public.profiles ALTER COLUMN id DROP DEFAULT;
ALTER TABLE IF EXISTS public.parking ALTER COLUMN id DROP DEFAULT;
ALTER TABLE IF EXISTS public.invoice_sequences ALTER COLUMN id DROP DEFAULT;
ALTER TABLE IF EXISTS public.company ALTER COLUMN id DROP DEFAULT;
ALTER TABLE IF EXISTS public.booking ALTER COLUMN id DROP DEFAULT;
DROP SEQUENCE IF EXISTS public.users_id_seq;
DROP TABLE IF EXISTS public.users;
DROP SEQUENCE IF EXISTS public.space_id_seq;
DROP TABLE IF EXISTS public.space;
DROP SEQUENCE IF EXISTS public.profiles_id_seq;
DROP TABLE IF EXISTS public.profiles;
DROP SEQUENCE IF EXISTS public.parking_id_seq;
DROP TABLE IF EXISTS public.parking;
DROP SEQUENCE IF EXISTS public.invoice_sequences_id_seq;
DROP TABLE IF EXISTS public.invoice_sequences;
DROP SEQUENCE IF EXISTS public.company_id_seq;
DROP TABLE IF EXISTS public.company;
DROP SEQUENCE IF EXISTS public.booking_id_seq;
DROP TABLE IF EXISTS public.booking;
DROP TYPE IF EXISTS public.userrole;
--
-- Name: userrole; Type: TYPE; Schema: public; Owner: defaultdb_user
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
-- Name: booking; Type: TABLE; Schema: public; Owner: defaultdb_user
--

CREATE TABLE public.booking (
    id bigint NOT NULL,
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

--
-- Name: booking_id_seq; Type: SEQUENCE; Schema: public; Owner: defaultdb_user
--

CREATE SEQUENCE public.booking_id_seq
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER TABLE public.booking_id_seq OWNER TO defaultdb_user;

--
-- Name: booking_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: defaultdb_user
--

ALTER SEQUENCE public.booking_id_seq OWNED BY public.booking.id;


--
-- Name: company; Type: TABLE; Schema: public; Owner: defaultdb_user
--

CREATE TABLE public.company (
    id integer NOT NULL,
    name character varying(50) NOT NULL,
    cif character varying(15),
    tbai_enabled boolean NOT NULL,
    tbai_software_license character varying(100)
);


ALTER TABLE public.company OWNER TO defaultdb_user;

--
-- Name: company_id_seq; Type: SEQUENCE; Schema: public; Owner: defaultdb_user
--

CREATE SEQUENCE public.company_id_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER TABLE public.company_id_seq OWNER TO defaultdb_user;

--
-- Name: company_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: defaultdb_user
--

ALTER SEQUENCE public.company_id_seq OWNED BY public.company.id;


--
-- Name: invoice_sequences; Type: TABLE; Schema: public; Owner: defaultdb_user
--

CREATE TABLE public.invoice_sequences (
    id integer NOT NULL,
    id_company integer NOT NULL,
    serie character varying(20) NOT NULL,
    last_number integer NOT NULL
);


ALTER TABLE public.invoice_sequences OWNER TO defaultdb_user;

--
-- Name: invoice_sequences_id_seq; Type: SEQUENCE; Schema: public; Owner: defaultdb_user
--

CREATE SEQUENCE public.invoice_sequences_id_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER TABLE public.invoice_sequences_id_seq OWNER TO defaultdb_user;

--
-- Name: invoice_sequences_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: defaultdb_user
--

ALTER SEQUENCE public.invoice_sequences_id_seq OWNED BY public.invoice_sequences.id;


--
-- Name: parking; Type: TABLE; Schema: public; Owner: defaultdb_user
--

CREATE TABLE public.parking (
    id bigint NOT NULL,
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

--
-- Name: parking_id_seq; Type: SEQUENCE; Schema: public; Owner: defaultdb_user
--

CREATE SEQUENCE public.parking_id_seq
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER TABLE public.parking_id_seq OWNER TO defaultdb_user;

--
-- Name: parking_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: defaultdb_user
--

ALTER SEQUENCE public.parking_id_seq OWNED BY public.parking.id;


--
-- Name: profiles; Type: TABLE; Schema: public; Owner: defaultdb_user
--

CREATE TABLE public.profiles (
    id bigint NOT NULL,
    user_id bigint NOT NULL,
    company_id integer,
    dni character varying(255),
    name character varying(255) NOT NULL,
    last_name character varying(255),
    birth_day date NOT NULL,
    avatar character varying(500),
    role public.userrole NOT NULL,
    iban character varying(34),
    metodo_pago character varying(50),
    tarjeta character varying(50)
);


ALTER TABLE public.profiles OWNER TO defaultdb_user;

--
-- Name: profiles_id_seq; Type: SEQUENCE; Schema: public; Owner: defaultdb_user
--

CREATE SEQUENCE public.profiles_id_seq
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER TABLE public.profiles_id_seq OWNER TO defaultdb_user;

--
-- Name: profiles_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: defaultdb_user
--

ALTER SEQUENCE public.profiles_id_seq OWNED BY public.profiles.id;


--
-- Name: space; Type: TABLE; Schema: public; Owner: defaultdb_user
--

CREATE TABLE public.space (
    id bigint NOT NULL,
    id_parking bigint NOT NULL,
    name character varying(50),
    isvip boolean,
    has_electr boolean,
    status character varying(1),
    price double precision
);


ALTER TABLE public.space OWNER TO defaultdb_user;

--
-- Name: space_id_seq; Type: SEQUENCE; Schema: public; Owner: defaultdb_user
--

CREATE SEQUENCE public.space_id_seq
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER TABLE public.space_id_seq OWNER TO defaultdb_user;

--
-- Name: space_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: defaultdb_user
--

ALTER SEQUENCE public.space_id_seq OWNED BY public.space.id;


--
-- Name: users; Type: TABLE; Schema: public; Owner: defaultdb_user
--

CREATE TABLE public.users (
    id bigint NOT NULL,
    email character varying(255) NOT NULL,
    pass_user character varying(255),
    is_verified boolean NOT NULL,
    verification_token character varying(255),
    reset_password_token character varying(255),
    reset_password_expires timestamp without time zone,
    password_reset_verified boolean NOT NULL
);


ALTER TABLE public.users OWNER TO defaultdb_user;

--
-- Name: users_id_seq; Type: SEQUENCE; Schema: public; Owner: defaultdb_user
--

CREATE SEQUENCE public.users_id_seq
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER TABLE public.users_id_seq OWNER TO defaultdb_user;

--
-- Name: users_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: defaultdb_user
--

ALTER SEQUENCE public.users_id_seq OWNED BY public.users.id;


--
-- Name: booking id; Type: DEFAULT; Schema: public; Owner: defaultdb_user
--

ALTER TABLE ONLY public.booking ALTER COLUMN id SET DEFAULT nextval('public.booking_id_seq'::regclass);


--
-- Name: company id; Type: DEFAULT; Schema: public; Owner: defaultdb_user
--

ALTER TABLE ONLY public.company ALTER COLUMN id SET DEFAULT nextval('public.company_id_seq'::regclass);


--
-- Name: invoice_sequences id; Type: DEFAULT; Schema: public; Owner: defaultdb_user
--

ALTER TABLE ONLY public.invoice_sequences ALTER COLUMN id SET DEFAULT nextval('public.invoice_sequences_id_seq'::regclass);


--
-- Name: parking id; Type: DEFAULT; Schema: public; Owner: defaultdb_user
--

ALTER TABLE ONLY public.parking ALTER COLUMN id SET DEFAULT nextval('public.parking_id_seq'::regclass);


--
-- Name: profiles id; Type: DEFAULT; Schema: public; Owner: defaultdb_user
--

ALTER TABLE ONLY public.profiles ALTER COLUMN id SET DEFAULT nextval('public.profiles_id_seq'::regclass);


--
-- Name: space id; Type: DEFAULT; Schema: public; Owner: defaultdb_user
--

ALTER TABLE ONLY public.space ALTER COLUMN id SET DEFAULT nextval('public.space_id_seq'::regclass);


--
-- Name: users id; Type: DEFAULT; Schema: public; Owner: defaultdb_user
--

ALTER TABLE ONLY public.users ALTER COLUMN id SET DEFAULT nextval('public.users_id_seq'::regclass);


--
-- Data for Name: booking; Type: TABLE DATA; Schema: public; Owner: defaultdb_user
--

COPY public.booking (id, id_user, id_space, start_date, end_date, created_at, status, rating, license_plate, total_price, invoice_serie, invoice_number, invoice_date, tbai_id, tbai_qr_code) FROM stdin;
\.


--
-- Data for Name: company; Type: TABLE DATA; Schema: public; Owner: defaultdb_user
--

COPY public.company (id, name, cif, tbai_enabled, tbai_software_license) FROM stdin;
1	Hemen-go	B12345678	t	TBAI-HEMENGO-99882
2	hemen-go	B12345678	f	\N
\.


--
-- Data for Name: invoice_sequences; Type: TABLE DATA; Schema: public; Owner: defaultdb_user
--

COPY public.invoice_sequences (id, id_company, serie, last_number) FROM stdin;
\.


--
-- Data for Name: parking; Type: TABLE DATA; Schema: public; Owner: defaultdb_user
--

COPY public.parking (id, id_company, name, province, municipality, isactive, web_parking, telephone, email, contact_person, has_electricity, has_waste_disposal, has_vip_spots, tbai_serie_facturacion, latitude, longitude, description) FROM stdin;
1	2	Parking La Galea beach	Bizkaia	Getxo	t	https://www.la-galea-caravaning.com	688745692	info@la-galea-caravaning.com	Mikel Basurko	t	t	t	GALEA26	43.3712	-3.0345	Estupendo parking frente a los acantilados de La Galea. Ideal para autocaravanas con vistas al mar de Getxo.
2	2	Parking Zarautz Costa	Gipuzkoa	Zarautz	t	https://www.zarautz-camper.com	943123456	info@zarautz-camper.com	Ane Mendizabal	t	f	t	ZARAUTZ26	43.2844	-2.1691	Ubicación privilegiada en la costa vasca. A pocos metros de la playa de Zarautz, ideal para surfistas.
3	2	Parking Hondarribia Puerto	Gipuzkoa	Hondarribia	t	\N	943654321	info@hondarribia-parking.com	Iñaki Agirre	f	t	f	HONDA26	43.3789	-1.7925	Ubicado junto al puerto deportivo de Hondarribia. Zona tranquila vigilada las 24 horas y con todos los servicios básicos.
\.


--
-- Data for Name: profiles; Type: TABLE DATA; Schema: public; Owner: defaultdb_user
--

--COPY public.profiles (id, user_id, company_id, dni, name, last_name, birth_day, avatar, role, iban, metodo_pago, tarjeta) FROM stdin;
--1	1	\N	00000000S	Super	Admin	1980-01-01	\N	SUPER_ADMIN	\N	iban	\N
--2	2	1	11111111H	Admin	Hemen-go	1981-06-01	\N	ADMIN	\N	iban	\N
--3	3	\N	12345678A	Jon	Doe	1990-05-12	\N	USER	\N	iban	\N
--4	4	\N	87654321B	María	García	1995-03-20	\N	USER	\N	iban	\N
--\.


--
-- Data for Name: space; Type: TABLE DATA; Schema: public; Owner: defaultdb_user
--

COPY public.space (id, id_parking, name, isvip, has_electr, status, price) FROM stdin;
1	1	A1	t	t	0	25
2	1	A2	f	t	0	27.5
3	1	B1	f	f	0	20
4	2	C1	t	t	0	30
5	2	C2	f	t	0	22
6	3	D1	f	f	0	18
\.


--
-- Data for Name: users; Type: TABLE DATA; Schema: public; Owner: defaultdb_user
--

--COPY public.users (id, email, pass_user, is_verified, verification_token, reset_password_token, reset_password_expires, password_reset_verified) FROM stdin;
--1	superadmin@hemen-go.com	scrypt:32768:8:1$CHKyBvN67nls2d1f$b7b6c63d7a0f24cdf633f63621f17ab98308c7cac01a2db8a373332712da1e8d6062953462a4f480e4d57faeef3fed12017bfe92de25f4c2ae72fc7819bcbf1f	t	\N	\N	\N	f
--2	admin@hemen-go.com	scrypt:32768:8:1$CHKyBvN67nls2d1f$b7b6c63d7a0f24cdf633f63621f17ab98308c7cac01a2db8a373332712da1e8d6062953462a4f480e4d57faeef3fed12017bfe92de25f4c2ae72fc7819bcbf1f	t	\N	\N	\N	f
--3	jon.doe@example.com	scrypt:32768:8:1$CHKyBvN67nls2d1f$b7b6c63d7a0f24cdf633f63621f17ab98308c7cac01a2db8a373332712da1e8d6062953462a4f480e4d57faeef3fed12017bfe92de25f4c2ae72fc7819bcbf1f	t	\N	\N	\N	f
--4	usuario@example.com	scrypt:32768:8:1$CHKyBvN67nls2d1f$b7b6c63d7a0f24cdf633f63621f17ab98308c7cac01a2db8a373332712da1e8d6062953462a4f480e4d57faeef3fed12017bfe92de25f4c2ae72fc7819bcbf1f	t	\N	\N	\N	f
--\.


--
-- Name: booking_id_seq; Type: SEQUENCE SET; Schema: public; Owner: defaultdb_user
--

SELECT pg_catalog.setval('public.booking_id_seq', 1, false);


--
-- Name: company_id_seq; Type: SEQUENCE SET; Schema: public; Owner: defaultdb_user
--

SELECT pg_catalog.setval('public.company_id_seq', 2, true);


--
-- Name: invoice_sequences_id_seq; Type: SEQUENCE SET; Schema: public; Owner: defaultdb_user
--

SELECT pg_catalog.setval('public.invoice_sequences_id_seq', 1, false);


--
-- Name: parking_id_seq; Type: SEQUENCE SET; Schema: public; Owner: defaultdb_user
--

SELECT pg_catalog.setval('public.parking_id_seq', 3, true);


--
-- Name: profiles_id_seq; Type: SEQUENCE SET; Schema: public; Owner: defaultdb_user
--

SELECT pg_catalog.setval('public.profiles_id_seq', 4, true);


--
-- Name: space_id_seq; Type: SEQUENCE SET; Schema: public; Owner: defaultdb_user
--

SELECT pg_catalog.setval('public.space_id_seq', 6, true);


--
-- Name: users_id_seq; Type: SEQUENCE SET; Schema: public; Owner: defaultdb_user
--

SELECT pg_catalog.setval('public.users_id_seq', 4, true);


--
-- Name: invoice_sequences _company_serie_uc; Type: CONSTRAINT; Schema: public; Owner: defaultdb_user
--

ALTER TABLE ONLY public.invoice_sequences
    ADD CONSTRAINT _company_serie_uc UNIQUE (id_company, serie);


--
-- Name: booking booking_pkey; Type: CONSTRAINT; Schema: public; Owner: defaultdb_user
--

ALTER TABLE ONLY public.booking
    ADD CONSTRAINT booking_pkey PRIMARY KEY (id);


--
-- Name: company company_pkey; Type: CONSTRAINT; Schema: public; Owner: defaultdb_user
--

ALTER TABLE ONLY public.company
    ADD CONSTRAINT company_pkey PRIMARY KEY (id);


--
-- Name: invoice_sequences invoice_sequences_pkey; Type: CONSTRAINT; Schema: public; Owner: defaultdb_user
--

ALTER TABLE ONLY public.invoice_sequences
    ADD CONSTRAINT invoice_sequences_pkey PRIMARY KEY (id);


--
-- Name: parking parking_pkey; Type: CONSTRAINT; Schema: public; Owner: defaultdb_user
--

ALTER TABLE ONLY public.parking
    ADD CONSTRAINT parking_pkey PRIMARY KEY (id);


--
-- Name: profiles profiles_pkey; Type: CONSTRAINT; Schema: public; Owner: defaultdb_user
--

ALTER TABLE ONLY public.profiles
    ADD CONSTRAINT profiles_pkey PRIMARY KEY (id);


--
-- Name: profiles profiles_user_id_key; Type: CONSTRAINT; Schema: public; Owner: defaultdb_user
--

ALTER TABLE ONLY public.profiles
    ADD CONSTRAINT profiles_user_id_key UNIQUE (user_id);


--
-- Name: space space_pkey; Type: CONSTRAINT; Schema: public; Owner: defaultdb_user
--

ALTER TABLE ONLY public.space
    ADD CONSTRAINT space_pkey PRIMARY KEY (id);


--
-- Name: users users_email_key; Type: CONSTRAINT; Schema: public; Owner: defaultdb_user
--

ALTER TABLE ONLY public.users
    ADD CONSTRAINT users_email_key UNIQUE (email);


--
-- Name: users users_pkey; Type: CONSTRAINT; Schema: public; Owner: defaultdb_user
--

ALTER TABLE ONLY public.users
    ADD CONSTRAINT users_pkey PRIMARY KEY (id);


--
-- Name: users users_reset_password_token_key; Type: CONSTRAINT; Schema: public; Owner: defaultdb_user
--

ALTER TABLE ONLY public.users
    ADD CONSTRAINT users_reset_password_token_key UNIQUE (reset_password_token);


--
-- Name: users users_verification_token_key; Type: CONSTRAINT; Schema: public; Owner: defaultdb_user
--

ALTER TABLE ONLY public.users
    ADD CONSTRAINT users_verification_token_key UNIQUE (verification_token);


--
-- Name: booking booking_id_space_fkey; Type: FK CONSTRAINT; Schema: public; Owner: defaultdb_user
--

ALTER TABLE ONLY public.booking
    ADD CONSTRAINT booking_id_space_fkey FOREIGN KEY (id_space) REFERENCES public.space(id) ON DELETE CASCADE;


--
-- Name: booking booking_id_user_fkey; Type: FK CONSTRAINT; Schema: public; Owner: defaultdb_user
--

ALTER TABLE ONLY public.booking
    ADD CONSTRAINT booking_id_user_fkey FOREIGN KEY (id_user) REFERENCES public.users(id) ON DELETE CASCADE;


--
-- Name: invoice_sequences invoice_sequences_id_company_fkey; Type: FK CONSTRAINT; Schema: public; Owner: defaultdb_user
--

ALTER TABLE ONLY public.invoice_sequences
    ADD CONSTRAINT invoice_sequences_id_company_fkey FOREIGN KEY (id_company) REFERENCES public.company(id) ON DELETE CASCADE;


--
-- Name: parking parking_id_company_fkey; Type: FK CONSTRAINT; Schema: public; Owner: defaultdb_user
--

ALTER TABLE ONLY public.parking
    ADD CONSTRAINT parking_id_company_fkey FOREIGN KEY (id_company) REFERENCES public.company(id);


--
-- Name: profiles profiles_company_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: defaultdb_user
--

ALTER TABLE ONLY public.profiles
    ADD CONSTRAINT profiles_company_id_fkey FOREIGN KEY (company_id) REFERENCES public.company(id);


--
-- Name: profiles profiles_user_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: defaultdb_user
--

ALTER TABLE ONLY public.profiles
    ADD CONSTRAINT profiles_user_id_fkey FOREIGN KEY (user_id) REFERENCES public.users(id);


--
-- Name: space space_id_parking_fkey; Type: FK CONSTRAINT; Schema: public; Owner: defaultdb_user
--

ALTER TABLE ONLY public.space
    ADD CONSTRAINT space_id_parking_fkey FOREIGN KEY (id_parking) REFERENCES public.parking(id) ON DELETE CASCADE;


--
-- PostgreSQL database dump complete
--

\unrestrict uCZvhlVclujAFMgaFZdRaHi54HMi2Sqpn6tVGs7CQHdntJ2CqQtxqLMgA0ygrqh

