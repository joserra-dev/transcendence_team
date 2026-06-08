--
-- PostgreSQL database dump (limpiado para Docker)
--

SET statement_timeout = 0;
SET lock_timeout = 0;
SET idle_in_transaction_session_timeout = 0;
SET transaction_timeout = 0;
SET client_encoding = 'UTF8';
SET standard_conforming_strings = on;
SELECT pg_catalog.set_config('search_path', '', false);
SET check_function_bodies = false;
SET xmloption = content;
SET client_min_messages = warning;
SET row_security = off;

-- Creamos la base si no existe
--CREATE DATABASE defaultdb;
\connect defaultdb

-- El esquema public ya existe en PostgreSQL, así que NO lo creamos
-- CREATE SCHEMA public;

-- Aseguramos que el propietario sea postgres (usuario que sí existe)
ALTER SCHEMA public OWNER TO defaultdb_uk1q_user;

-- Secuencia
CREATE SEQUENCE public.empresa_id_empresa_seq
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    MAXVALUE 2147483647
    CACHE 1;

-- Cambiamos propietario a postgres
ALTER SEQUENCE public.empresa_id_empresa_seq OWNER TO defaultdb_uk1q_user;

SET default_tablespace = '';
SET default_table_access_method = heap;


--
-- TOC entry 219 (class 1259 OID 24602)
-- Name: empresas; Type: TABLE; Schema: public; Owner: defaultdb_uk1q_user
--

CREATE TABLE public.empresas (
    id_empresa integer DEFAULT nextval('public.empresa_id_empresa_seq'::regclass) NOT NULL,
    nombre_empresa character varying(50) NOT NULL,
    cif_empresa character varying(15)
);


ALTER TABLE public.empresas OWNER TO defaultdb_uk1q_user;

--
-- TOC entry 221 (class 1259 OID 24645)
-- Name: parkings; Type: TABLE; Schema: public; Owner: defaultdb_uk1q_user
--

CREATE TABLE public.parkings (
    id_parking bigint NOT NULL,
    id_empresa_parking integer NOT NULL,
    nombre_parking character varying(100) NOT NULL,
    provincia_parking character varying(255),
    municipio_parking character varying(255),
    isactivo_parking boolean,
    web_parking character varying(255),
    telefono_parking character varying(255),
    email_parking character varying(255),
    persona_contacto_parking character varying(255),
    tiene_electricidad_parking boolean,
    tiene_residuales_parking boolean,
    tiene_plazas_vip_parking boolean
);


ALTER TABLE public.parkings OWNER TO defaultdb_uk1q_user;

--
-- TOC entry 222 (class 1259 OID 24657)
-- Name: parking_id_seq; Type: SEQUENCE; Schema: public; Owner: defaultdb_uk1q_user
--

CREATE SEQUENCE public.parking_id_seq
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    MAXVALUE 999999999
    CACHE 1;


ALTER SEQUENCE public.parking_id_seq OWNER TO defaultdb_uk1q_user;

--
-- TOC entry 4480 (class 0 OID 0)
-- Dependencies: 222
-- Name: parking_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: defaultdb_uk1q_user
--

ALTER SEQUENCE public.parking_id_seq OWNED BY public.parkings.id_parking;


--
-- TOC entry 218 (class 1259 OID 24586)
-- Name: persona_id_persona_seq; Type: SEQUENCE; Schema: public; Owner: defaultdb_uk1q_user
--

CREATE SEQUENCE public.persona_id_persona_seq
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    MAXVALUE 2147483647
    CACHE 1;


ALTER SEQUENCE public.persona_id_persona_seq OWNER TO defaultdb_uk1q_user;

--
-- TOC entry 220 (class 1259 OID 24608)
-- Name: personas; Type: TABLE; Schema: public; Owner: defaultdb_uk1q_user
--

