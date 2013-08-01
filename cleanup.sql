CREATE TABLE dummy_values (id INT);
INSERT INTO dummy_values 
 SELECT id FROM phenotype_values 
 WHERE id IN
  (SELECT phenotype_values.id 
   FROM phenotype_values, phenotypes
   WHERE phenotypes.id = phenotype_values.phenotype_id
   AND phenotypes.date = '2012-10-01');
DELETE FROM phenotype_values
WHERE phenotype_values.id IN
 (SELECT dummy_values.id 
  FROM dummy_values);
DELETE FROM phenotypes
WHERE phenotypes.date = '2012-10-01';
DELETE FROM samples
WHERE samples.created < '2000';
DROP TABLE dummy_values;

