--
-- PostgreSQL database dump
--

\restrict NcVndGb3jxxh8P2W3y0pTidrPQfbVd02Tu9sExP4KP0JGmwrqLrNpfJyhiOfM2a

-- Dumped from database version 15.14
-- Dumped by pg_dump version 15.14

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

ALTER TABLE IF EXISTS ONLY public.user_typing_status DROP CONSTRAINT IF EXISTS user_typing_status_user_id_fkey;
ALTER TABLE IF EXISTS ONLY public.user_typing_status DROP CONSTRAINT IF EXISTS user_typing_status_conversation_id_fkey;
ALTER TABLE IF EXISTS ONLY public.user_presence DROP CONSTRAINT IF EXISTS user_presence_user_id_fkey;
ALTER TABLE IF EXISTS ONLY public.refresh_tokens DROP CONSTRAINT IF EXISTS refresh_tokens_user_id_fkey;
ALTER TABLE IF EXISTS ONLY public.plants DROP CONSTRAINT IF EXISTS plants_owner_id_fkey;
ALTER TABLE IF EXISTS ONLY public.plant_cares DROP CONSTRAINT IF EXISTS plant_cares_plant_id_fkey;
ALTER TABLE IF EXISTS ONLY public.plant_cares DROP CONSTRAINT IF EXISTS plant_cares_owner_id_fkey;
ALTER TABLE IF EXISTS ONLY public.plant_cares DROP CONSTRAINT IF EXISTS plant_cares_conversation_id_fkey;
ALTER TABLE IF EXISTS ONLY public.plant_cares DROP CONSTRAINT IF EXISTS plant_cares_caretaker_id_fkey;
ALTER TABLE IF EXISTS ONLY public.photos DROP CONSTRAINT IF EXISTS photos_plant_id_fkey;
ALTER TABLE IF EXISTS ONLY public.messages DROP CONSTRAINT IF EXISTS messages_sender_id_fkey;
ALTER TABLE IF EXISTS ONLY public.messages DROP CONSTRAINT IF EXISTS messages_conversation_id_fkey;
ALTER TABLE IF EXISTS ONLY public.conversation_participants DROP CONSTRAINT IF EXISTS conversation_participants_user_id_fkey;
ALTER TABLE IF EXISTS ONLY public.conversation_participants DROP CONSTRAINT IF EXISTS conversation_participants_conversation_id_fkey;
ALTER TABLE IF EXISTS ONLY public.care_reports DROP CONSTRAINT IF EXISTS care_reports_plant_care_id_fkey;
ALTER TABLE IF EXISTS ONLY public.care_reports DROP CONSTRAINT IF EXISTS care_reports_caretaker_id_fkey;
ALTER TABLE IF EXISTS ONLY public.botanist_report_advices DROP CONSTRAINT IF EXISTS botanist_report_advices_care_report_id_fkey;
ALTER TABLE IF EXISTS ONLY public.botanist_report_advices DROP CONSTRAINT IF EXISTS botanist_report_advices_botanist_id_fkey;
ALTER TABLE IF EXISTS ONLY public.advices DROP CONSTRAINT IF EXISTS advices_validator_id_fkey;
ALTER TABLE IF EXISTS ONLY public.advices DROP CONSTRAINT IF EXISTS advices_previous_version_id_fkey;
ALTER TABLE IF EXISTS ONLY public.advices DROP CONSTRAINT IF EXISTS advices_plant_care_id_fkey;
ALTER TABLE IF EXISTS ONLY public.advices DROP CONSTRAINT IF EXISTS advices_botanist_id_fkey;
DROP INDEX IF EXISTS public.ix_refresh_tokens_token;
ALTER TABLE IF EXISTS ONLY public.users DROP CONSTRAINT IF EXISTS users_pkey;
ALTER TABLE IF EXISTS ONLY public.users DROP CONSTRAINT IF EXISTS users_email_key;
ALTER TABLE IF EXISTS ONLY public.user_typing_status DROP CONSTRAINT IF EXISTS user_typing_status_pkey;
ALTER TABLE IF EXISTS ONLY public.user_presence DROP CONSTRAINT IF EXISTS user_presence_user_id_key;
ALTER TABLE IF EXISTS ONLY public.user_presence DROP CONSTRAINT IF EXISTS user_presence_pkey;
ALTER TABLE IF EXISTS ONLY public.conversation_participants DROP CONSTRAINT IF EXISTS unique_conversation_participant;
ALTER TABLE IF EXISTS ONLY public.refresh_tokens DROP CONSTRAINT IF EXISTS refresh_tokens_pkey;
ALTER TABLE IF EXISTS ONLY public.plants DROP CONSTRAINT IF EXISTS plants_pkey;
ALTER TABLE IF EXISTS ONLY public.plant_cares DROP CONSTRAINT IF EXISTS plant_cares_pkey;
ALTER TABLE IF EXISTS ONLY public.photos DROP CONSTRAINT IF EXISTS photos_pkey;
ALTER TABLE IF EXISTS ONLY public.messages DROP CONSTRAINT IF EXISTS messages_pkey;
ALTER TABLE IF EXISTS ONLY public.conversations DROP CONSTRAINT IF EXISTS conversations_pkey;
ALTER TABLE IF EXISTS ONLY public.conversation_participants DROP CONSTRAINT IF EXISTS conversation_participants_pkey;
ALTER TABLE IF EXISTS ONLY public.care_reports DROP CONSTRAINT IF EXISTS care_reports_pkey;
ALTER TABLE IF EXISTS ONLY public.botanist_report_advices DROP CONSTRAINT IF EXISTS botanist_report_advices_pkey;
ALTER TABLE IF EXISTS ONLY public.alembic_version DROP CONSTRAINT IF EXISTS alembic_version_pkc;
ALTER TABLE IF EXISTS ONLY public.advices DROP CONSTRAINT IF EXISTS advices_pkey;
ALTER TABLE IF EXISTS public.users ALTER COLUMN id DROP DEFAULT;
ALTER TABLE IF EXISTS public.user_typing_status ALTER COLUMN id DROP DEFAULT;
ALTER TABLE IF EXISTS public.user_presence ALTER COLUMN id DROP DEFAULT;
ALTER TABLE IF EXISTS public.refresh_tokens ALTER COLUMN id DROP DEFAULT;
ALTER TABLE IF EXISTS public.plants ALTER COLUMN id DROP DEFAULT;
ALTER TABLE IF EXISTS public.plant_cares ALTER COLUMN id DROP DEFAULT;
ALTER TABLE IF EXISTS public.photos ALTER COLUMN id DROP DEFAULT;
ALTER TABLE IF EXISTS public.messages ALTER COLUMN id DROP DEFAULT;
ALTER TABLE IF EXISTS public.conversations ALTER COLUMN id DROP DEFAULT;
ALTER TABLE IF EXISTS public.conversation_participants ALTER COLUMN id DROP DEFAULT;
ALTER TABLE IF EXISTS public.care_reports ALTER COLUMN id DROP DEFAULT;
ALTER TABLE IF EXISTS public.botanist_report_advices ALTER COLUMN id DROP DEFAULT;
ALTER TABLE IF EXISTS public.advices ALTER COLUMN id DROP DEFAULT;
DROP SEQUENCE IF EXISTS public.users_id_seq;
DROP TABLE IF EXISTS public.users;
DROP SEQUENCE IF EXISTS public.user_typing_status_id_seq;
DROP TABLE IF EXISTS public.user_typing_status;
DROP SEQUENCE IF EXISTS public.user_presence_id_seq;
DROP TABLE IF EXISTS public.user_presence;
DROP SEQUENCE IF EXISTS public.refresh_tokens_id_seq;
DROP TABLE IF EXISTS public.refresh_tokens;
DROP SEQUENCE IF EXISTS public.plants_id_seq;
DROP TABLE IF EXISTS public.plants;
DROP SEQUENCE IF EXISTS public.plant_cares_id_seq;
DROP TABLE IF EXISTS public.plant_cares;
DROP SEQUENCE IF EXISTS public.photos_id_seq;
DROP TABLE IF EXISTS public.photos;
DROP SEQUENCE IF EXISTS public.messages_id_seq;
DROP TABLE IF EXISTS public.messages;
DROP SEQUENCE IF EXISTS public.conversations_id_seq;
DROP TABLE IF EXISTS public.conversations;
DROP SEQUENCE IF EXISTS public.conversation_participants_id_seq;
DROP TABLE IF EXISTS public.conversation_participants;
DROP SEQUENCE IF EXISTS public.care_reports_id_seq;
DROP TABLE IF EXISTS public.care_reports;
DROP SEQUENCE IF EXISTS public.botanist_report_advices_id_seq;
DROP TABLE IF EXISTS public.botanist_report_advices;
DROP TABLE IF EXISTS public.alembic_version;
DROP SEQUENCE IF EXISTS public.advices_id_seq;
DROP TABLE IF EXISTS public.advices;
DROP TYPE IF EXISTS public.validationstatus;
DROP TYPE IF EXISTS public.userstatus;
DROP TYPE IF EXISTS public.userrole;
DROP TYPE IF EXISTS public.healthlevel;
DROP TYPE IF EXISTS public.conversationtype;
DROP TYPE IF EXISTS public.carestatus;
DROP TYPE IF EXISTS public.advicepriority;
--
-- Name: advicepriority; Type: TYPE; Schema: public; Owner: arosaje
--

