ALTER TABLE public.booking
    ADD COLUMN IF NOT EXISTS customer_email character varying(255),
    ADD COLUMN IF NOT EXISTS customer_name character varying(255);

UPDATE public.booking b
SET customer_email = u.email,
    customer_name = TRIM(
        COALESCE(p.name, '') || CASE
            WHEN p.last_name IS NOT NULL AND p.last_name <> '' THEN ' ' || p.last_name
            ELSE ''
        END
    )
FROM public.users u
LEFT JOIN public.profiles p ON p.user_id = u.id
WHERE b.id_user = u.id
  AND (b.customer_email IS NULL OR b.customer_name IS NULL);

ALTER TABLE public.booking DROP CONSTRAINT IF EXISTS booking_id_user_fkey;
ALTER TABLE public.booking ALTER COLUMN id_user DROP NOT NULL;
ALTER TABLE public.booking
    ADD CONSTRAINT booking_id_user_fkey
    FOREIGN KEY (id_user) REFERENCES public.users(id) ON DELETE SET NULL;
