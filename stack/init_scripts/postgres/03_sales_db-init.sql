--
-- postgresQL Northwind Database v1.0 from Ramiro Estigarribia Canese  
-- you may contact him at email   ramiro.estigarribia@rieder.com.py 
--
CREATE DATABASE sales_db;

-- Connect to it and create tables
\connect sales_db;


SET statement_timeout = 0;
SET client_encoding = 'UTF8';
SET standard_conforming_strings = on;
SET check_function_bodies = false;
SET client_min_messages = warning;

--
-- Name: plpgsql; Type: EXTENSION; Schema: -; Owner: 
--

CREATE EXTENSION IF NOT EXISTS plpgsql WITH SCHEMA pg_catalog;


--
-- Name: EXTENSION plpgsql; Type: COMMENT; Schema: -; Owner: 
--

COMMENT ON EXTENSION plpgsql IS 'PL/pgSQL procedural language';


SET search_path = public, pg_catalog;

SET default_tablespace = '';

SET default_with_oids = false;


CREATE TABLE customer_sales_data (
    "customer_id" VARCHAR(10) PRIMARY KEY,
    "customer_name" VARCHAR(100),
    "region" VARCHAR(50),
    "sale_date" DATE,
    "sale_amount" NUMERIC(10,2),
    "product" VARCHAR(100)
);


ALTER TABLE public.customer_sales_data OWNER TO postgres;



CREATE TABLE regional_commision (
    "region_name" VARCHAR(10) PRIMARY KEY,
    "sale_commision" NUMERIC(10,2)
);


ALTER TABLE public.regional_commision OWNER TO postgres;



--
-- Data for Name: regional_commision; Type: TABLE DATA; Schema: public; Owner: postgres
--

INSERT INTO regional_commision VALUES ('North', 0.2);
INSERT INTO regional_commision VALUES ('West', 0.8);
INSERT INTO regional_commision VALUES ('South', 0.33);
INSERT INTO regional_commision VALUES ('East', 0.8);
