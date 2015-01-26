#!/bin/bash

#INFILE=short_treatments.csv
INFILE=$1

echo 'START TRANSACTION;'


for ROW in $(cut -f 1,3 -d , $INFILE)
do
 #echo $ROW
 ARR=(${ROW//,/ });
 # echo $ARR
 CMD0="INSERT INTO phenotypes VALUES (NULL, NULL, 'LIMS-Aliquot', 4, CURDATE(), CURTIME(), NULL, 805, ${ARR[1]}, NULL);"
 CMD1="INSERT INTO phenotype_plants VALUES (NULL, ${ARR[0]}, LAST_INSERT_ID());"
 echo $CMD0;
 echo $CMD1;
done

echo 'COMMIT;'

#INSERT INTO phenotypes 
#VALUES (NULL, NULL, 'LIMS-Aliquot', 4, CURDATE(), CURTIME(), NULL, -180181, $VALUE_ID, NULL);
#
#INSERT INTO phenotype_plants
#VALUES (NULL, $PLANT_ID, LAST_INSERT_ID());
