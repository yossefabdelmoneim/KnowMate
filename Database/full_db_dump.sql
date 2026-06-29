--
-- PostgreSQL database dump
--

\restrict NmzDblEqtF3oCgj6nc6Hknjxe3yeAjcR9l09mZby2eiLNCrj3hqSCJ1Buq14on6

-- Dumped from database version 18.0
-- Dumped by pg_dump version 18.0

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
-- Name: companies; Type: TABLE; Schema: public; Owner: knowmate
--

CREATE TABLE public.companies (
    id integer NOT NULL,
    name character varying(255) NOT NULL,
    description text,
    created_at timestamp with time zone DEFAULT now()
);


ALTER TABLE public.companies OWNER TO knowmate;

--
-- Name: companies_id_seq; Type: SEQUENCE; Schema: public; Owner: knowmate
--

CREATE SEQUENCE public.companies_id_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER SEQUENCE public.companies_id_seq OWNER TO knowmate;

--
-- Name: companies_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: knowmate
--

ALTER SEQUENCE public.companies_id_seq OWNED BY public.companies.id;


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
-- Name: users; Type: TABLE; Schema: public; Owner: knowmate
--

CREATE TABLE public.users (
    id integer NOT NULL,
    email character varying(255) NOT NULL,
    hashed_password character varying(255) NOT NULL,
    full_name character varying(255),
    company_id integer,
    created_at timestamp with time zone DEFAULT now(),
    role character varying(50) DEFAULT 'employee'::character varying NOT NULL
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
-- Name: chat_messages id; Type: DEFAULT; Schema: public; Owner: knowmate
--

ALTER TABLE ONLY public.chat_messages ALTER COLUMN id SET DEFAULT nextval('public.chat_messages_id_seq'::regclass);


--
-- Name: chat_sessions id; Type: DEFAULT; Schema: public; Owner: knowmate
--

ALTER TABLE ONLY public.chat_sessions ALTER COLUMN id SET DEFAULT nextval('public.chat_sessions_id_seq'::regclass);


--
-- Name: companies id; Type: DEFAULT; Schema: public; Owner: knowmate
--

ALTER TABLE ONLY public.companies ALTER COLUMN id SET DEFAULT nextval('public.companies_id_seq'::regclass);


--
-- Name: documents id; Type: DEFAULT; Schema: public; Owner: knowmate
--

ALTER TABLE ONLY public.documents ALTER COLUMN id SET DEFAULT nextval('public.documents_id_seq'::regclass);


--
-- Name: users id; Type: DEFAULT; Schema: public; Owner: knowmate
--

ALTER TABLE ONLY public.users ALTER COLUMN id SET DEFAULT nextval('public.users_id_seq'::regclass);


--
-- Data for Name: chat_messages; Type: TABLE DATA; Schema: public; Owner: knowmate
--

COPY public.chat_messages (id, session_id, role, content, sources, created_at) FROM stdin;
\.


--
-- Data for Name: chat_sessions; Type: TABLE DATA; Schema: public; Owner: knowmate
--

COPY public.chat_sessions (id, user_id, title, created_at) FROM stdin;
\.


--
-- Data for Name: companies; Type: TABLE DATA; Schema: public; Owner: knowmate
--

COPY public.companies (id, name, description, created_at) FROM stdin;
\.


--
-- Data for Name: documents; Type: TABLE DATA; Schema: public; Owner: knowmate
--

COPY public.documents (id, user_id, company_id, filename, file_path, doc_id, chunks, created_at) FROM stdin;
\.


--
-- Data for Name: users; Type: TABLE DATA; Schema: public; Owner: knowmate
--

COPY public.users (id, email, hashed_password, full_name, company_id, created_at, role) FROM stdin;
\.


--
-- Name: chat_messages_id_seq; Type: SEQUENCE SET; Schema: public; Owner: knowmate
--

SELECT pg_catalog.setval('public.chat_messages_id_seq', 1, false);


--
-- Name: chat_sessions_id_seq; Type: SEQUENCE SET; Schema: public; Owner: knowmate
--

SELECT pg_catalog.setval('public.chat_sessions_id_seq', 1, false);


--
-- Name: companies_id_seq; Type: SEQUENCE SET; Schema: public; Owner: knowmate
--

SELECT pg_catalog.setval('public.companies_id_seq', 1, false);


--
-- Name: documents_id_seq; Type: SEQUENCE SET; Schema: public; Owner: knowmate
--

SELECT pg_catalog.setval('public.documents_id_seq', 1, false);


--
-- Name: users_id_seq; Type: SEQUENCE SET; Schema: public; Owner: knowmate
--

SELECT pg_catalog.setval('public.users_id_seq', 1, false);


--
-- Name: chat_messages chat_messages_pkey; Type: CONSTRAINT; Schema: public; Owner: knowmate
--

ALTER TABLE ONLY public.chat_messages
    ADD CONSTRAINT chat_messages_pkey PRIMARY KEY (id);


--
-- Name: chat_sessions chat_sessions_pkey; Type: CONSTRAINT; Schema: public; Owner: knowmate
--

ALTER TABLE ONLY public.chat_sessions
    ADD CONSTRAINT chat_sessions_pkey PRIMARY KEY (id);


--
-- Name: companies companies_pkey; Type: CONSTRAINT; Schema: public; Owner: knowmate
--

ALTER TABLE ONLY public.companies
    ADD CONSTRAINT companies_pkey PRIMARY KEY (id);


--
-- Name: documents documents_pkey; Type: CONSTRAINT; Schema: public; Owner: knowmate
--

ALTER TABLE ONLY public.documents
    ADD CONSTRAINT documents_pkey PRIMARY KEY (id);


--
-- Name: users users_pkey; Type: CONSTRAINT; Schema: public; Owner: knowmate
--

ALTER TABLE ONLY public.users
    ADD CONSTRAINT users_pkey PRIMARY KEY (id);


--
-- Name: ix_chat_messages_id; Type: INDEX; Schema: public; Owner: knowmate
--

CREATE INDEX ix_chat_messages_id ON public.chat_messages USING btree (id);


--
-- Name: ix_chat_sessions_id; Type: INDEX; Schema: public; Owner: knowmate
--

CREATE INDEX ix_chat_sessions_id ON public.chat_sessions USING btree (id);


--
-- Name: ix_companies_id; Type: INDEX; Schema: public; Owner: knowmate
--

CREATE INDEX ix_companies_id ON public.companies USING btree (id);


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
-- Name: ix_users_email; Type: INDEX; Schema: public; Owner: knowmate
--

CREATE UNIQUE INDEX ix_users_email ON public.users USING btree (email);


--
-- Name: ix_users_id; Type: INDEX; Schema: public; Owner: knowmate
--

CREATE INDEX ix_users_id ON public.users USING btree (id);


--
-- Name: chat_messages chat_messages_session_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: knowmate
--

ALTER TABLE ONLY public.chat_messages
    ADD CONSTRAINT chat_messages_session_id_fkey FOREIGN KEY (session_id) REFERENCES public.chat_sessions(id);


--
-- Name: chat_sessions chat_sessions_user_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: knowmate
--

ALTER TABLE ONLY public.chat_sessions
    ADD CONSTRAINT chat_sessions_user_id_fkey FOREIGN KEY (user_id) REFERENCES public.users(id);


--
-- Name: documents documents_user_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: knowmate
--

ALTER TABLE ONLY public.documents
    ADD CONSTRAINT documents_user_id_fkey FOREIGN KEY (user_id) REFERENCES public.users(id);


--
-- Name: users users_company_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: knowmate
--

ALTER TABLE ONLY public.users
    ADD CONSTRAINT users_company_id_fkey FOREIGN KEY (company_id) REFERENCES public.companies(id);


--
-- PostgreSQL database dump complete
--

\unrestrict NmzDblEqtF3oCgj6nc6Hknjxe3yeAjcR9l09mZby2eiLNCrj3hqSCJ1Buq14on6

