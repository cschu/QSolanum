select 
P1.sample_id as sample_id, 
P1.id as p1_id, P1.date as p1_date, 
PV1.*,
P2.id as p2_id, P2.date as p2_date,
PV2.*,
P3.id as p3_id, P3.date as p3_date,
PV3.*,
PE1.entity_id as entity_id

from 
phenotypes as P1 
left join phenotypes as P2
on P1.sample_id = P2.sample_id

left join phenotypes as P3
on P1.sample_id = P3.sample_id

left join phenotype_values as PV1
on P1.id = PV1.phenotype_id

left join phenotype_values as PV2
on P2.id = PV2.phenotype_id

left join phenotype_values as PV3
on P3.id = PV3.phenotype_id

left join phenotype_entities as PE1
on P1.id = PE1.phenotype_id

left join phenotype_entities as PE2
on P2.id = PE2.phenotype_id

left join phenotype_entities as PE3
on P3.id = PE3.phenotype_id

where 
P1.id != P2.id and P1.id != P3.id and P2.id != P3.id and
P1.object = 'LIMS-Aliquot' and P2.object = 'LIMS-Aliquot' and P3.object = 'LIMS-Aliquot' and
((PV1.value_id = 55 and PV2.value_id = 156 and PV3.value_id = 69) or 
(PV1.value_id = 163 and PV2.value_id = 164 and (PV3.value_id = 69
or PV3.value_id = 225))) and
(PE1.entity_id in (12,366) and PE1.entity_id = PE2.entity_id and PE1.entity_id = PE3.entity_id);




 