CREATE TABLE public.personas (
    id_persona bigint DEFAULT nextval('public.persona_id_persona_seq'::regclass) NOT NULL,
    dni_persona character varying(255),
    nombre_persona character varying(255) NOT NULL,
    apellidos_persona character varying(255),
    fec_nacimiento_persona date NOT NULL,
    iban_persona character varying(255),
    email_persona character varying(255) NOT NULL,
    pass_persona character varying(255),
    is_admin boolean,
    id_empresa_persona integer
);


ALTER TABLE public.personas OWNER TO defaultdb_uk1q_user;

--
-- TOC entry 223 (class 1259 OID 24669)
-- Name: plazas_id_seq; Type: SEQUENCE; Schema: public; Owner: defaultdb_uk1q_user
--

CREATE SEQUENCE public.plazas_id_seq
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    MAXVALUE 999999
    CACHE 1;


ALTER SEQUENCE public.plazas_id_seq OWNER TO defaultdb_uk1q_user;

--
-- TOC entry 224 (class 1259 OID 24670)
-- Name: plazas; Type: TABLE; Schema: public; Owner: defaultdb_uk1q_user
--

CREATE TABLE public.plazas (
    id_plaza bigint DEFAULT nextval('public.plazas_id_seq'::regclass) NOT NULL,
    id_parking_plaza bigint NOT NULL,
    nombre_plaza character varying(50),
    isvip_plaza boolean,
    tiene_electricidad_plaza boolean,
    estado_plaza character varying(1),
    precio_plaza real
);


ALTER TABLE public.plazas OWNER TO defaultdb_uk1q_user;

--
-- TOC entry 226 (class 1259 OID 24682)
-- Name: reservas; Type: TABLE; Schema: public; Owner: defaultdb_uk1q_user
--

CREATE TABLE public.reservas (
    id_reserva bigint NOT NULL,
    id_persona_reserva bigint NOT NULL,
    id_plaza_reserva bigint NOT NULL,
    fecha_inicio_reserva date,
    fecha_fin_reserva date,
    fecha_alta_reserva date DEFAULT now(),
    estado_reserva character varying(1),
    puntuacion_reserva numeric(2,0)
);


ALTER TABLE public.reservas OWNER TO defaultdb_uk1q_user;

--
-- TOC entry 225 (class 1259 OID 24681)
-- Name: reservas_id_reserva_seq; Type: SEQUENCE; Schema: public; Owner: defaultdb_uk1q_user
--

CREATE SEQUENCE public.reservas_id_reserva_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER SEQUENCE public.reservas_id_reserva_seq OWNER TO defaultdb_uk1q_user;

--
-- TOC entry 4481 (class 0 OID 0)
-- Dependencies: 225
-- Name: reservas_id_reserva_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: defaultdb_uk1q_user
--

ALTER SEQUENCE public.reservas_id_reserva_seq OWNED BY public.reservas.id_reserva;


--
-- TOC entry 4297 (class 2604 OID 24701)
-- Name: parkings id_parking; Type: DEFAULT; Schema: public; Owner: defaultdb_uk1q_user
--

ALTER TABLE ONLY public.parkings ALTER COLUMN id_parking SET DEFAULT nextval('public.parking_id_seq'::regclass);


--
-- TOC entry 4299 (class 2604 OID 24757)
-- Name: reservas id_reserva; Type: DEFAULT; Schema: public; Owner: defaultdb_uk1q_user
--

ALTER TABLE ONLY public.reservas ALTER COLUMN id_reserva SET DEFAULT nextval('public.reservas_id_reserva_seq'::regclass);


--
-- TOC entry 4465 (class 0 OID 24602)
-- Dependencies: 219
-- Data for Name: empresas; Type: TABLE DATA; Schema: public; Owner: defaultdb_uk1q_user
--

INSERT INTO public.empresas (id_empresa, nombre_empresa, cif_empresa) VALUES (1, 'Hemen-go', 'B4896522');


