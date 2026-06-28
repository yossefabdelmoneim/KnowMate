--
-- PostgreSQL database dump
--

\restrict 5hRI7mJwfigbhfN152tWyy00oDShH2JeNETZgwbSWxb3nMDLgUdsRYD3HBq7kqW

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
-- Name: chat_sessions; Type: TABLE; Schema: public; Owner: knowmate
--

CREATE TABLE public.chat_sessions (
    id integer NOT NULL,
    user_id integer NOT NULL,
    title character varying(255),
    created_at timestamp with time zone DEFAULT now()
);


ALTER TABLE public.chat_sessions OWNER TO knowmate;

--
-- Name: chat_sessions_id_seq; Type: SEQUENCE; Schema: public; Owner: knowmate
--

CREATE SEQUENCE public.chat_sessions_id_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER SEQUENCE public.chat_sessions_id_seq OWNER TO knowmate;

--
-- Name: chat_sessions_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: knowmate
--

ALTER SEQUENCE public.chat_sessions_id_seq OWNED BY public.chat_sessions.id;


--
-- Name: chat_sessions id; Type: DEFAULT; Schema: public; Owner: knowmate
--

ALTER TABLE ONLY public.chat_sessions ALTER COLUMN id SET DEFAULT nextval('public.chat_sessions_id_seq'::regclass);


--
-- Data for Name: chat_sessions; Type: TABLE DATA; Schema: public; Owner: knowmate
--

COPY public.chat_sessions (id, user_id, title, created_at) FROM stdin;
\.


--
-- Name: chat_sessions_id_seq; Type: SEQUENCE SET; Schema: public; Owner: knowmate
--

SELECT pg_catalog.setval('public.chat_sessions_id_seq', 1, false);


--
-- Name: chat_sessions chat_sessions_pkey; Type: CONSTRAINT; Schema: public; Owner: knowmate
--

ALTER TABLE ONLY public.chat_sessions
    ADD CONSTRAINT chat_sessions_pkey PRIMARY KEY (id);


--
-- Name: ix_chat_sessions_id; Type: INDEX; Schema: public; Owner: knowmate
--

CREATE INDEX ix_chat_sessions_id ON public.chat_sessions USING btree (id);


--
-- Name: chat_sessions chat_sessions_user_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: knowmate
--

ALTER TABLE ONLY public.chat_sessions
    ADD CONSTRAINT chat_sessions_user_id_fkey FOREIGN KEY (user_id) REFERENCES public.users(id);


--
-- PostgreSQL database dump complete
--

\unrestrict 5hRI7mJwfigbhfN152tWyy00oDShH2JeNETZgwbSWxb3nMDLgUdsRYD3HBq7kqW

