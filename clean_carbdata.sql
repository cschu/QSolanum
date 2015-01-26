create temporary table tmp_table (id int) select id from phenotypes where value_id in (212,131,132,142);
delete from phenotype_aliquots where phenotype_id in (select id from tmp_table);
delete from phenotypes where value_id in  (212,131,132,142);



