--
-- PostgreSQL database dump
--

\restrict g8yNeMfGsoBKFSSbsLAP2dkZLMVltfuXE5AyIMwrtfiEesIPuMCRs0sSX7Nh5fm

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
-- Name: chat_messages; Type: TABLE; Schema: public; Owner: knowmate
--

CREATE TABLE public.chat_messages (
    id integer NOT NULL,
    session_id integer NOT NULL,
    role character varying(50) NOT NULL,
    content text NOT NULL,
    sources text,
    created_at timestamp with time zone DEFAULT now()
);


ALTER TABLE public.chat_messages OWNER TO knowmate;

--
-- Name: chat_messages_id_seq; Type: SEQUENCE; Schema: public; Owner: knowmate
--

CREATE SEQUENCE public.chat_messages_id_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER SEQUENCE public.chat_messages_id_seq OWNER TO knowmate;

--
-- Name: chat_messages_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: knowmate
--

ALTER SEQUENCE public.chat_messages_id_seq OWNED BY public.chat_messages.id;


--
-- Name: chat_messages id; Type: DEFAULT; Schema: public; Owner: knowmate
--

ALTER TABLE ONLY public.chat_messages ALTER COLUMN id SET DEFAULT nextval('public.chat_messages_id_seq'::regclass);


--
-- Data for Name: chat_messages; Type: TABLE DATA; Schema: public; Owner: knowmate
--

COPY public.chat_messages (id, session_id, role, content, sources, created_at) FROM stdin;
\.


--
-- Name: chat_messages_id_seq; Type: SEQUENCE SET; Schema: public; Owner: knowmate
--

SELECT pg_catalog.setval('public.chat_messages_id_seq', 1, false);


--
-- Name: chat_messages chat_messages_pkey; Type: CONSTRAINT; Schema: public; Owner: knowmate
--

ALTER TABLE ONLY public.chat_messages
    ADD CONSTRAINT chat_messages_pkey PRIMARY KEY (id);


--
-- Name: ix_chat_messages_id; Type: INDEX; Schema: public; Owner: knowmate
--

CREATE INDEX ix_chat_messages_id ON public.chat_messages USING btree (id);


--
-- Name: chat_messages chat_messages_session_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: knowmate
--

ALTER TABLE ONLY public.chat_messages
    ADD CONSTRAINT chat_messages_session_id_fkey FOREIGN KEY (session_id) REFERENCES public.chat_sessions(id);


--
-- PostgreSQL database dump complete
--

\unrestrict g8yNeMfGsoBKFSSbsLAP2dkZLMVltfuXE5AyIMwrtfiEesIPuMCRs0sSX7Nh5fm

