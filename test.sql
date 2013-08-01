select 
P1.sample_id as sample_id, 
P1.id as p1_id, P1.date as p1_date, 
PV1.*,
P2.id as p2_id, P2.date as p2_date,
PV2.*,
PE1.entity_id as pe1_id, PE2.entity_id as pe2_id

from 
phenotypes as P1 
left join phenotypes as P2
on P1.sample_id = P2.sample_id

left join phenotype_values as PV1
on P1.id = PV1.phenotype_id

left join phenotype_values as PV2
on P2.id = PV2.phenotype_id

left join phenotype_entities as PE1
on P1.id = PE1.phenotype_id

left join phenotype_entities as PE2
on P2.id = PE2.phenotype_id

where 
P1.id != P2.id and
P1.object = 'LIMS-Aliquot' and P2.object = 'LIMS-Aliquot' and
PV1.value_id in (55,156,69,163,164) and
PV2.value_id in (55,156,69,163,164) and
PV1.value_id != PV2.value_id and
(PV1.value_id = 55 or (PV1.value_id = 69 and PV2.value_id != 55));

 