--
-- TOC entry 4467 (class 0 OID 24645)
-- Dependencies: 221
-- Data for Name: parkings; Type: TABLE DATA; Schema: public; Owner: defaultdb_uk1q_user
--

INSERT INTO public.parkings (id_parking, id_empresa_parking, nombre_parking, provincia_parking, municipio_parking, isactivo_parking, web_parking, telefono_parking, email_parking, persona_contacto_parking, tiene_electricidad_parking, tiene_residuales_parking, tiene_plazas_vip_parking) VALUES (1, 1, 'Parking La Galea beach', 'Bizkaia', 'Getxo', true, 'https://www.la-galea-caravaning.com', '688745692', 'info@la-galea-caravaning.com', 'Mikel Basurko', true, true, true);


--
-- TOC entry 4466 (class 0 OID 24608)
-- Dependencies: 220
-- Data for Name: personas; Type: TABLE DATA; Schema: public; Owner: defaultdb_uk1q_user
--

INSERT INTO public.personas (id_persona, dni_persona, nombre_persona, apellidos_persona, fec_nacimiento_persona, iban_persona, email_persona, pass_persona, is_admin, id_empresa_persona) VALUES (11, '12345678A', 'Jon', 'Doe', '1990-05-12', 'ES1234567890123456789012', 'jon.doe@example.com', '$2a$10$nbt1FRaXkFnLoeEQX6LT/.7EoXY2fONUijkYKYiQtbEb2v059Yxqq', false, 1);
INSERT INTO public.personas (id_persona, dni_persona, nombre_persona, apellidos_persona, fec_nacimiento_persona, iban_persona, email_persona, pass_persona, is_admin, id_empresa_persona) VALUES (57, '12345678A', 'Egoitz', 'Larrea', '1978-05-12', 'ES1234567890123456789012', 'eglarrea@birt.eus', '$2a$10$Q3ACk6nRq3g0rJnoARrER.Q84RjTjppWJ7pnADpC7FAfzwuqlB20i', false, NULL);
INSERT INTO public.personas (id_persona, dni_persona, nombre_persona, apellidos_persona, fec_nacimiento_persona, iban_persona, email_persona, pass_persona, is_admin, id_empresa_persona) VALUES (15, '1111111H', 'Admin', 'BIRT', '1981-06-01', NULL, 'admin@birt.eus', '$2a$10$9r5II6V1Uvvi7tPx8Sx01u2oboIrrLDf4uicBN.orP7jYmZZIv00S', true, 1);
INSERT INTO public.personas (id_persona, dni_persona, nombre_persona, apellidos_persona, fec_nacimiento_persona, iban_persona, email_persona, pass_persona, is_admin, id_empresa_persona) VALUES (60, '55553333T', 'Joritz', 'Gajate Mendizabal', '1999-08-15', 'ES8308208479331748883483', 'joritzgajate@gmail.com', '$2a$10$mSOvZp58j8xul9yCq0txPejJGpAca/rNrMPL3p2j0L8U8/Ja.o02S', false, NULL);
INSERT INTO public.personas (id_persona, dni_persona, nombre_persona, apellidos_persona, fec_nacimiento_persona, iban_persona, email_persona, pass_persona, is_admin, id_empresa_persona) VALUES (61, '12312312K', 'Joritz ', 'Gajate Mendizabal', '1999-08-15', 'ES8301238479331748884583', 'joritz@gmail.com', '$2a$10$CdCKKKUPtQvsQjRU0VOvLeDErw2LHnN582XEcHIm41xiP0FaB2vTq', false, NULL);
INSERT INTO public.personas (id_persona, dni_persona, nombre_persona, apellidos_persona, fec_nacimiento_persona, iban_persona, email_persona, pass_persona, is_admin, id_empresa_persona) VALUES (77, '16071765D', 'Karmel', 'Idarraga Ariño', '1981-01-06', 'ES1234567890123456789012', 'kidarraga@birt.eus', '$2a$10$MBzqFPcG0IjVNc0Qh5QGAeZZMKczE.g5kG5bb6SE5Uydor9wpujUS', false, NULL);
INSERT INTO public.personas (id_persona, dni_persona, nombre_persona, apellidos_persona, fec_nacimiento_persona, iban_persona, email_persona, pass_persona, is_admin, id_empresa_persona) VALUES (62, '23123220B', 'Prueba', 'Prueba', '2003-11-28', 'ES9983233951336692075924', 'prueba@gmail.com', '$2a$10$nvuqaHwKRW0NUeWHmp8IYutiNECkLwtXHzRMVfRyy2xvUuDqyh5Ge', false, NULL);
INSERT INTO public.personas (id_persona, dni_persona, nombre_persona, apellidos_persona, fec_nacimiento_persona, iban_persona, email_persona, pass_persona, is_admin, id_empresa_persona) VALUES (69, '12345678A', 'Jonjklj1', 'Doe2', '1990-05-12', 'ES1234567890123456789012', 'jon.doe1@example.com', '$2a$10$LSDO8SOQKIJVxxKO4IqukOoVGsLgrg1Cok9kTJPeIdR/ywiHoIV4.', false, NULL);
INSERT INTO public.personas (id_persona, dni_persona, nombre_persona, apellidos_persona, fec_nacimiento_persona, iban_persona, email_persona, pass_persona, is_admin, id_empresa_persona) VALUES (70, '12345678A', 'Jon1', 'Doe2', '1990-05-12', 'ES1234567890123456789012', 'jon1.doe1@example.com', '$2a$10$sg8G5rePe53.F7eYNEG3cuDLFEDbgc1SAYr.fBXk7ROrDVLfh0ZbC', false, NULL);
INSERT INTO public.personas (id_persona, dni_persona, nombre_persona, apellidos_persona, fec_nacimiento_persona, iban_persona, email_persona, pass_persona, is_admin, id_empresa_persona) VALUES (73, '11111111H', 'egoitz2', 'Larrea2', '1970-12-02', 'ES7777777777777777777777', 'elarrea@birt.eus', '$2a$10$rOUoltU0TF1Lcv8FZguF0Oy.w/eWwAyZLFLoLQzmeL7tTFV787naK', false, NULL);
INSERT INTO public.personas (id_persona, dni_persona, nombre_persona, apellidos_persona, fec_nacimiento_persona, iban_persona, email_persona, pass_persona, is_admin, id_empresa_persona) VALUES (76, '11111111H', 'Joritz', 'Gajate Mendizabal', '2006-01-03', 'ES1234567890098765432112', 'joritz@gamil.com', '$2a$10$lp51ZUgaO2i/eLPyAzCvcu3iasEIYpYHI3tAXrjVtoeq4W1xYS05.', false, NULL);
INSERT INTO public.personas (id_persona, dni_persona, nombre_persona, apellidos_persona, fec_nacimiento_persona, iban_persona, email_persona, pass_persona, is_admin, id_empresa_persona) VALUES (67, '12345679S', 'Prueba2', 'Prueba Prueba4', '1993-03-12', 'ES1111208479331748883483', 'prueba2@gmail.com', '$2a$10$9CZpxbG6bSeLasPOnukkee4o6outpP4iaLo6f.kcKd8HseBZLSap6', false, NULL);
INSERT INTO public.personas (id_persona, dni_persona, nombre_persona, apellidos_persona, fec_nacimiento_persona, iban_persona, email_persona, pass_persona, is_admin, id_empresa_persona) VALUES (74, '08476195M', 'Nadia', 'D''Alessio', '2000-04-30', 'ES3333333333333333333333', 'ndalessio@birt.eus', '$2a$10$xp4jZtOiWnvknSuh5h/QOOCCFxCOMtrXPSPk7DhzJLSjyjdN8X9Ie', false, NULL);


