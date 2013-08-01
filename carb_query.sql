SELECT 
pl.culture_id AS culture,
pl.subspecies_id AS cultivar,
a.id AS aliquot, 
als.sample_id AS sample,
p1.number AS C6, LOG(p1.number) AS C6_log,
p2.number AS Glu, LOG(p2.number) AS Glu_log,
p3.number AS Fru, LOG(p3.number) AS Fru_log,
p4.number AS Sac, LOG(p4.number) AS Sac_log,
p_treatment.value_id AS treatment
FROM
aliquots a
JOIN phenotype_aliquots AS pa1 ON a.id = pa1.aliquot_id
JOIN phenotypes p1 ON p1.id = pa1.phenotype_id
JOIN phenotype_aliquots AS pa2 ON a.id = pa2.aliquot_id
JOIN phenotypes p2 ON p2.id = pa2.phenotype_id
JOIN phenotype_aliquots AS pa3 ON a.id = pa3.aliquot_id
JOIN phenotypes p3 ON p3.id = pa3.phenotype_id
JOIN phenotype_aliquots AS pa4 ON a.id = pa4.aliquot_id
JOIN phenotypes p4 ON p4.id = pa4.phenotype_id
JOIN aliquot_plants AS ap ON ap.aliquot_id = a.id
JOIN plants AS pl ON pl.id = ap.plant_id
JOIN phenotype_plants AS pp ON pl.id = pp.plant_id
JOIN phenotypes AS p_treatment ON p_treatment.id = pp.phenotype_id
JOIN aliquot_samples AS als ON als.aliquot_id = a.id
WHERE 
p1.value_id = 212 AND
p2.value_id = 131 AND
p3.value_id = 132 AND
p4.value_id = 142 AND
p_treatment.value_id IN (169,170,171,172)
GROUP BY a.id
ORDER BY culture
