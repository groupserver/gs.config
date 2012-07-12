DATABASE_USER="gstestdbbeta3pre1user"
DATABASE_NAME="gstestdbbeta3pre1"

dbSetupDone = False

from commands import getstatusoutput as execute
import sys
import os

def dbsetup():
    print "setting up database %s with user %s" % (DATABASE_NAME,DATABASE_USER)
    code,result = execute("createdb -U%s %s" % (DATABASE_USER,DATABASE_NAME))
    if code:
        print result
        print "Database either already existed, or some other error occurred."
        sys.exit(1)
        
def dbTable(module, filename, dropTables=[]):
    path = module.__path__[0]
    sql_filepath = os.path.join(path,filename)
    for table in dropTables:
        print "dropping table %s" % table
        execute("echo 'drop table %s' | psql -U%s %s" % (table,DATABASE_USER,DATABASE_NAME))
    
    print "setting up table"
    code,result = execute("cat %s | psql -U%s %s" % (sql_filepath,
                                                     DATABASE_USER,
                                                     DATABASE_NAME))
    if code:
        print result
        print "Table either already existed, or some other error occurred."
        sys.exit(1)
        
def dbteardown():
    print "destroying database %s" % DATABASE_NAME
    code,result = execute("dropdb -U%s %s" % (DATABASE_USER,DATABASE_NAME))
    if code:
        print result
        print "Database was either already destroyed, or some other error occurred."
        sys.exit(1)
    