CREATE TYPE public.advicepriority AS ENUM (
    'NORMAL',
    'URGENT',
    'FOLLOW_UP'
);


ALTER TYPE public.advicepriority OWNER TO arosaje;

--
-- Name: carestatus; Type: TYPE; Schema: public; Owner: arosaje
--

CREATE TYPE public.carestatus AS ENUM (
    'PENDING',
    'ACCEPTED',
    'REFUSED',
    'IN_PROGRESS',
    'COMPLETED',
    'CANCELLED'
);


ALTER TYPE public.carestatus OWNER TO arosaje;

--
-- Name: conversationtype; Type: TYPE; Schema: public; Owner: arosaje
--

CREATE TYPE public.conversationtype AS ENUM (
    'PLANT_CARE',
    'BOTANICAL_ADVICE'
);


ALTER TYPE public.conversationtype OWNER TO arosaje;

--
-- Name: healthlevel; Type: TYPE; Schema: public; Owner: arosaje
--

CREATE TYPE public.healthlevel AS ENUM (
    'BAS',
    'MOYEN',
    'BON'
);


ALTER TYPE public.healthlevel OWNER TO arosaje;

--
-- Name: userrole; Type: TYPE; Schema: public; Owner: arosaje
--

CREATE TYPE public.userrole AS ENUM (
    'USER',
    'BOTANIST',
    'ADMIN'
);


ALTER TYPE public.userrole OWNER TO arosaje;

--
-- Name: userstatus; Type: TYPE; Schema: public; Owner: arosaje
--

CREATE TYPE public.userstatus AS ENUM (
    'ONLINE',
    'OFFLINE',
    'AWAY'
);


ALTER TYPE public.userstatus OWNER TO arosaje;

--
-- Name: validationstatus; Type: TYPE; Schema: public; Owner: arosaje
--

CREATE TYPE public.validationstatus AS ENUM (
    'PENDING',
    'VALIDATED',
    'REJECTED',
    'NEEDS_REVISION'
);


ALTER TYPE public.validationstatus OWNER TO arosaje;

SET default_tablespace = '';

SET default_table_access_method = heap;

--
-- Name: advices; Type: TABLE; Schema: public; Owner: arosaje
--

CREATE TABLE public.advices (
    id integer NOT NULL,
    plant_care_id integer NOT NULL,
    botanist_id integer NOT NULL,
    title character varying(255) NOT NULL,
    content text NOT NULL,
    priority public.advicepriority,
    validation_status public.validationstatus,
    validator_id integer,
    validation_comment text,
    validated_at timestamp without time zone,
    version integer,
    is_current_version boolean,
    previous_version_id integer,
    owner_notified boolean,
    botanist_notified boolean,
    created_at timestamp without time zone,
    updated_at timestamp without time zone
);


ALTER TABLE public.advices OWNER TO arosaje;

--
-- Name: advices_id_seq; Type: SEQUENCE; Schema: public; Owner: arosaje
--

CREATE SEQUENCE public.advices_id_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER TABLE public.advices_id_seq OWNER TO arosaje;

--
-- Name: advices_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: arosaje
--

ALTER SEQUENCE public.advices_id_seq OWNED BY public.advices.id;


--
-- Name: alembic_version; Type: TABLE; Schema: public; Owner: arosaje
--

CREATE TABLE public.alembic_version (
    version_num character varying(32) NOT NULL
);


ALTER TABLE public.alembic_version OWNER TO arosaje;

--
-- Name: botanist_report_advices; Type: TABLE; Schema: public; Owner: arosaje
--

CREATE TABLE public.botanist_report_advices (
    id integer NOT NULL,
    care_report_id integer NOT NULL,
    botanist_id integer NOT NULL,
    advice_text text NOT NULL,
    created_at timestamp without time zone,
    updated_at timestamp without time zone
);


ALTER TABLE public.botanist_report_advices OWNER TO arosaje;

--
-- Name: botanist_report_advices_id_seq; Type: SEQUENCE; Schema: public; Owner: arosaje
--

CREATE SEQUENCE public.botanist_report_advices_id_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER TABLE public.botanist_report_advices_id_seq OWNER TO arosaje;

--
-- Name: botanist_report_advices_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: arosaje
--

ALTER SEQUENCE public.botanist_report_advices_id_seq OWNED BY public.botanist_report_advices.id;


--
-- Name: care_reports; Type: TABLE; Schema: public; Owner: arosaje
--

CREATE TABLE public.care_reports (
    id integer NOT NULL,
    plant_care_id integer NOT NULL,
    caretaker_id integer NOT NULL,
    session_date timestamp without time zone NOT NULL,
    photo_url character varying,
    health_level public.healthlevel NOT NULL,
    hydration_level public.healthlevel NOT NULL,
    vitality_level public.healthlevel NOT NULL,
    description text,
    created_at timestamp without time zone,
    updated_at timestamp without time zone
);


ALTER TABLE public.care_reports OWNER TO arosaje;

--
-- Name: care_reports_id_seq; Type: SEQUENCE; Schema: public; Owner: arosaje
--

CREATE SEQUENCE public.care_reports_id_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER TABLE public.care_reports_id_seq OWNER TO arosaje;

--
-- Name: care_reports_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: arosaje
--

ALTER SEQUENCE public.care_reports_id_seq OWNED BY public.care_reports.id;


--
-- Name: conversation_participants; Type: TABLE; Schema: public; Owner: arosaje
--

CREATE TABLE public.conversation_participants (
    id integer NOT NULL,
    conversation_id integer NOT NULL,
    user_id integer NOT NULL,
    last_read_at timestamp without time zone
);


ALTER TABLE public.conversation_participants OWNER TO arosaje;

--
-- Name: conversation_participants_id_seq; Type: SEQUENCE; Schema: public; Owner: arosaje
--

CREATE SEQUENCE public.conversation_participants_id_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER TABLE public.conversation_participants_id_seq OWNER TO arosaje;

--
-- Name: conversation_participants_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: arosaje
--

