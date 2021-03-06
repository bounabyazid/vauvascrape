CREATE TABLE posts
(
    id UUID     PRIMARY KEY DEFAULT gen_random_uuid(),
    topic_id    INT REFERENCES topics(id),
    content     TEXT NOT NULL,
    post_time   timestamp without time zone NOT NULL DEFAULT '1970-01-01 00:00:00'::timestamp without time zone,
    post_number INT NOT NULL
);

CREATE INDEX posts_topic_id_idx
    ON public.posts USING btree
    (topic_id)
    TABLESPACE pg_default;
