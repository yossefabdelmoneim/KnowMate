--
-- PostgreSQL database dump
--

\restrict jba62yi5JiMsn8nlZZ2Hrw0Djede0BUAARMPIQ8Dmx2zf2bUMY4UM1p53YyRS7J

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
-- Name: documents; Type: TABLE; Schema: public; Owner: knowmate
--

CREATE TABLE public.documents (
    id integer NOT NULL,
    user_id integer NOT NULL,
    company_id character varying(255) NOT NULL,
    filename character varying(255) NOT NULL,
    file_path text NOT NULL,
    doc_id character varying(255) NOT NULL,
    chunks integer NOT NULL,
    created_at timestamp with time zone DEFAULT now()
);


ALTER TABLE public.documents OWNER TO knowmate;

--
-- Name: documents_id_seq; Type: SEQUENCE; Schema: public; Owner: knowmate
--

CREATE SEQUENCE public.documents_id_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER SEQUENCE public.documents_id_seq OWNER TO knowmate;

--
-- Name: documents_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: knowmate
--

ALTER SEQUENCE public.documents_id_seq OWNED BY public.documents.id;


--
-- Name: documents id; Type: DEFAULT; Schema: public; Owner: knowmate
--

ALTER TABLE ONLY public.documents ALTER COLUMN id SET DEFAULT nextval('public.documents_id_seq'::regclass);


--
-- Data for Name: documents; Type: TABLE DATA; Schema: public; Owner: knowmate
--

COPY public.documents (id, user_id, company_id, filename, file_path, doc_id, chunks, created_at) FROM stdin;
\.


--
-- Name: documents_id_seq; Type: SEQUENCE SET; Schema: public; Owner: knowmate
--

SELECT pg_catalog.setval('public.documents_id_seq', 1, false);


--
-- Name: documents documents_pkey; Type: CONSTRAINT; Schema: public; Owner: knowmate
--

ALTER TABLE ONLY public.documents
    ADD CONSTRAINT documents_pkey PRIMARY KEY (id);


--
-- Name: ix_documents_company_id; Type: INDEX; Schema: public; Owner: knowmate
--

CREATE INDEX ix_documents_company_id ON public.documents USING btree (company_id);


--
-- Name: ix_documents_doc_id; Type: INDEX; Schema: public; Owner: knowmate
--

CREATE UNIQUE INDEX ix_documents_doc_id ON public.documents USING btree (doc_id);


--
-- Name: ix_documents_id; Type: INDEX; Schema: public; Owner: knowmate
--

CREATE INDEX ix_documents_id ON public.documents USING btree (id);


--
-- Name: documents documents_user_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: knowmate
--

ALTER TABLE ONLY public.documents
    ADD CONSTRAINT documents_user_id_fkey FOREIGN KEY (user_id) REFERENCES public.users(id);


--
-- PostgreSQL database dump complete
--

\unrestrict jba62yi5JiMsn8nlZZ2Hrw0Djede0BUAARMPIQ8Dmx2zf2bUMY4UM1p53YyRS7J

