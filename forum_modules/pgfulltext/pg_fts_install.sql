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
     cv tsvector;
     rev_id int;
     child_count int;
     r record;
  begin
     SELECT active_revision_id INTO rev_id FROM forum_node WHERE id = node_id;
     SELECT tsv INTO v FROM forum_noderevision WHERE id = rev_id;

    SELECT  count(*) INTO child_count FROM forum_node WHERE abs_parent_id = node_id AND NOT deleted;

    IF child_count > 0 THEN
       FOR r in SELECT * FROM forum_node WHERE abs_parent_id = node_id  AND NOT deleted LOOP
           SELECT tsv INTO cv FROM forum_noderevision WHERE id = r.active_revision_id;
           v :=(v || cv);
       END LOOP;
     END IF;

     RETURN ts_rank_cd(v, plainto_tsquery('english', srch), 32);
  end
  $$ LANGUAGE plpgsql;

  CREATE OR REPLACE FUNCTION set_node_tsv() RETURNS TRIGGER AS $$
  begin
      new.tsv :=
         setweight(to_tsvector('english', coalesce(new.tagnames,'')), 'A') ||
         setweight(to_tsvector('english', coalesce(new.title,'')), 'B') ||
         setweight(to_tsvector('english', coalesce(new.body,'')), 'C');

    RETURN new;
  end
  $$ LANGUAGE plpgsql;

  CREATE OR REPLACE FUNCTION public.create_tsv_noderevision_column () RETURNS TEXT AS $$
  begin
          ALTER TABLE forum_noderevision ADD COLUMN tsv tsvector;

          DROP TRIGGER IF EXISTS tsvectorupdate ON forum_noderevision;

          CREATE TRIGGER tsvectorupdate BEFORE INSERT OR UPDATE
	        ON forum_noderevision FOR EACH ROW EXECUTE PROCEDURE set_node_tsv();

	      CREATE INDEX noderevision_tsv ON forum_noderevision USING gin(tsv);

          RETURN 'tsv column created'::TEXT;
  end
  $$ LANGUAGE plpgsql;

  SELECT CASE WHEN
     (SELECT true::BOOLEAN FROM pg_attribute WHERE attrelid = (SELECT oid FROM pg_class WHERE relname = 'forum_noderevision') AND attname = 'tsv')
  THEN
     (SELECT 'Tsv column already exists'::TEXT)
  ELSE
     (SELECT public.create_tsv_noderevision_column())

  END;

  DROP FUNCTION public.create_tsv_noderevision_column();

  UPDATE forum_noderevision SET id=id WHERE TRUE;