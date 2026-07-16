CREATE TABLE IF NOT EXISTS public.parking_blocked_day (
    id bigint NOT NULL PRIMARY KEY,
    id_parking bigint NOT NULL,
    day date NOT NULL,
    created_at timestamp without time zone DEFAULT CURRENT_TIMESTAMP,
    CONSTRAINT uq_parking_blocked_day UNIQUE (id_parking, day)
);

DO $$
BEGIN
    IF NOT EXISTS (
        SELECT 1 FROM pg_class WHERE relname = 'parking_blocked_day_id_seq'
    ) THEN
        CREATE SEQUENCE public.parking_blocked_day_id_seq
            START WITH 1 INCREMENT BY 1 NO MINVALUE NO MAXVALUE CACHE 1;
        ALTER SEQUENCE public.parking_blocked_day_id_seq OWNED BY public.parking_blocked_day.id;
        ALTER TABLE ONLY public.parking_blocked_day
            ALTER COLUMN id SET DEFAULT nextval('public.parking_blocked_day_id_seq'::regclass);
    END IF;
END $$;

DO $$
BEGIN
    IF NOT EXISTS (
        SELECT 1
        FROM pg_constraint
        WHERE conname = 'parking_blocked_day_id_parking_fkey'
    ) THEN
        ALTER TABLE ONLY public.parking_blocked_day
            ADD CONSTRAINT parking_blocked_day_id_parking_fkey
            FOREIGN KEY (id_parking) REFERENCES public.parking(id) ON DELETE CASCADE;
    END IF;
END $$;