ALTER SEQUENCE public.conversation_participants_id_seq OWNED BY public.conversation_participants.id;


--
-- Name: conversations; Type: TABLE; Schema: public; Owner: arosaje
--

CREATE TABLE public.conversations (
    id integer NOT NULL,
    type public.conversationtype,
    related_id integer,
    created_at timestamp without time zone,
    updated_at timestamp without time zone
);


ALTER TABLE public.conversations OWNER TO arosaje;

--
-- Name: conversations_id_seq; Type: SEQUENCE; Schema: public; Owner: arosaje
--

CREATE SEQUENCE public.conversations_id_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER TABLE public.conversations_id_seq OWNER TO arosaje;

--
-- Name: conversations_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: arosaje
--

ALTER SEQUENCE public.conversations_id_seq OWNED BY public.conversations.id;


--
-- Name: messages; Type: TABLE; Schema: public; Owner: arosaje
--

CREATE TABLE public.messages (
    id integer NOT NULL,
    content character varying(2000) NOT NULL,
    sender_id integer,
    conversation_id integer NOT NULL,
    created_at timestamp without time zone,
    updated_at timestamp without time zone,
    is_read boolean
);


ALTER TABLE public.messages OWNER TO arosaje;

--
-- Name: messages_id_seq; Type: SEQUENCE; Schema: public; Owner: arosaje
--

CREATE SEQUENCE public.messages_id_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER TABLE public.messages_id_seq OWNER TO arosaje;

--
-- Name: messages_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: arosaje
--

ALTER SEQUENCE public.messages_id_seq OWNED BY public.messages.id;


--
-- Name: photos; Type: TABLE; Schema: public; Owner: arosaje
--

CREATE TABLE public.photos (
    id integer NOT NULL,
    filename character varying NOT NULL,
    url character varying NOT NULL,
    description character varying,
    type character varying NOT NULL,
    created_at timestamp without time zone,
    plant_id integer
);


ALTER TABLE public.photos OWNER TO arosaje;

--
-- Name: photos_id_seq; Type: SEQUENCE; Schema: public; Owner: arosaje
--

CREATE SEQUENCE public.photos_id_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER TABLE public.photos_id_seq OWNER TO arosaje;

--
-- Name: photos_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: arosaje
--

ALTER SEQUENCE public.photos_id_seq OWNED BY public.photos.id;


--
-- Name: plant_cares; Type: TABLE; Schema: public; Owner: arosaje
--

CREATE TABLE public.plant_cares (
    id integer NOT NULL,
    plant_id integer NOT NULL,
    owner_id integer NOT NULL,
    caretaker_id integer,
    conversation_id integer,
    start_date timestamp without time zone NOT NULL,
    end_date timestamp without time zone NOT NULL,
    status public.carestatus,
    care_instructions character varying,
    localisation character varying,
    latitude double precision,
    longitude double precision,
    created_at timestamp without time zone,
    updated_at timestamp without time zone
);


ALTER TABLE public.plant_cares OWNER TO arosaje;

--
-- Name: plant_cares_id_seq; Type: SEQUENCE; Schema: public; Owner: arosaje
--

CREATE SEQUENCE public.plant_cares_id_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER TABLE public.plant_cares_id_seq OWNER TO arosaje;

--
-- Name: plant_cares_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: arosaje
--

ALTER SEQUENCE public.plant_cares_id_seq OWNED BY public.plant_cares.id;


--
-- Name: plants; Type: TABLE; Schema: public; Owner: arosaje
--

CREATE TABLE public.plants (
    id integer NOT NULL,
    nom character varying NOT NULL,
    espece character varying,
    description character varying,
    photo character varying,
    owner_id integer NOT NULL
);


ALTER TABLE public.plants OWNER TO arosaje;

--
-- Name: plants_id_seq; Type: SEQUENCE; Schema: public; Owner: arosaje
--

CREATE SEQUENCE public.plants_id_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER TABLE public.plants_id_seq OWNER TO arosaje;

--
-- Name: plants_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: arosaje
--

ALTER SEQUENCE public.plants_id_seq OWNED BY public.plants.id;


--
-- Name: refresh_tokens; Type: TABLE; Schema: public; Owner: arosaje
--

CREATE TABLE public.refresh_tokens (
    id integer NOT NULL,
    token character varying(255) NOT NULL,
    user_id integer NOT NULL,
    expires_at timestamp without time zone NOT NULL,
    is_revoked boolean NOT NULL,
    created_at timestamp without time zone,
    updated_at timestamp without time zone,
    device_info character varying(500),
    last_used_at timestamp without time zone
);


ALTER TABLE public.refresh_tokens OWNER TO arosaje;

--
-- Name: refresh_tokens_id_seq; Type: SEQUENCE; Schema: public; Owner: arosaje
--

CREATE SEQUENCE public.refresh_tokens_id_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER TABLE public.refresh_tokens_id_seq OWNER TO arosaje;

--
-- Name: refresh_tokens_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: arosaje
--

ALTER SEQUENCE public.refresh_tokens_id_seq OWNED BY public.refresh_tokens.id;


--
-- Name: user_presence; Type: TABLE; Schema: public; Owner: arosaje
--

CREATE TABLE public.user_presence (
    id integer NOT NULL,
    user_id integer NOT NULL,
    status public.userstatus,
    last_seen_at timestamp without time zone,
    socket_id character varying
);


ALTER TABLE public.user_presence OWNER TO arosaje;

--
-- Name: user_presence_id_seq; Type: SEQUENCE; Schema: public; Owner: arosaje
--

CREATE SEQUENCE public.user_presence_id_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER TABLE public.user_presence_id_seq OWNER TO arosaje;

--
-- Name: user_presence_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: arosaje
--

ALTER SEQUENCE public.user_presence_id_seq OWNED BY public.user_presence.id;


--
-- Name: user_typing_status; Type: TABLE; Schema: public; Owner: arosaje
--

CREATE TABLE public.user_typing_status (
    id integer NOT NULL,
    user_id integer NOT NULL,
    conversation_id integer NOT NULL,
    is_typing boolean,
    last_typed_at timestamp without time zone
);


ALTER TABLE public.user_typing_status OWNER TO arosaje;

--
-- Name: user_typing_status_id_seq; Type: SEQUENCE; Schema: public; Owner: arosaje
--

CREATE SEQUENCE public.user_typing_status_id_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER TABLE public.user_typing_status_id_seq OWNER TO arosaje;

--
-- Name: user_typing_status_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: arosaje
--

ALTER SEQUENCE public.user_typing_status_id_seq OWNED BY public.user_typing_status.id;


--
-- Name: users; Type: TABLE; Schema: public; Owner: arosaje
--

CREATE TABLE public.users (
    id integer NOT NULL,
    email character varying,
    password character varying,
    nom character varying,
    prenom character varying,
    telephone character varying,
    localisation character varying,
    role public.userrole,
    is_verified boolean
);


ALTER TABLE public.users OWNER TO arosaje;

--
-- Name: users_id_seq; Type: SEQUENCE; Schema: public; Owner: arosaje
--

CREATE SEQUENCE public.users_id_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER TABLE public.users_id_seq OWNER TO arosaje;

--
-- Name: users_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: arosaje
--

ALTER SEQUENCE public.users_id_seq OWNED BY public.users.id;


--
-- Name: advices id; Type: DEFAULT; Schema: public; Owner: arosaje
--

ALTER TABLE ONLY public.advices ALTER COLUMN id SET DEFAULT nextval('public.advices_id_seq'::regclass);


--
-- Name: botanist_report_advices id; Type: DEFAULT; Schema: public; Owner: arosaje
--

ALTER TABLE ONLY public.botanist_report_advices ALTER COLUMN id SET DEFAULT nextval('public.botanist_report_advices_id_seq'::regclass);


