__author__ = 'Maykungth'
# 18/8/2558
import happybase
Master2='172.30.224.142'
con=happybase.Connection(Master2)
con.open()
alltable = con.tables()

creatingTable=False
# Reset Delete Table
# con.delete_table('MetaTable',disable=True)
# con.delete_table('EncTable',disable=True)


# Creating Hbase schema #
if creatingTable:
    if ('MetaTable' and 'EncTable') not in alltable:
    #Create Table and column
        print "Creating table : " + 'MetaTable'
        con.create_table(
        'MetaTable',{
                'pp':dict(max_versions=1)
            }
        )
        print "Creating table : " + 'EncTable'
        con.create_table(
        'EncTable',{
                'enc':dict(max_versions=1)
            }
        )
    metaTable = con.table('MetaTable')
    encTable = con.table('EncTable')

    print('TableMeta Colfam: '+ str(metaTable._column_family_names()))
    print('TableEnc Colfam: '+ str(encTable._column_family_names()))

