SELECT 
a.id, 
group_concat(DISTINCT ap.plant_id ORDER BY ap.plant_id) AS plant_ids, 
a_s.sample_id, 
COUNT(*), 
p.culture_id, p.subspecies_id, 
c.location_id, c.description, 
a.sample_date, a.amount, a.amount_unit,
p1.date, p1.number AS FW_abs_g,
p2.date, p2.number AS DW_abs_g,
pt.value_id AS treatment,
p1.number >= p2.number AS sanity1_passed,
p1.number / p2.number AS FW_DW,
0 <= p1.number / p2.number <= 15 AS sanity2_passed

FROM aliquots a
JOIN aliquot_plants ap ON ap.aliquot_id = a.id
JOIN aliquot_samples a_s ON a_s.aliquot_id = a.id
JOIN plants p ON p.id = ap.plant_id
JOIN cultures c ON c.id = p.culture_id

JOIN phenotype_plants AS pp1 ON pp1.plant_id = p.id
JOIN phenotypes AS p1 ON p1.id = pp1.phenotype_id 

JOIN phenotype_plants AS pp2 ON pp2.plant_id = p.id
JOIN phenotypes AS p2 ON p2.id = pp2.phenotype_id 

JOIN phenotype_plants AS ppt ON ppt.plant_id = p.id
JOIN phenotypes AS pt ON pt.id = ppt.phenotype_id 


WHERE
a.amount IS NOT NULL AND

p1.entity_id = 366 AND
p2.entity_id = 366 AND
pt.entity_id = 805 AND

p1.value_id = 55 AND
p2.value_id = 69 AND
pt.value_id IN (169, 170, 171, 172) AND

p2.date >= (p1.date + INTERVAL 1 DAY) AND
p2.date <= (p1.date + INTERVAL 7 DAY)

GROUP BY a.id, a_s.sample_id
LIMIT 0,10;