--
-- Name: care_reports id; Type: DEFAULT; Schema: public; Owner: arosaje
--

ALTER TABLE ONLY public.care_reports ALTER COLUMN id SET DEFAULT nextval('public.care_reports_id_seq'::regclass);


--
-- Name: conversation_participants id; Type: DEFAULT; Schema: public; Owner: arosaje
--

ALTER TABLE ONLY public.conversation_participants ALTER COLUMN id SET DEFAULT nextval('public.conversation_participants_id_seq'::regclass);


--
-- Name: conversations id; Type: DEFAULT; Schema: public; Owner: arosaje
--

ALTER TABLE ONLY public.conversations ALTER COLUMN id SET DEFAULT nextval('public.conversations_id_seq'::regclass);


--
-- Name: messages id; Type: DEFAULT; Schema: public; Owner: arosaje
--

ALTER TABLE ONLY public.messages ALTER COLUMN id SET DEFAULT nextval('public.messages_id_seq'::regclass);


--
-- Name: photos id; Type: DEFAULT; Schema: public; Owner: arosaje
--

ALTER TABLE ONLY public.photos ALTER COLUMN id SET DEFAULT nextval('public.photos_id_seq'::regclass);


--
-- Name: plant_cares id; Type: DEFAULT; Schema: public; Owner: arosaje
--

ALTER TABLE ONLY public.plant_cares ALTER COLUMN id SET DEFAULT nextval('public.plant_cares_id_seq'::regclass);


--
-- Name: plants id; Type: DEFAULT; Schema: public; Owner: arosaje
--

ALTER TABLE ONLY public.plants ALTER COLUMN id SET DEFAULT nextval('public.plants_id_seq'::regclass);


--
-- Name: refresh_tokens id; Type: DEFAULT; Schema: public; Owner: arosaje
--

ALTER TABLE ONLY public.refresh_tokens ALTER COLUMN id SET DEFAULT nextval('public.refresh_tokens_id_seq'::regclass);


--
-- Name: user_presence id; Type: DEFAULT; Schema: public; Owner: arosaje
--

ALTER TABLE ONLY public.user_presence ALTER COLUMN id SET DEFAULT nextval('public.user_presence_id_seq'::regclass);


--
-- Name: user_typing_status id; Type: DEFAULT; Schema: public; Owner: arosaje
--

ALTER TABLE ONLY public.user_typing_status ALTER COLUMN id SET DEFAULT nextval('public.user_typing_status_id_seq'::regclass);


--
-- Name: users id; Type: DEFAULT; Schema: public; Owner: arosaje
--

ALTER TABLE ONLY public.users ALTER COLUMN id SET DEFAULT nextval('public.users_id_seq'::regclass);


--
-- Data for Name: advices; Type: TABLE DATA; Schema: public; Owner: arosaje
--

COPY public.advices (id, plant_care_id, botanist_id, title, content, priority, validation_status, validator_id, validation_comment, validated_at, version, is_current_version, previous_version_id, owner_notified, botanist_notified, created_at, updated_at) FROM stdin;
7	41	3	rgthty	fgbfghhhhhhhhhhhhhhhhh	NORMAL	PENDING	\N	\N	\N	1	f	\N	f	f	2025-09-10 22:11:44.239992	2025-09-10 22:11:55.93975
8	41	3	rgthtyy	fgbfghhhhhhhhhhhhhhhhh	NORMAL	PENDING	\N	\N	\N	2	t	7	f	f	2025-09-10 22:11:55.946608	2025-09-10 22:11:55.946611
\.


--
-- Data for Name: alembic_version; Type: TABLE DATA; Schema: public; Owner: arosaje
--

COPY public.alembic_version (version_num) FROM stdin;
remove_photo_columns
\.


--
-- Data for Name: botanist_report_advices; Type: TABLE DATA; Schema: public; Owner: arosaje
--

COPY public.botanist_report_advices (id, care_report_id, botanist_id, advice_text, created_at, updated_at) FROM stdin;
\.


--
-- Data for Name: care_reports; Type: TABLE DATA; Schema: public; Owner: arosaje
--

COPY public.care_reports (id, plant_care_id, caretaker_id, session_date, photo_url, health_level, hydration_level, vitality_level, description, created_at, updated_at) FROM stdin;
13	41	184	2025-09-10 22:09:07.88123	/assets/persisted_img/persisted_care_report_a8e93434-a814-41ba-845c-15071aaf8504.jpg	BON	BAS	MOYEN	vrvrtvf	2025-09-10 22:09:07.881235	2025-09-10 22:09:08.412619
\.


--
-- Data for Name: conversation_participants; Type: TABLE DATA; Schema: public; Owner: arosaje
--

COPY public.conversation_participants (id, conversation_id, user_id, last_read_at) FROM stdin;
71	36	2	2025-09-10 22:07:25.177231
72	36	184	2025-09-10 22:07:25.177234
74	37	183	2025-09-10 22:12:35.039048
73	37	2	2025-09-11 10:19:57.069506
\.


--
-- Data for Name: conversations; Type: TABLE DATA; Schema: public; Owner: arosaje
--

COPY public.conversations (id, type, related_id, created_at, updated_at) FROM stdin;
36	PLANT_CARE	41	2025-09-10 22:07:25.158375	2025-09-10 22:07:25.158378
37	BOTANICAL_ADVICE	51	2025-09-10 22:12:35.027878	2025-09-11 10:19:58.411945
\.


--
-- Data for Name: messages; Type: TABLE DATA; Schema: public; Owner: arosaje
--

COPY public.messages (id, content, sender_id, conversation_id, created_at, updated_at, is_read) FROM stdin;
10	Bonjour, j'aimerais avoir des conseils pour l'entretien de ma plante 'test' (test). Pouvez-vous m'aider ?	2	37	2025-09-10 22:12:35.102526	2025-09-10 22:12:35.10253	f
11	Salut	2	37	2025-09-11 10:19:58.448454	2025-09-11 10:19:58.448462	f
\.


--
-- Data for Name: photos; Type: TABLE DATA; Schema: public; Owner: arosaje
--

COPY public.photos (id, filename, url, description, type, created_at, plant_id) FROM stdin;
\.


--
-- Data for Name: plant_cares; Type: TABLE DATA; Schema: public; Owner: arosaje
--

COPY public.plant_cares (id, plant_id, owner_id, caretaker_id, conversation_id, start_date, end_date, status, care_instructions, localisation, latitude, longitude, created_at, updated_at) FROM stdin;
41	51	2	184	36	2025-09-11 00:00:00	2025-09-14 00:00:00	ACCEPTED	zeyduz	776 Rue de l'Épinette, Nieppe, France	50.6892876	2.8418648	2025-09-10 22:06:57.646302	2025-09-10 22:07:25.258965
\.


--
-- Data for Name: plants; Type: TABLE DATA; Schema: public; Owner: arosaje
--

COPY public.plants (id, nom, espece, description, photo, owner_id) FROM stdin;
51	test	test	\N	assets/persisted_img/persisted_d4ebe670-40d0-4fe7-ae76-661ae6918c8d.jpg	2
\.


--
-- Data for Name: refresh_tokens; Type: TABLE DATA; Schema: public; Owner: arosaje
--