--
-- TOC entry 4470 (class 0 OID 24670)
-- Dependencies: 224
-- Data for Name: plazas; Type: TABLE DATA; Schema: public; Owner: defaultdb_uk1q_user
--

INSERT INTO public.plazas (id_plaza, id_parking_plaza, nombre_plaza, isvip_plaza, tiene_electricidad_plaza, estado_plaza, precio_plaza) VALUES (1, 1, 'A1', true, true, '0', 25);
INSERT INTO public.plazas (id_plaza, id_parking_plaza, nombre_plaza, isvip_plaza, tiene_electricidad_plaza, estado_plaza, precio_plaza) VALUES (2, 1, 'A2', false, true, '0', 27.5);


--
-- TOC entry 4472 (class 0 OID 24682)
-- Dependencies: 226
-- Data for Name: reservas; Type: TABLE DATA; Schema: public; Owner: defaultdb_uk1q_user
--

INSERT INTO public.reservas (id_reserva, id_persona_reserva, id_plaza_reserva, fecha_inicio_reserva, fecha_fin_reserva, fecha_alta_reserva, estado_reserva, puntuacion_reserva) VALUES (15, 57, 1, '2025-11-22', '2025-11-22', '2025-11-18', '0', NULL);
INSERT INTO public.reservas (id_reserva, id_persona_reserva, id_plaza_reserva, fecha_inicio_reserva, fecha_fin_reserva, fecha_alta_reserva, estado_reserva, puntuacion_reserva) VALUES (13, 57, 1, '2025-11-17', '2025-11-17', '2025-11-17', '1', 8);
INSERT INTO public.reservas (id_reserva, id_persona_reserva, id_plaza_reserva, fecha_inicio_reserva, fecha_fin_reserva, fecha_alta_reserva, estado_reserva, puntuacion_reserva) VALUES (14, 57, 1, '2025-11-18', '2025-11-20', '2025-11-17', '1', 6);
INSERT INTO public.reservas (id_reserva, id_persona_reserva, id_plaza_reserva, fecha_inicio_reserva, fecha_fin_reserva, fecha_alta_reserva, estado_reserva, puntuacion_reserva) VALUES (17, 67, 1, NULL, NULL, '2025-12-11', '1', NULL);
INSERT INTO public.reservas (id_reserva, id_persona_reserva, id_plaza_reserva, fecha_inicio_reserva, fecha_fin_reserva, fecha_alta_reserva, estado_reserva, puntuacion_reserva) VALUES (16, 57, 1, '2025-11-26', '2025-11-28', '2025-10-25', '1', 5);
INSERT INTO public.reservas (id_reserva, id_persona_reserva, id_plaza_reserva, fecha_inicio_reserva, fecha_fin_reserva, fecha_alta_reserva, estado_reserva, puntuacion_reserva) VALUES (20, 67, 2, '2025-12-20', '2025-12-22', '2025-12-17', '0', NULL);
INSERT INTO public.reservas (id_reserva, id_persona_reserva, id_plaza_reserva, fecha_inicio_reserva, fecha_fin_reserva, fecha_alta_reserva, estado_reserva, puntuacion_reserva) VALUES (19, 67, 1, '2025-12-17', '2025-12-17', '2025-12-17', '0', 6);
INSERT INTO public.reservas (id_reserva, id_persona_reserva, id_plaza_reserva, fecha_inicio_reserva, fecha_fin_reserva, fecha_alta_reserva, estado_reserva, puntuacion_reserva) VALUES (18, 67, 1, '2025-12-25', '2025-12-25', '2025-12-11', '0', NULL);
INSERT INTO public.reservas (id_reserva, id_persona_reserva, id_plaza_reserva, fecha_inicio_reserva, fecha_fin_reserva, fecha_alta_reserva, estado_reserva, puntuacion_reserva) VALUES (21, 67, 1, '2025-12-27', '2025-12-28', '2025-12-17', '0', NULL);
INSERT INTO public.reservas (id_reserva, id_persona_reserva, id_plaza_reserva, fecha_inicio_reserva, fecha_fin_reserva, fecha_alta_reserva, estado_reserva, puntuacion_reserva) VALUES (23, 67, 1, '2025-12-18', '2025-12-18', '2025-12-17', '0', NULL);
INSERT INTO public.reservas (id_reserva, id_persona_reserva, id_plaza_reserva, fecha_inicio_reserva, fecha_fin_reserva, fecha_alta_reserva, estado_reserva, puntuacion_reserva) VALUES (22, 67, 2, '2025-12-17', '2025-12-17', '2025-12-17', '0', 7);
INSERT INTO public.reservas (id_reserva, id_persona_reserva, id_plaza_reserva, fecha_inicio_reserva, fecha_fin_reserva, fecha_alta_reserva, estado_reserva, puntuacion_reserva) VALUES (24, 67, 2, '2025-12-30', '2025-12-31', '2025-12-17', '0', NULL);
INSERT INTO public.reservas (id_reserva, id_persona_reserva, id_plaza_reserva, fecha_inicio_reserva, fecha_fin_reserva, fecha_alta_reserva, estado_reserva, puntuacion_reserva) VALUES (25, 67, 2, '2025-12-26', '2025-12-26', '2025-12-17', '0', NULL);
INSERT INTO public.reservas (id_reserva, id_persona_reserva, id_plaza_reserva, fecha_inicio_reserva, fecha_fin_reserva, fecha_alta_reserva, estado_reserva, puntuacion_reserva) VALUES (26, 67, 2, '2025-12-28', '2025-12-28', '2025-12-17', '1', NULL);
INSERT INTO public.reservas (id_reserva, id_persona_reserva, id_plaza_reserva, fecha_inicio_reserva, fecha_fin_reserva, fecha_alta_reserva, estado_reserva, puntuacion_reserva) VALUES (27, 57, 1, '2025-12-23', '2025-12-23', '2025-12-23', '1', NULL);


