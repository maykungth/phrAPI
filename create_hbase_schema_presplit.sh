#!/bin/bash
# NUM_RS is number of region servers in HBase cluster
NUM_RS=15

#{ BLOOMFILTER => 'ROW', VERSIONS => 1, BLOCKCACHE => true } are default
NUM_RS=$NUM_RS+1
RS_KEY=""
step=$((1000/$NUM_RS))
for ((i=step; i<1000 ; i+=step))
do
    if ((i+step<1000))
    then
        if ((i<10))
        then
        RS_KEY="$RS_KEY""'u00""$i',"
        elif ((i<100)) 
        then
        RS_KEY="$RS_KEY""'u0""$i',"
        else
        RS_KEY="$RS_KEY""'u""$i',"
        fi
    else
        RS_KEY="$RS_KEY""'u""$i'"
    fi
done
RS_KEY="[$RS_KEY]"
echo $RS_KEY

#echo "
#create 'EncTable','enc', SPLITS => $RS_KEY ; 
#create 'MetaTable','pp' " | hbase shell