COPY public.refresh_tokens (id, token, user_id, expires_at, is_revoked, created_at, updated_at, device_info, last_used_at) FROM stdin;
3	XdJM6FWU4SdW3Cl71H8h8cGqODmC3Usyrg_Fe0CAQ3IU28PgoqR7SjD5ySy0HJc8	2	2025-09-17 10:28:19.830509	f	2025-09-10 10:28:19.899772	2025-09-10 10:28:19.899777	IP:172.18.0.1 UA:Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/139.0.0.0 Safari/537.36 Avast/139.0.0.0	2025-09-10 10:28:19.830528
4	Su07opa2OAmofAaGxM4HCneNg-0IVVYrloogV7XcbE8dQzy3XMWl2XbcWMqIOvGh	184	2025-09-17 10:31:09.11564	f	2025-09-10 10:31:09.21875	2025-09-10 10:31:09.218759	IP:172.18.0.1 UA:curl/7.86.0	2025-09-10 10:31:09.115657
5	dVr-8malVoHGu1eyVelmOy836Sgz4rY3iKUgySzThGzHc3DmhVItr3xmQvh-ECbG	184	2025-09-17 10:31:55.957841	f	2025-09-10 10:31:55.9602	2025-09-10 10:31:55.960202	IP:172.18.0.1 UA:Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/139.0.0.0 Safari/537.36 Avast/139.0.0.0	2025-09-10 10:31:55.957849
6	ns37xq2Qq7KRG0VfY8__y4KcTF7z_Vl8WaoqLlRtjOYal1kzCRCf2cEuPe6yq4s1	184	2025-09-17 10:48:43.349931	f	2025-09-10 10:48:43.384999	2025-09-10 10:48:43.385002	IP:172.18.0.1 UA:Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/139.0.0.0 Safari/537.36 Avast/139.0.0.0	2025-09-10 10:48:43.34994
7	37463YiSz-wB5kp4Kwfn8qQVHj55BI8H-Sbk1UKsknsdiRI-6JoAEdQDMQFoWrCm	184	2025-09-17 10:51:07.568291	f	2025-09-10 10:51:07.579917	2025-09-10 10:51:07.579936	IP:172.18.0.1 UA:Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/139.0.0.0 Safari/537.36 Avast/139.0.0.0	2025-09-10 10:51:07.568312
8	eO6jkfbUCTmvWSWHmKvq9z8Kp6NCuZgCLFbQ3lgTDMJ14g2PcoIQ4YTLvLsLmfsq	184	2025-09-17 10:58:26.665412	f	2025-09-10 10:58:26.676714	2025-09-10 10:58:26.676747	IP:172.18.0.1 UA:Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/139.0.0.0 Safari/537.36 Avast/139.0.0.0	2025-09-10 10:58:26.665425
9	hhOBNyCpO2BojCMnnoy9aijM_oL4Lh8VICDFbF0hg7_kNXGKjnoOuJBAuNBNv6Bw	184	2025-09-17 11:02:16.730817	f	2025-09-10 11:02:16.737085	2025-09-10 11:02:16.737098	IP:172.18.0.1 UA:Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/139.0.0.0 Safari/537.36 Avast/139.0.0.0	2025-09-10 11:02:16.73083
10	kMmuJ_eWy8INE0gDZTI6bnIsX_750qwCiaGh78ivBalJTAU09nyZkKQHoWr9E7Ga	184	2025-09-17 11:02:40.447036	f	2025-09-10 11:02:40.482952	2025-09-10 11:02:40.482956	IP:172.18.0.1 UA:Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/139.0.0.0 Safari/537.36 Avast/139.0.0.0	2025-09-10 11:02:40.447055
11	FdIRaygO4aB2MN97m-5QqiL8xERFpWpKNDsQT5wPlRo0CQXxyOfvYSZVBzw0tZMP	184	2025-09-17 11:09:31.498824	f	2025-09-10 11:09:31.514028	2025-09-10 11:09:31.514042	IP:172.18.0.1 UA:Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/139.0.0.0 Safari/537.36 Avast/139.0.0.0	2025-09-10 11:09:31.498875
12	QW0NDmAiJeE_resvK4Rn68m_TY8ZKWSQfN0cDeBArZH4KMNfAvuHWkh4tiqLs81l	184	2025-09-17 11:15:08.016541	f	2025-09-10 11:15:08.038504	2025-09-10 11:15:08.038779	IP:172.18.0.1 UA:Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/139.0.0.0 Safari/537.36 Avast/139.0.0.0	2025-09-10 11:15:08.016559
13	1ueB2USNHSSsDIQCrsjXZOgPbo6wdSsrII_vyy0CuGbKROOljsAzrVIGPVwpExQB	184	2025-09-17 11:18:58.833397	f	2025-09-10 11:18:58.847786	2025-09-10 11:18:58.848103	IP:172.18.0.1 UA:Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/139.0.0.0 Safari/537.36 Avast/139.0.0.0	2025-09-10 11:18:58.833437
14	nTl7oOlfih8RpRHyoD3Mxa5tl2XOM3wyhdGwwpBAjhHwwh2h7sNN6WC-Odolx0IW	184	2025-09-17 11:35:15.985982	f	2025-09-10 11:35:16.00023	2025-09-10 11:35:16.000253	IP:172.18.0.1 UA:Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/139.0.0.0 Safari/537.36 Avast/139.0.0.0	2025-09-10 11:35:15.986015
15	y3kZ124WZnsyd0c8L2dDSGp_JjZ4hoqQfXU0uSVbXzEGxt-atbWUPbOkhbqGxY9M	184	2025-09-17 11:44:50.978904	f	2025-09-10 11:44:51.030297	2025-09-10 11:44:51.030312	IP:172.18.0.1 UA:Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/139.0.0.0 Safari/537.36 Avast/139.0.0.0	2025-09-10 11:44:50.978947
16	ntKKiMQFXaPfxKvnoyC1WG17y9obpG45iOgQRgBuzWqBB95mQL-xFq_2_oiA3P7D	184	2025-09-17 13:14:45.559459	f	2025-09-10 13:14:45.598016	2025-09-10 13:14:45.598043	IP:172.18.0.1 UA:Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/139.0.0.0 Safari/537.36 Avast/139.0.0.0	2025-09-10 13:14:45.559489
17	fczw7-tTqvJUhGnlmJJDpqzH1OtMBAdk8riLktd6drbJRVi60bO7J-d5jD3QxtJz	184	2025-09-17 14:24:42.200495	f	2025-09-10 14:24:42.261913	2025-09-10 14:24:42.261927	IP:172.18.0.1 UA:Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/139.0.0.0 Safari/537.36 Avast/139.0.0.0	2025-09-10 14:24:42.200963
18	0YGHP1967LU8v8ulv4YRHSKlGtsKfmv_ZaFEMoQdu-D5HH9SsceL_Bt8Pdmphc1O	184	2025-09-17 14:26:56.21058	f	2025-09-10 14:26:56.221699	2025-09-10 14:26:56.221737	IP:172.18.0.1 UA:Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/139.0.0.0 Safari/537.36 Avast/139.0.0.0	2025-09-10 14:26:56.210606
19	zjRTo3vkrxQVEsf6NZh8g3aAx3ZqjA1IghwI7z7Vmn7gO_Tgjma-NR0gQczm_25A	184	2025-09-17 14:33:34.080418	f	2025-09-10 14:33:34.274083	2025-09-10 14:33:34.274098	IP:172.18.0.1 UA:Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/139.0.0.0 Safari/537.36 Avast/139.0.0.0	2025-09-10 14:33:34.080485
28	aFoBEyMv27mCAsMenvqait5wZ5wjv95njXokSOCSUjWF3F1VQvRLkAxZLX1nCCaZ	2	2025-09-17 21:43:10.937986	f	2025-09-10 21:43:10.93856	2025-09-10 21:43:10.938563	IP:172.18.0.1 UA:curl/7.86.0	2025-09-10 21:43:10.937989
21	BErgvhaZEWctcJDsMAkkCxb14JWpOk2dsY204FqX8MLTd3D-rCRr8teHxqdmQyBE	1	2025-09-17 21:05:05.41882	f	2025-09-10 21:05:05.592253	2025-09-10 21:05:05.592263	IP:172.18.0.1 UA:curl/7.86.0	2025-09-10 21:05:05.419584
22	qM9RKFUcQpdBzOURcgDCqcaLSN9lKZPe4fw7OE3iSK-9L7ylwA05lfG0R4wS_Egj	1	2025-09-17 21:07:06.603136	f	2025-09-10 21:07:06.605435	2025-09-10 21:07:06.605437	IP:172.18.0.1 UA:curl/7.86.0	2025-09-10 21:07:06.603147
20	d9mGKEPdCE8VVIxHjnvLewq-W1MLXq3LbVTKDFJHUWtn20136z-81oPQk9MBTtkN	184	2025-09-17 15:15:14.968132	f	2025-09-10 15:15:15.256327	2025-09-10 21:08:52.486942	IP:172.18.0.1 UA:Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/139.0.0.0 Safari/537.36 Avast/139.0.0.0	2025-09-10 21:08:52.486667
23	bD9q-YODhOYUO7uOw9tByly16TTY1HBoEczZM469nA6PKEu7lOLfQjAl6DelXz0t	184	2025-09-17 21:31:26.521048	f	2025-09-10 21:31:26.587589	2025-09-10 21:31:26.587771	IP:172.18.0.1 UA:Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/140.0.0.0 Safari/537.36	2025-09-10 21:31:26.521228
24	_8qPR8yoBy7PDrc5ZXixJEpF1V4e2jvujcHJ2fPZqVs2MRJOseCx5WgBZJGfnZeE	2	2025-09-17 21:32:53.143188	f	2025-09-10 21:32:53.144549	2025-09-10 21:32:53.144551	IP:172.18.0.1 UA:Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/140.0.0.0 Safari/537.36	2025-09-10 21:32:53.143209
25	5-ABqVsCqekgb82gTTHoR04XdEopf0Xb2rLJO6m-sEheUahae41IupDNdnD3D10a	2	2025-09-17 21:40:06.591459	f	2025-09-10 21:40:06.683518	2025-09-10 21:40:06.683524	IP:172.18.0.1 UA:Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/139.0.0.0 Safari/537.36 Avast/139.0.0.0	2025-09-10 21:40:06.591504
29	f43Ynhlsr0PNqwkD80B3qjWV-ETmPZFEGzq1PJWzC_MXBh64b045b2CB1COTiHdY	2	2025-09-17 21:43:23.558107	f	2025-09-10 21:43:23.562355	2025-09-10 21:43:23.562357	IP:172.18.0.1 UA:curl/7.86.0	2025-09-10 21:43:23.558125
26	r_hidKZHvhRf380QYvpwtmz6mgAkREzEO2QVFTfOmmMY7szl3EB94ibM1nO4XSMD	184	2025-09-17 21:41:14.002237	f	2025-09-10 21:41:14.060254	2025-09-10 21:41:14.060285	IP:172.18.0.1 UA:curl/7.86.0	2025-09-10 21:41:14.00229
27	1scB40KsWEseFcQ_PQhNZh9HVhaSDXWvpeWU19XE8BqG1PDlB0iRmcPDNizSFumL	2	2025-09-17 21:42:41.313905	f	2025-09-10 21:42:41.317572	2025-09-10 21:42:41.317576	IP:172.18.0.1 UA:curl/7.86.0	2025-09-10 21:42:41.313921
30	Xgwr-HV6qu3cPcRXEykachQEXQp6nbUplRFTMMAsierux3tH_uHaZl2Qkh1Xr9Kq	184	2025-09-17 21:43:45.528409	f	2025-09-10 21:43:45.529045	2025-09-10 21:43:45.529047	IP:172.18.0.1 UA:curl/7.86.0	2025-09-10 21:43:45.528415
31	RBCShY4qiA_jRcoHAXUucu-q9ZBnbAwVZNvEVhmyYKHsE-MvJheseNOsK1V260Km	184	2025-09-17 21:44:28.31138	f	2025-09-10 21:44:28.315198	2025-09-10 21:44:28.3152	IP:172.18.0.1 UA:curl/7.86.0	2025-09-10 21:44:28.311398
32	bXzIBGC7aN8BMUQE3972dwC6Ju3RQBFz1u8YnBRpc_EEplM_1v9UV-xbsxGKjx8b	184	2025-09-17 21:58:17.37864	f	2025-09-10 21:58:17.46923	2025-09-10 21:58:17.469233	IP:172.18.0.1 UA:Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/139.0.0.0 Safari/537.36 Avast/139.0.0.0	2025-09-10 21:58:17.378664
33	zeDdXfon56KSlM4kJXplQG3ffc_guOp-ImMz6Kda1ozNCUTlWJoxMerRU6VzqpN8	2	2025-09-17 21:58:39.120667	f	2025-09-10 21:58:39.210296	2025-09-10 21:58:39.2103	IP:172.18.0.1 UA:Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/139.0.0.0 Safari/537.36 Avast/139.0.0.0	2025-09-10 21:58:39.120682
34	OclrHRGLkuYP08lF8_Hf8ETE12g7b3EpoUq93zzQEuZ39hCHgXoRcJQ-qmu4hGBF	184	2025-09-17 22:01:23.515448	f	2025-09-10 22:01:23.523357	2025-09-10 22:01:23.523361	IP:172.18.0.1 UA:Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/139.0.0.0 Safari/537.36 Avast/139.0.0.0	2025-09-10 22:01:23.515476
35	9c0SyUMUDIH8FOxHLTQl2ts-rsuCyAEdh63fYkUHPCODlLgMyRF3bgyWWU5LgVgV	1	2025-09-17 22:03:34.370584	f	2025-09-10 22:03:34.429837	2025-09-10 22:03:34.430146	IP:172.18.0.1 UA:curl/7.86.0	2025-09-10 22:03:34.370913
37	dGHiAMJYEy63FOL74g-mqGtvKgHpqpQ7XrbLQV6mMPbCi_9Pya8myKDkis8RYA9H	3	2025-09-17 22:11:27.046757	f	2025-09-10 22:11:27.077046	2025-09-10 22:11:27.077144	IP:172.18.0.1 UA:Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/139.0.0.0 Safari/537.36 Avast/139.0.0.0	2025-09-10 22:11:27.046809
38	p_etsRtpp3WTc1kv04tISQo-WSvzt2ImvzJO7AJk1HYAQnhxIWiQJ7o6c028cYhj	1	2025-09-17 22:16:21.939982	f	2025-09-10 22:16:22.025825	2025-09-10 22:16:22.02586	IP:172.18.0.1 UA:curl/7.86.0	2025-09-10 22:16:21.940029
39	ZwDrS3HCBXWV_4bnkV9ALfe8kTWQOPDKQCyuGYsOWWDZXCwKDdE5MaWYHcoxHvu9	183	2025-09-17 22:19:50.205819	f	2025-09-10 22:19:50.314201	2025-09-10 22:19:50.314238	IP:172.18.0.1 UA:curl/7.86.0	2025-09-10 22:19:50.206188
36	J-2iRmaLVSaKj0WjpN6raAbawsXt_3vfAbZ4gdNta-cGzDrC19d8TJzCgF9vyW51	2	2025-09-17 22:05:46.849738	f	2025-09-10 22:05:46.880465	2025-09-11 11:10:07.702952	IP:172.18.0.1 UA:Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/140.0.0.0 Safari/537.36	2025-09-11 11:10:07.699119
\.


