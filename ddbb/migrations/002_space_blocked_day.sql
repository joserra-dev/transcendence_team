DROP TABLE IF EXISTS public.parking_blocked_day CASCADE;

CREATE TABLE IF NOT EXISTS public.space_blocked_day (
    id bigint NOT NULL PRIMARY KEY,
    id_space bigint NOT NULL,
    day date NOT NULL,
    created_at timestamp without time zone DEFAULT CURRENT_TIMESTAMP,
    CONSTRAINT uq_space_blocked_day UNIQUE (id_space, day)
);

DO $$
BEGIN
    IF NOT EXISTS (
        SELECT 1 FROM pg_class WHERE relname = 'space_blocked_day_id_seq'
    ) THEN
        CREATE SEQUENCE public.space_blocked_day_id_seq
            START WITH 1 INCREMENT BY 1 NO MINVALUE NO MAXVALUE CACHE 1;
        ALTER SEQUENCE public.space_blocked_day_id_seq OWNED BY public.space_blocked_day.id;
        ALTER TABLE ONLY public.space_blocked_day
            ALTER COLUMN id SET DEFAULT nextval('public.space_blocked_day_id_seq'::regclass);
    END IF;
END $$;

DO $$
BEGIN
    IF NOT EXISTS (
        SELECT 1
        FROM pg_constraint
        WHERE conname = 'space_blocked_day_id_space_fkey'
    ) THEN
        ALTER TABLE ONLY public.space_blocked_day
            ADD CONSTRAINT space_blocked_day_id_space_fkey
            FOREIGN KEY (id_space) REFERENCES public.space(id) ON DELETE CASCADE;
    END IF;
END $$;