--
-- TOC entry 4482 (class 0 OID 0)
-- Dependencies: 217
-- Name: empresa_id_empresa_seq; Type: SEQUENCE SET; Schema: public; Owner: defaultdb_uk1q_user
--

SELECT pg_catalog.setval('public.empresa_id_empresa_seq', 2, true);


--
-- TOC entry 4483 (class 0 OID 0)
-- Dependencies: 222
-- Name: parking_id_seq; Type: SEQUENCE SET; Schema: public; Owner: defaultdb_uk1q_user
--

SELECT pg_catalog.setval('public.parking_id_seq', 1, true);


--
-- TOC entry 4484 (class 0 OID 0)
-- Dependencies: 218
-- Name: persona_id_persona_seq; Type: SEQUENCE SET; Schema: public; Owner: defaultdb_uk1q_user
--

SELECT pg_catalog.setval('public.persona_id_persona_seq', 77, true);


--
-- TOC entry 4485 (class 0 OID 0)
-- Dependencies: 223
-- Name: plazas_id_seq; Type: SEQUENCE SET; Schema: public; Owner: defaultdb_uk1q_user
--

SELECT pg_catalog.setval('public.plazas_id_seq', 2, true);


--
-- TOC entry 4486 (class 0 OID 0)
-- Dependencies: 225
-- Name: reservas_id_reserva_seq; Type: SEQUENCE SET; Schema: public; Owner: defaultdb_uk1q_user
--

