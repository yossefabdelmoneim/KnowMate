--
-- PostgreSQL database dump
--

\restrict 64JXO5cuBjiDjqPjH9yHmZkDcug3yZXYKrmgKYFEKzjbX6bNTZiz2tDi5jKXQPx

-- Dumped from database version 16.14 (Debian 16.14-1.pgdg13+1)
-- Dumped by pg_dump version 16.14 (Debian 16.14-1.pgdg13+1)

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

SET default_tablespace = '';

SET default_table_access_method = heap;

--
-- Name: users; Type: TABLE; Schema: public; Owner: knowmate
--

CREATE TABLE public.users (
    id integer NOT NULL,
    email character varying(255) NOT NULL,
    hashed_password character varying(255) NOT NULL,
    full_name character varying(255),
    created_at timestamp with time zone DEFAULT now()
);


ALTER TABLE public.users OWNER TO knowmate;

--
-- Name: users_id_seq; Type: SEQUENCE; Schema: public; Owner: knowmate
--

CREATE SEQUENCE public.users_id_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER SEQUENCE public.users_id_seq OWNER TO knowmate;

--
-- Name: users_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: knowmate
--

ALTER SEQUENCE public.users_id_seq OWNED BY public.users.id;


--
-- Name: users id; Type: DEFAULT; Schema: public; Owner: knowmate
--

ALTER TABLE ONLY public.users ALTER COLUMN id SET DEFAULT nextval('public.users_id_seq'::regclass);


--
-- Data for Name: users; Type: TABLE DATA; Schema: public; Owner: knowmate
--

COPY public.users (id, email, hashed_password, full_name, created_at) FROM stdin;
1	moazabuelabass@gmail.com	$2b$12$VsGvSKtZ9KuOgTQobDJqsuT9D5O/E.iLqXsLu7wNKFZtwBqKkBkqW	moaz abuelabass	2026-06-24 18:39:48.719717+00
\.


--
-- Name: users_id_seq; Type: SEQUENCE SET; Schema: public; Owner: knowmate
--

SELECT pg_catalog.setval('public.users_id_seq', 1, true);


--
-- Name: users users_pkey; Type: CONSTRAINT; Schema: public; Owner: knowmate
--

ALTER TABLE ONLY public.users
    ADD CONSTRAINT users_pkey PRIMARY KEY (id);


--
-- Name: ix_users_email; Type: INDEX; Schema: public; Owner: knowmate
--

CREATE UNIQUE INDEX ix_users_email ON public.users USING btree (email);


--
-- Name: ix_users_id; Type: INDEX; Schema: public; Owner: knowmate
--

CREATE INDEX ix_users_id ON public.users USING btree (id);


--
-- PostgreSQL database dump complete
--

\unrestrict 64JXO5cuBjiDjqPjH9yHmZkDcug3yZXYKrmgKYFEKzjbX6bNTZiz2tDi5jKXQPx

