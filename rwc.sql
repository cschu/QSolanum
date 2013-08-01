SELECT 
pl.culture_id AS CULTURE_ID, 
pl.id AS PLANT_ID, 
pl.subspecies_id AS subspecies,
p1.date, p1.number AS FW_abs_g,
p2.date, p2.number AS SW_abs_g,
p3.date, p3.number AS DW_abs_g,
p4.value_id AS treatment,
c.location_id AS location,
c.description,
p2.number >= p1.number >= p3.number AS sanity1_passed,
(p1.number - p3.number) / (p2.number - p3.number) AS RWC,
0 <= (p1.number - p3.number) / (p2.number - p3.number) <= 1 AS sanity2_passed
FROM plants pl

LEFT JOIN cultures c ON pl.culture_id = c.id

LEFT JOIN phenotype_plants AS pp1 ON pp1.plant_id = pl.id
LEFT JOIN phenotypes AS p1 ON p1.id = pp1.phenotype_id 

LEFT JOIN phenotype_plants AS pp2 ON pp2.plant_id = pl.id
LEFT JOIN phenotypes AS p2 ON p2.id = pp2.phenotype_id 

LEFT JOIN phenotype_plants AS pp3 ON pp3.plant_id = pl.id
LEFT JOIN phenotypes AS p3 ON p3.id = pp3.phenotype_id 

LEFT JOIN phenotype_plants AS pp4 ON pp4.plant_id = pl.id
LEFT JOIN phenotypes AS p4 ON p4.id = pp4.phenotype_id 

WHERE 
p1.entity_id = 366 AND
p2.entity_id = 366 AND
p3.entity_id = 366 AND
p4.entity_id = 805 AND

p1.value_id = 55 AND
p2.value_id = 156 AND
p3.value_id = 69 AND
p4.value_id IN (169, 170, 171, 172) AND

p2.date >= (p1.date + INTERVAL 1 DAY) AND 
p2.date <= (p1.date + INTERVAL 2 DAY) AND

p3.date >= (p1.date + INTERVAL 2 DAY) AND 
p3.date <= (p1.date + INTERVAL 7 DAY) 

ORDER BY CULTURE_ID, PLANT_ID
LIMIT 0,10;