SELECT pg_catalog.setval('public.reservas_id_reserva_seq', 27, true);


--
-- TOC entry 4302 (class 2606 OID 24607)
-- Name: empresas empresa_pkey; Type: CONSTRAINT; Schema: public; Owner: defaultdb_uk1q_user
--

ALTER TABLE ONLY public.empresas
    ADD CONSTRAINT empresa_pkey PRIMARY KEY (id_empresa);


--
-- TOC entry 4308 (class 2606 OID 24703)
-- Name: parkings parkings_pkey; Type: CONSTRAINT; Schema: public; Owner: defaultdb_uk1q_user
--

ALTER TABLE ONLY public.parkings
    ADD CONSTRAINT parkings_pkey PRIMARY KEY (id_parking);


--
-- TOC entry 4304 (class 2606 OID 24731)
-- Name: personas persona_email_un; Type: CONSTRAINT; Schema: public; Owner: defaultdb_uk1q_user
--

ALTER TABLE ONLY public.personas
    ADD CONSTRAINT persona_email_un UNIQUE (email_persona);


--
-- TOC entry 4306 (class 2606 OID 24717)
-- Name: personas persona_pkey; Type: CONSTRAINT; Schema: public; Owner: defaultdb_uk1q_user
--

ALTER TABLE ONLY public.personas
    ADD CONSTRAINT persona_pkey PRIMARY KEY (id_persona);


