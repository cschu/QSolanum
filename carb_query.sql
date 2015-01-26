SELECT 
pl.culture_id AS cultureID,
cu.description AS culture,
cu.location_id AS locationID,
loc.name AS location,
pl.subspecies_id AS cultivarID,
sub.cultivar AS cultivar,
a.id AS aliquot, 
als.sample_id AS sample,
p1.number AS C6, LOG(p1.number) AS C6_log,
p2.number AS Glu, LOG(p2.number) AS Glu_log,
p3.number AS Fru, LOG(p3.number) AS Fru_log,
p4.number AS Sac, LOG(p4.number) AS Sac_log,
p_treatment.value_id AS treatmentID,
v.value AS treatment
FROM
aliquots a
LEFT OUTER JOIN phenotype_aliquots AS pa1 ON a.id = pa1.aliquot_id
LEFT OUTER JOIN phenotypes p1 ON p1.id = pa1.phenotype_id
LEFT OUTER JOIN phenotype_aliquots AS pa2 ON a.id = pa2.aliquot_id
LEFT OUTER JOIN phenotypes p2 ON p2.id = pa2.phenotype_id
LEFT OUTER JOIN phenotype_aliquots AS pa3 ON a.id = pa3.aliquot_id
LEFT OUTER JOIN phenotypes p3 ON p3.id = pa3.phenotype_id
LEFT OUTER JOIN phenotype_aliquots AS pa4 ON a.id = pa4.aliquot_id
LEFT OUTER JOIN phenotypes p4 ON p4.id = pa4.phenotype_id
LEFT OUTER JOIN aliquot_plants AS ap ON ap.aliquot_id = a.id
LEFT OUTER JOIN plants AS pl ON pl.id = ap.plant_id
LEFT OUTER JOIN phenotype_plants AS pp ON pl.id = pp.plant_id
LEFT OUTER JOIN phenotypes AS p_treatment ON p_treatment.id = pp.phenotype_id
LEFT OUTER JOIN aliquot_samples AS als ON als.aliquot_id = a.id
LEFT OUTER JOIN cultures AS cu ON cu.id = pl.culture_id
LEFT OUTER JOIN locations AS loc ON loc.id = cu.location_id
LEFT OUTER JOIN subspecies AS sub ON sub.id = pl.subspecies_id
LEFT OUTER JOIN `values` AS v ON v.id = p_treatment.value_id
WHERE 
p1.value_id = 212 AND
p2.value_id = 131 AND
p3.value_id = 132 AND
p4.value_id = 142 AND
p_treatment.value_id IN (169,170,171,172)
GROUP BY a.id
ORDER BY cultureID
