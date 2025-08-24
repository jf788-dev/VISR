create table if not exists objects (
  bucket        text not null,
  key           text not null,
  size_bytes    bigint not null,
  etag          text,
  content_type  text,
  last_modified timestamptz not null,
  first_seen    timestamptz not null default now(),
  last_seen     timestamptz not null default now(),
  primary key (bucket, key)
);
create index if not exists objects_bucket_lm_idx on objects (bucket, last_modified desc);