--
-- Data for Name: user_presence; Type: TABLE DATA; Schema: public; Owner: arosaje
--

COPY public.user_presence (id, user_id, status, last_seen_at, socket_id) FROM stdin;
3	184	OFFLINE	2025-09-10 13:12:18.183383	f97b5c17-9d64-410c-8fb9-39285325ad07
4	2	OFFLINE	2025-09-11 11:26:20.155918	d8bd2e7b-0f66-409e-8071-09fa6b257567
\.


--
-- Data for Name: user_typing_status; Type: TABLE DATA; Schema: public; Owner: arosaje
--

COPY public.user_typing_status (id, user_id, conversation_id, is_typing, last_typed_at) FROM stdin;
3	2	37	f	2025-09-11 10:19:58.498466
\.


--
-- Data for Name: users; Type: TABLE DATA; Schema: public; Owner: arosaje
--

COPY public.users (id, email, password, nom, prenom, telephone, localisation, role, is_verified) FROM stdin;
1	root@arosaje.fr	$2b$12$Ecr.B8pN/WhBjTl1ozFdEusFPN20oIcoc95P1m4U5yaGh3yXPJR/G	Admin	System	\N	\N	ADMIN	t
2	user@arosaje.fr	$2b$12$r2KRHOXdZzAR/4c0iQ6fq.u.iNpeIENLAW97jiR7wBNvyH9UpFNnO	Test	User	\N	\N	USER	t
3	botanist@arosaje.fr	$2b$12$6KR8OiPY1xoHo8OR44BWZuREvv3Nts5yXy6v4W6aopbcFj9WClfHW	Botanist	Test	\N	\N	BOTANIST	t
184	gardien@arosaje.fr	$2b$12$Ecr.B8pN/WhBjTl1ozFdEusFPN20oIcoc95P1m4U5yaGh3yXPJR/G	Dupont	Marie	+33123456791	Toulouse	USER	t
183	botanist2@arosaje.fr	$2b$12$ag2YhVBNgmuH0NXV6KXWTu/XH/R0MY1SCZuzUdVi9mv.x3J07wFMq	Martin	Sophie	+33123456790	Lyon	BOTANIST	t
\.


