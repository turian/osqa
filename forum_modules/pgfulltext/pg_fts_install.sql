  CREATE OR REPLACE FUNCTION public.create_plpgsql_language ()
      RETURNS TEXT
      AS $$
          CREATE LANGUAGE plpgsql;
          SELECT 'language plpgsql created'::TEXT;
      $$
  LANGUAGE 'sql';

  SELECT CASE WHEN
        (SELECT true::BOOLEAN
           FROM pg_language
          WHERE lanname='plpgsql')
      THEN
        (SELECT 'language already installed'::TEXT)
      ELSE
        (SELECT public.create_plpgsql_language())
      END;

  DROP FUNCTION public.create_plpgsql_language ();

  CREATE OR REPLACE FUNCTION node_ranking(node_id int, srch text) RETURNS float AS $$
  declare
     v tsvector;
  begin
     SELECT tsv INTO v FROM forum_node WHERE id = node_id;
     RETURN ts_rank_cd(v || children_tsv(node_id), plainto_tsquery(srch), 32);
  end
  $$ LANGUAGE plpgsql;

  CREATE OR REPLACE FUNCTION children_tsv(id int) RETURNS tsvector AS $$
    declare
      v tsvector := ''::tsvector;
      r record;
    begin
      FOR r IN SELECT * FROM forum_node WHERE parent_id = id LOOP
        v := v || r.tsv || children_tsv(r.id);
      END LOOP;
      RETURN v;
    end
  $$ LANGUAGE plpgsql;

  CREATE OR REPLACE FUNCTION set_node_tsv() RETURNS TRIGGER AS $$
  begin
    IF (tg_op = 'INSERT') THEN
      new.tsv :=
         setweight(to_tsvector('english', coalesce(new.tagnames,'')), 'A') ||
         setweight(to_tsvector('english', coalesce(new.title,'')), 'B') ||
         setweight(to_tsvector('english', coalesce(new.body,'')), 'C');
    ELSIF (new.active_revision_id <> old.active_revision_id) OR (new.tsv IS NULL) THEN
      new.tsv :=
         setweight(to_tsvector('english', coalesce(new.tagnames,'')), 'A') ||
         setweight(to_tsvector('english', coalesce(new.title,'')), 'B') ||
         setweight(to_tsvector('english', coalesce(new.body,'')), 'C'); 
    END IF;
    RETURN new;
  end
  $$ LANGUAGE plpgsql;

  CREATE OR REPLACE FUNCTION public.create_tsv_node_column ()
      RETURNS TEXT
      AS $$
          ALTER TABLE forum_node ADD COLUMN tsv tsvector;

          CREATE TRIGGER tsvectorupdate BEFORE INSERT OR UPDATE
	        ON forum_node FOR EACH ROW EXECUTE PROCEDURE set_node_tsv();

	      CREATE INDEX node_tsv ON forum_node USING gin(tsv);

          SELECT 'tsv column created'::TEXT;
      $$
  LANGUAGE 'sql';

  SELECT CASE WHEN
     (SELECT true::BOOLEAN FROM pg_attribute WHERE attrelid = (SELECT oid FROM pg_class WHERE relname = 'forum_node') AND attname = 'tsv')
  THEN
     (SELECT 'Tsv column already exists'::TEXT)
  ELSE
     (SELECT public.create_tsv_node_column())

  END;

  DROP FUNCTION public.create_tsv_node_column ();

  UPDATE forum_node SET id=id WHERE TRUE;
