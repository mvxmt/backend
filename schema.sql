--
-- PostgreSQL database dump
--

-- Dumped from database version 16.6
-- Dumped by pg_dump version 16.6

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

--
-- Name: document_data; Type: SCHEMA; Schema: -; Owner: postgres
--

CREATE SCHEMA document_data;


ALTER SCHEMA document_data OWNER TO postgres;

--
-- Name: user_data; Type: SCHEMA; Schema: -; Owner: postgres
--

CREATE SCHEMA user_data;


ALTER SCHEMA user_data OWNER TO postgres;

--
-- Name: vector; Type: EXTENSION; Schema: -; Owner: -
--

CREATE EXTENSION IF NOT EXISTS vector WITH SCHEMA public;


--
-- Name: EXTENSION vector; Type: COMMENT; Schema: -; Owner: 
--

COMMENT ON EXTENSION vector IS 'vector data type and ivfflat and hnsw access methods';


SET default_tablespace = '';

SET default_table_access_method = heap;

--
-- Name: chunks; Type: TABLE; Schema: document_data; Owner: postgres
--

CREATE TABLE document_data.chunks (
    id bigint NOT NULL,
    source_id integer,
    chunk_text text,
    chunk_vector public.vector(768)
);


ALTER TABLE document_data.chunks OWNER TO postgres;

--
-- Name: chunks_id_seq; Type: SEQUENCE; Schema: document_data; Owner: postgres
--

CREATE SEQUENCE document_data.chunks_id_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER SEQUENCE document_data.chunks_id_seq OWNER TO postgres;

--
-- Name: chunks_id_seq; Type: SEQUENCE OWNED BY; Schema: document_data; Owner: postgres
--

ALTER SEQUENCE document_data.chunks_id_seq OWNED BY document_data.chunks.id;


--
-- Name: documents; Type: TABLE; Schema: document_data; Owner: postgres
--

CREATE TABLE document_data.documents (
    id integer NOT NULL,
    owner integer,
    filename character varying NOT NULL
);


ALTER TABLE document_data.documents OWNER TO postgres;

--
-- Name: document_id_seq; Type: SEQUENCE; Schema: document_data; Owner: postgres
--

CREATE SEQUENCE document_data.document_id_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER SEQUENCE document_data.document_id_seq OWNER TO postgres;

--
-- Name: document_id_seq; Type: SEQUENCE OWNED BY; Schema: document_data; Owner: postgres
--

ALTER SEQUENCE document_data.document_id_seq OWNED BY document_data.documents.id;


--
-- Name: chat_threads; Type: TABLE; Schema: user_data; Owner: postgres
--

CREATE TABLE user_data.chat_threads (
    user_id integer NOT NULL,
    chat_thread_id uuid NOT NULL,
    thread_data jsonb DEFAULT '[]'::jsonb NOT NULL,
    name text DEFAULT ''::text NOT NULL,
    modified_at timestamp without time zone DEFAULT now() NOT NULL
);


ALTER TABLE user_data.chat_threads OWNER TO postgres;

--
-- Name: users; Type: TABLE; Schema: user_data; Owner: postgres
--

CREATE TABLE user_data.users (
    id integer NOT NULL,
    name character varying(50) NOT NULL,
    email character varying(50) NOT NULL,
    password_hash character varying
);


ALTER TABLE user_data.users OWNER TO postgres;

--
-- Name: users_id_seq; Type: SEQUENCE; Schema: user_data; Owner: postgres
--

CREATE SEQUENCE user_data.users_id_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER SEQUENCE user_data.users_id_seq OWNER TO postgres;

--
-- Name: users_id_seq; Type: SEQUENCE OWNED BY; Schema: user_data; Owner: postgres
--

ALTER SEQUENCE user_data.users_id_seq OWNED BY user_data.users.id;


--
-- Name: chunks id; Type: DEFAULT; Schema: document_data; Owner: postgres
--

ALTER TABLE ONLY document_data.chunks ALTER COLUMN id SET DEFAULT nextval('document_data.chunks_id_seq'::regclass);


--
-- Name: documents id; Type: DEFAULT; Schema: document_data; Owner: postgres
--

ALTER TABLE ONLY document_data.documents ALTER COLUMN id SET DEFAULT nextval('document_data.document_id_seq'::regclass);


--
-- Name: users id; Type: DEFAULT; Schema: user_data; Owner: postgres
--

ALTER TABLE ONLY user_data.users ALTER COLUMN id SET DEFAULT nextval('user_data.users_id_seq'::regclass);


--
-- Name: chunks chunks_pkey; Type: CONSTRAINT; Schema: document_data; Owner: postgres
--

ALTER TABLE ONLY document_data.chunks
    ADD CONSTRAINT chunks_pkey PRIMARY KEY (id);


--
-- Name: documents document_pkey; Type: CONSTRAINT; Schema: document_data; Owner: postgres
--

ALTER TABLE ONLY document_data.documents
    ADD CONSTRAINT document_pkey PRIMARY KEY (id);


--
-- Name: chat_threads chat_threads_pkey; Type: CONSTRAINT; Schema: user_data; Owner: postgres
--

ALTER TABLE ONLY user_data.chat_threads
    ADD CONSTRAINT chat_threads_pkey PRIMARY KEY (user_id, chat_thread_id);


--
-- Name: users users_pkey; Type: CONSTRAINT; Schema: user_data; Owner: postgres
--

ALTER TABLE ONLY user_data.users
    ADD CONSTRAINT users_pkey PRIMARY KEY (id);


--
-- Name: chunks fk_document_id; Type: FK CONSTRAINT; Schema: document_data; Owner: postgres
--

ALTER TABLE ONLY document_data.chunks
    ADD CONSTRAINT fk_document_id FOREIGN KEY (source_id) REFERENCES document_data.documents(id);


--
-- Name: documents fk_owner_user_id; Type: FK CONSTRAINT; Schema: document_data; Owner: postgres
--

ALTER TABLE ONLY document_data.documents
    ADD CONSTRAINT fk_owner_user_id FOREIGN KEY (owner) REFERENCES user_data.users(id);


--
-- Name: chat_threads user_id_fk; Type: FK CONSTRAINT; Schema: user_data; Owner: postgres
--

ALTER TABLE ONLY user_data.chat_threads
    ADD CONSTRAINT user_id_fk FOREIGN KEY (user_id) REFERENCES user_data.users(id) ON UPDATE CASCADE ON DELETE CASCADE;


--
-- Name: SCHEMA document_data; Type: ACL; Schema: -; Owner: postgres
--

GRANT ALL ON SCHEMA document_data TO mvxmt;


--
-- Name: SCHEMA user_data; Type: ACL; Schema: -; Owner: postgres
--

GRANT ALL ON SCHEMA user_data TO mvxmt;


--
-- Name: TABLE chunks; Type: ACL; Schema: document_data; Owner: postgres
--

GRANT ALL ON TABLE document_data.chunks TO mvxmt;


--
-- Name: TABLE documents; Type: ACL; Schema: document_data; Owner: postgres
--

GRANT ALL ON TABLE document_data.documents TO mvxmt;


--
-- Name: TABLE users; Type: ACL; Schema: user_data; Owner: postgres
--

GRANT ALL ON TABLE user_data.users TO mvxmt;


--
-- PostgreSQL database dump complete
--