--
-- Name: advices_id_seq; Type: SEQUENCE SET; Schema: public; Owner: arosaje
--

SELECT pg_catalog.setval('public.advices_id_seq', 8, true);


--
-- Name: botanist_report_advices_id_seq; Type: SEQUENCE SET; Schema: public; Owner: arosaje
--

SELECT pg_catalog.setval('public.botanist_report_advices_id_seq', 1, true);


--
-- Name: care_reports_id_seq; Type: SEQUENCE SET; Schema: public; Owner: arosaje
--

SELECT pg_catalog.setval('public.care_reports_id_seq', 13, true);


--
-- Name: conversation_participants_id_seq; Type: SEQUENCE SET; Schema: public; Owner: arosaje
--

SELECT pg_catalog.setval('public.conversation_participants_id_seq', 74, true);


--
-- Name: conversations_id_seq; Type: SEQUENCE SET; Schema: public; Owner: arosaje
--

SELECT pg_catalog.setval('public.conversations_id_seq', 37, true);


--
-- Name: messages_id_seq; Type: SEQUENCE SET; Schema: public; Owner: arosaje
--

SELECT pg_catalog.setval('public.messages_id_seq', 11, true);


--
-- Name: photos_id_seq; Type: SEQUENCE SET; Schema: public; Owner: arosaje
--

SELECT pg_catalog.setval('public.photos_id_seq', 6, true);


--
-- Name: plant_cares_id_seq; Type: SEQUENCE SET; Schema: public; Owner: arosaje
--

SELECT pg_catalog.setval('public.plant_cares_id_seq', 41, true);


--
-- Name: plants_id_seq; Type: SEQUENCE SET; Schema: public; Owner: arosaje
--

SELECT pg_catalog.setval('public.plants_id_seq', 51, true);


--
-- Name: refresh_tokens_id_seq; Type: SEQUENCE SET; Schema: public; Owner: arosaje
--

SELECT pg_catalog.setval('public.refresh_tokens_id_seq', 39, true);


--
-- Name: user_presence_id_seq; Type: SEQUENCE SET; Schema: public; Owner: arosaje
--

SELECT pg_catalog.setval('public.user_presence_id_seq', 4, true);


--
-- Name: user_typing_status_id_seq; Type: SEQUENCE SET; Schema: public; Owner: arosaje
--

SELECT pg_catalog.setval('public.user_typing_status_id_seq', 3, true);


--
-- Name: users_id_seq; Type: SEQUENCE SET; Schema: public; Owner: arosaje
--

SELECT pg_catalog.setval('public.users_id_seq', 184, true);


--
-- Name: advices advices_pkey; Type: CONSTRAINT; Schema: public; Owner: arosaje
--

ALTER TABLE ONLY public.advices
    ADD CONSTRAINT advices_pkey PRIMARY KEY (id);


--
-- Name: alembic_version alembic_version_pkc; Type: CONSTRAINT; Schema: public; Owner: arosaje
--

ALTER TABLE ONLY public.alembic_version
    ADD CONSTRAINT alembic_version_pkc PRIMARY KEY (version_num);


--
-- Name: botanist_report_advices botanist_report_advices_pkey; Type: CONSTRAINT; Schema: public; Owner: arosaje
--

ALTER TABLE ONLY public.botanist_report_advices
    ADD CONSTRAINT botanist_report_advices_pkey PRIMARY KEY (id);


--
-- Name: care_reports care_reports_pkey; Type: CONSTRAINT; Schema: public; Owner: arosaje
--

ALTER TABLE ONLY public.care_reports
    ADD CONSTRAINT care_reports_pkey PRIMARY KEY (id);


--
-- Name: conversation_participants conversation_participants_pkey; Type: CONSTRAINT; Schema: public; Owner: arosaje
--

ALTER TABLE ONLY public.conversation_participants
    ADD CONSTRAINT conversation_participants_pkey PRIMARY KEY (id);


--
-- Name: conversations conversations_pkey; Type: CONSTRAINT; Schema: public; Owner: arosaje
--

ALTER TABLE ONLY public.conversations
    ADD CONSTRAINT conversations_pkey PRIMARY KEY (id);


--
-- Name: messages messages_pkey; Type: CONSTRAINT; Schema: public; Owner: arosaje
--

ALTER TABLE ONLY public.messages
    ADD CONSTRAINT messages_pkey PRIMARY KEY (id);


--
-- Name: photos photos_pkey; Type: CONSTRAINT; Schema: public; Owner: arosaje
--

ALTER TABLE ONLY public.photos
    ADD CONSTRAINT photos_pkey PRIMARY KEY (id);


--
-- Name: plant_cares plant_cares_pkey; Type: CONSTRAINT; Schema: public; Owner: arosaje
--

ALTER TABLE ONLY public.plant_cares
    ADD CONSTRAINT plant_cares_pkey PRIMARY KEY (id);


--
-- Name: plants plants_pkey; Type: CONSTRAINT; Schema: public; Owner: arosaje
--

ALTER TABLE ONLY public.plants
    ADD CONSTRAINT plants_pkey PRIMARY KEY (id);


--
-- Name: refresh_tokens refresh_tokens_pkey; Type: CONSTRAINT; Schema: public; Owner: arosaje
--

ALTER TABLE ONLY public.refresh_tokens
    ADD CONSTRAINT refresh_tokens_pkey PRIMARY KEY (id);


--
-- Name: conversation_participants unique_conversation_participant; Type: CONSTRAINT; Schema: public; Owner: arosaje
--

ALTER TABLE ONLY public.conversation_participants
    ADD CONSTRAINT unique_conversation_participant UNIQUE (conversation_id, user_id);


--
-- Name: user_presence user_presence_pkey; Type: CONSTRAINT; Schema: public; Owner: arosaje
--

ALTER TABLE ONLY public.user_presence
    ADD CONSTRAINT user_presence_pkey PRIMARY KEY (id);


