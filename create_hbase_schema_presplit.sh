#!/bin/bash
# NUM_RS is number of region servers in HBase cluster
NUM_RS=4

#{ BLOOMFILTER => 'ROW', VERSIONS => 1, BLOCKCACHE => true } are default
RS_KEY=""
for i in $(seq 2 $NUM_RS)
do
    if ((i!=$NUM_RS))
    then
        RS_KEY="$RS_KEY""'s""$i',"
    else
        RS_KEY="$RS_KEY""'s""$i'"
    fi
done
RS_KEY="[$RS_KEY]"
echo $RS_KEY

#echo "
#create 'EncTable','enc', SPLITS => $RS_KEY ; 
#create 'MetaTable','pp' " | hbase shell
