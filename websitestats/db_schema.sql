CREATE TABLE public.websites (
    id integer NOT NULL,
    name character varying(60),
    url character varying(150) NOT NULL
);


CREATE SEQUENCE public.websites_id_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


CREATE TABLE public.stats (
    id integer NOT NULL,
    http_response_time double precision,
    error_code character varying(10),
    content text,
    website_id bigint NOT NULL,
    datetime timestamp with time zone DEFAULT CURRENT_TIMESTAMP
);

CREATE SEQUENCE public.stats_id_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;

ALTER SEQUENCE public.stats_id_seq OWNED BY public.stats.id;
ALTER SEQUENCE public.websites_id_seq OWNED BY public.websites.id;
ALTER TABLE ONLY public.stats ALTER COLUMN id SET DEFAULT nextval('public.stats_id_seq'::regclass);
ALTER TABLE ONLY public.websites ALTER COLUMN id SET DEFAULT nextval('public.websites_id_seq'::regclass);
ALTER TABLE ONLY public.stats ADD CONSTRAINT stats_pkey PRIMARY KEY (id);
ALTER TABLE ONLY public.websites ADD CONSTRAINT websites_pkey PRIMARY KEY (id);
CREATE INDEX fki_website_id ON public.stats USING btree (website_id);
ALTER TABLE ONLY public.stats ADD CONSTRAINT website_id FOREIGN KEY (website_id) REFERENCES public.websites(id);