--
-- Name: user_presence user_presence_user_id_key; Type: CONSTRAINT; Schema: public; Owner: arosaje
--

ALTER TABLE ONLY public.user_presence
    ADD CONSTRAINT user_presence_user_id_key UNIQUE (user_id);


--
-- Name: user_typing_status user_typing_status_pkey; Type: CONSTRAINT; Schema: public; Owner: arosaje
--

ALTER TABLE ONLY public.user_typing_status
    ADD CONSTRAINT user_typing_status_pkey PRIMARY KEY (id);


--
-- Name: users users_email_key; Type: CONSTRAINT; Schema: public; Owner: arosaje
--

ALTER TABLE ONLY public.users
    ADD CONSTRAINT users_email_key UNIQUE (email);


--
-- Name: users users_pkey; Type: CONSTRAINT; Schema: public; Owner: arosaje
--

ALTER TABLE ONLY public.users
    ADD CONSTRAINT users_pkey PRIMARY KEY (id);


--
-- Name: ix_refresh_tokens_token; Type: INDEX; Schema: public; Owner: arosaje
--

CREATE UNIQUE INDEX ix_refresh_tokens_token ON public.refresh_tokens USING btree (token);


--
-- Name: advices advices_botanist_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: arosaje
--

ALTER TABLE ONLY public.advices
    ADD CONSTRAINT advices_botanist_id_fkey FOREIGN KEY (botanist_id) REFERENCES public.users(id) ON DELETE CASCADE;


--
-- Name: advices advices_plant_care_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: arosaje
--

ALTER TABLE ONLY public.advices
    ADD CONSTRAINT advices_plant_care_id_fkey FOREIGN KEY (plant_care_id) REFERENCES public.plant_cares(id) ON DELETE CASCADE;


--
-- Name: advices advices_previous_version_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: arosaje
--

ALTER TABLE ONLY public.advices
    ADD CONSTRAINT advices_previous_version_id_fkey FOREIGN KEY (previous_version_id) REFERENCES public.advices(id) ON DELETE SET NULL;


--
-- Name: advices advices_validator_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: arosaje
--

ALTER TABLE ONLY public.advices
    ADD CONSTRAINT advices_validator_id_fkey FOREIGN KEY (validator_id) REFERENCES public.users(id) ON DELETE SET NULL;


--
-- Name: botanist_report_advices botanist_report_advices_botanist_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: arosaje
--

ALTER TABLE ONLY public.botanist_report_advices
    ADD CONSTRAINT botanist_report_advices_botanist_id_fkey FOREIGN KEY (botanist_id) REFERENCES public.users(id) ON DELETE CASCADE;


--
-- Name: botanist_report_advices botanist_report_advices_care_report_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: arosaje
--

ALTER TABLE ONLY public.botanist_report_advices
    ADD CONSTRAINT botanist_report_advices_care_report_id_fkey FOREIGN KEY (care_report_id) REFERENCES public.care_reports(id) ON DELETE CASCADE;


--
-- Name: care_reports care_reports_caretaker_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: arosaje
--

ALTER TABLE ONLY public.care_reports
    ADD CONSTRAINT care_reports_caretaker_id_fkey FOREIGN KEY (caretaker_id) REFERENCES public.users(id) ON DELETE CASCADE;


--
-- Name: care_reports care_reports_plant_care_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: arosaje
--

ALTER TABLE ONLY public.care_reports
    ADD CONSTRAINT care_reports_plant_care_id_fkey FOREIGN KEY (plant_care_id) REFERENCES public.plant_cares(id) ON DELETE CASCADE;


--
-- Name: conversation_participants conversation_participants_conversation_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: arosaje
--

ALTER TABLE ONLY public.conversation_participants
    ADD CONSTRAINT conversation_participants_conversation_id_fkey FOREIGN KEY (conversation_id) REFERENCES public.conversations(id) ON DELETE CASCADE;


--
-- Name: conversation_participants conversation_participants_user_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: arosaje
--

ALTER TABLE ONLY public.conversation_participants
    ADD CONSTRAINT conversation_participants_user_id_fkey FOREIGN KEY (user_id) REFERENCES public.users(id) ON DELETE CASCADE;


--
-- Name: messages messages_conversation_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: arosaje
--

ALTER TABLE ONLY public.messages
    ADD CONSTRAINT messages_conversation_id_fkey FOREIGN KEY (conversation_id) REFERENCES public.conversations(id) ON DELETE CASCADE;


--
-- Name: messages messages_sender_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: arosaje
--

ALTER TABLE ONLY public.messages
    ADD CONSTRAINT messages_sender_id_fkey FOREIGN KEY (sender_id) REFERENCES public.users(id) ON DELETE SET NULL;


--
-- Name: photos photos_plant_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: arosaje
--

ALTER TABLE ONLY public.photos
    ADD CONSTRAINT photos_plant_id_fkey FOREIGN KEY (plant_id) REFERENCES public.plants(id);


--
-- Name: plant_cares plant_cares_caretaker_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: arosaje
--

ALTER TABLE ONLY public.plant_cares
    ADD CONSTRAINT plant_cares_caretaker_id_fkey FOREIGN KEY (caretaker_id) REFERENCES public.users(id) ON DELETE CASCADE;


--
-- Name: plant_cares plant_cares_conversation_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: arosaje
--

ALTER TABLE ONLY public.plant_cares
    ADD CONSTRAINT plant_cares_conversation_id_fkey FOREIGN KEY (conversation_id) REFERENCES public.conversations(id) ON DELETE SET NULL;


--
-- Name: plant_cares plant_cares_owner_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: arosaje
--

ALTER TABLE ONLY public.plant_cares
    ADD CONSTRAINT plant_cares_owner_id_fkey FOREIGN KEY (owner_id) REFERENCES public.users(id) ON DELETE CASCADE;


--
-- Name: plant_cares plant_cares_plant_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: arosaje
--

ALTER TABLE ONLY public.plant_cares
    ADD CONSTRAINT plant_cares_plant_id_fkey FOREIGN KEY (plant_id) REFERENCES public.plants(id) ON DELETE CASCADE;


--
-- Name: plants plants_owner_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: arosaje
--

ALTER TABLE ONLY public.plants
    ADD CONSTRAINT plants_owner_id_fkey FOREIGN KEY (owner_id) REFERENCES public.users(id);


--
-- Name: refresh_tokens refresh_tokens_user_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: arosaje
--

ALTER TABLE ONLY public.refresh_tokens
    ADD CONSTRAINT refresh_tokens_user_id_fkey FOREIGN KEY (user_id) REFERENCES public.users(id) ON DELETE CASCADE;


--
-- Name: user_presence user_presence_user_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: arosaje
--

ALTER TABLE ONLY public.user_presence
    ADD CONSTRAINT user_presence_user_id_fkey FOREIGN KEY (user_id) REFERENCES public.users(id) ON DELETE CASCADE;


--
-- Name: user_typing_status user_typing_status_conversation_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: arosaje
--

ALTER TABLE ONLY public.user_typing_status
    ADD CONSTRAINT user_typing_status_conversation_id_fkey FOREIGN KEY (conversation_id) REFERENCES public.conversations(id) ON DELETE CASCADE;


--
-- Name: user_typing_status user_typing_status_user_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: arosaje
--

ALTER TABLE ONLY public.user_typing_status
    ADD CONSTRAINT user_typing_status_user_id_fkey FOREIGN KEY (user_id) REFERENCES public.users(id) ON DELETE CASCADE;


--
-- PostgreSQL database dump complete
--

\unrestrict NcVndGb3jxxh8P2W3y0pTidrPQfbVd02Tu9sExP4KP0JGmwrqLrNpfJyhiOfM2a