--
-- TOC entry 4310 (class 2606 OID 24734)
-- Name: plazas plazas_pkey; Type: CONSTRAINT; Schema: public; Owner: defaultdb_uk1q_user
--

ALTER TABLE ONLY public.plazas
    ADD CONSTRAINT plazas_pkey PRIMARY KEY (id_plaza);


--
-- TOC entry 4312 (class 2606 OID 24759)
-- Name: reservas reservas_pkey; Type: CONSTRAINT; Schema: public; Owner: defaultdb_uk1q_user
--

ALTER TABLE ONLY public.reservas
    ADD CONSTRAINT reservas_pkey PRIMARY KEY (id_reserva);


--
-- TOC entry 4314 (class 2606 OID 24652)
-- Name: parkings parking_empresa_fk; Type: FK CONSTRAINT; Schema: public; Owner: defaultdb_uk1q_user
--

ALTER TABLE ONLY public.parkings
    ADD CONSTRAINT parking_empresa_fk FOREIGN KEY (id_empresa_parking) REFERENCES public.empresas(id_empresa);


--
-- TOC entry 4313 (class 2606 OID 24614)
-- Name: personas persona_empresa; Type: FK CONSTRAINT; Schema: public; Owner: defaultdb_uk1q_user
--

ALTER TABLE ONLY public.personas
    ADD CONSTRAINT persona_empresa FOREIGN KEY (id_empresa_persona) REFERENCES public.empresas(id_empresa);


--
-- TOC entry 4316 (class 2606 OID 24767)
-- Name: reservas persona_reserva_fk; Type: FK CONSTRAINT; Schema: public; Owner: defaultdb_uk1q_user
--

ALTER TABLE ONLY public.reservas
    ADD CONSTRAINT persona_reserva_fk FOREIGN KEY (id_persona_reserva) REFERENCES public.personas(id_persona) ON DELETE CASCADE NOT VALID;


--
-- TOC entry 4317 (class 2606 OID 24776)
-- Name: reservas plaza_reserva_fk; Type: FK CONSTRAINT; Schema: public; Owner: defaultdb_uk1q_user
--

ALTER TABLE ONLY public.reservas
    ADD CONSTRAINT plaza_reserva_fk FOREIGN KEY (id_plaza_reserva) REFERENCES public.plazas(id_plaza) ON DELETE CASCADE NOT VALID;


--
-- TOC entry 4315 (class 2606 OID 24748)
-- Name: plazas plazas_parking_fk; Type: FK CONSTRAINT; Schema: public; Owner: defaultdb_uk1q_user
--

ALTER TABLE ONLY public.plazas
    ADD CONSTRAINT plazas_parking_fk FOREIGN KEY (id_parking_plaza) REFERENCES public.parkings(id_parking) ON DELETE CASCADE NOT VALID;


-- Completed on 2025-12-23 20:06:11

--
-- PostgreSQL database dump complete
--

