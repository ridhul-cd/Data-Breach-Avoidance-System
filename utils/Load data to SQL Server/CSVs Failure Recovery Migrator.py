#CSVs Migrator: Migrate CSV or XLSX Files from Local PC to SQL Server with ease.
#Contributed by Sairam Parshi

'''


Future Updates:
>Preserve the order of records even with multi threading
>Deal with higher size files by not loading whole contents to RAM
>Empty cells repesentation EmptyCells=[spaces,'','--', '-','n/a','N/A','null','na', 'NA']
>Give time estimation (acc to file size/ num of rows and threads) 5 MB per minute (200 threads)
>Background running thread updating % of import every 5 mins
>4,598 is reading as str
>Auto initiate failed rows
>dynamically detect date type with library <or> Add Date Format externally, Like: mm/dd/yyyy (Ex: 5/30/2022)
https://www.geeksforgeeks.org/python-datetime-strptime-function/
>Use LCA in trees to set right datatype when colflict


SPEED: 300MB/ hour (200 threads)
'''


#--------------------Input Section-----------------------------------------------------------------


MainFile="paths.txt" # Which contains paths of all CSVs/ XLSXs
MaxThreads=10
preserve_source_file_row_order=True #Requires more computation


getPathsFromLoadFilesFolder=False
delim=","

#SQL Server Details:



#Driver="SQL Server Native Client 11.0"


Driver="SQL Server"
ServerName="devdbinstance01"
DatabaseName="MyBankCardsManager"
UserID="ServerAdminPro"
Password="S3cure#Adm!nPr0"

#-------------------------------------------------------------------------------------------------------------------




#- - - - - -
def install(package):
    # This function will install a package if it is not present
    from importlib import import_module
    try:
        import_module(package)
    except:
        from sys import executable as se
        from subprocess import check_call
        check_call([se,'-m','pip','-q','install',package])


for package in ['pypyodbc','csv','threading','time','codecs','pandas','os']:
    install(package)
#- - - - - -


import pypyodbc
import csv
import threading
import time
import codecs
import pandas as pd
import os

#---------Datatype setting logic--------------

precedence=['VARCHAR','DATETIME','DATE','FLOAT','BIGINT','INT','EMPTYSTRING'] #Precedence Of Datatypes




def isFloat(mystr):

    if float(mystr)-int(float(mystr))==0:
        return whatisit(str(int(float(mystr))))
    else:
        a=-1.79e+308
        b=-2.23e-308
        c=2.23e-308
        d=1.79e+308
        if a<=float(mystr)<=b or c<=float(mystr)<=d:
            return 'FLOAT'
        else:
            return 'VARCHAR'

def isfloatconvertable(numstr):
    try:
        float(numstr)
        return True
    except ValueError:
        return False


def isWhichInt(mystr):
    a=-2147483648
    b=2147483647
    c=-9223372036854775808
    d=9223372036854775807
    if len(mystr)>1 and mystr[0]=='0':
        return 'VARCHAR'
    if len(mystr)>=20:
        return 'VARCHAR'
    if a<=int(mystr)<=b:
        return 'INT'
    elif c<=int(mystr)<=d:
        return 'BIGINT'
    else:
        return 'VARCHAR'


def whatisit(mystr):
    if mystr=='':
        return 'EMPTYSTRING'
    if mystr.isnumeric():
        return isWhichInt(mystr)
    if len(mystr)>=2 and (mystr[0]=='-' and mystr[1::].isnumeric()):
        return isWhichInt(mystr)
    '''
    if mystr.replace(',','').isnumeric():
        return isWhichInt(mystr.replace(',',''))
    '''
    doublechecker=mystr.replace('.','',1)
    if isfloatconvertable(mystr) and str(float(mystr.lower())) in ['inf','-inf','infinity','-infinity']:
        return 'FLOAT'
    if isfloatconvertable(mystr) or doublechecker.isnumeric():
        return isFloat(mystr)
    
    if (len(mystr)>=2 and (mystr[0]=='-' and mystr[1::].replace('.','',1).isnumeric())):
        return isFloat(mystr)
    
    if mystr.isalnum():
        return 'VARCHAR'
    remsps=mystr.replace(' ','')
    if remsps.isalnum():
        return 'VARCHAR'
    checkdatetime=mystr.split()
    
    if len(checkdatetime)==1:
        datefields=checkdatetime[0].split('-')
        #DATETIME FORMAT: YYYY-MM-DD HH:MM:SS
        if len(datefields)==3 and (datefields[0].isnumeric() and datefields[1].isnumeric() and datefields[2].isnumeric()):
            if len(datefields[0])==4 and 0<int(datefields[1])<13 and 0<int(datefields[2])<32:
                return 'DATE'
            else:
                return 'VARCHAR'
        else:
            return 'VARCHAR'
    elif len(checkdatetime)==2:
        if whatisit(checkdatetime[0])=='DATE':
            t=checkdatetime[1].split(':')
            if len(t)==3 and (t[0].isnumeric() and t[1].isnumeric() and isfloatconvertable(t[2])) and (0<=int(t[0])<=24 and 0<=int(t[1])<=60 and 0<=int(float(t[2]))<=60):
                return 'DATETIME'
            else:
                return 'VARCHAR'
        else:
            return 'VARCHAR'
    return 'VARCHAR'


#- - - - - - - - Connection establishment details- - - - - - - - - - - -

def fast_computepaths(directory,outputFileName): # Computes Paths
    
    myfiles=[]
    for filename in os.listdir(directory):
        f = os.path.join(directory, filename)
        if os.path.isfile(f):
            myfiles.append(str(f))
    for i in range(len(myfiles)):
        p=myfiles[i].split('\\')
        myfiles[i]='/'.join(p)
    with open(outputFileName,"w") as paths:
        for i in myfiles:
            if i.split('.')[-1].lower() in {'csv','xlsx'}:
                paths.write(i+"\n")
#'/'.join(os.getcwd().split('\\'))+"/"+                
if getPathsFromLoadFilesFolder:
    loadfiles_pwd="Load Files"
    fast_computepaths(loadfiles_pwd,"Paths.txt")

print("Hey There! Please wait while Establishing Connection with SQL Server\n")
a="Driver={"+Driver+"};"
b="Server="+ServerName+";"
c="Database="+DatabaseName+";"
d="uid="+UserID+";pwd="+Password

conn_str = (
    r'Driver={ODBC Driver 17 for SQL Server};'
    r'Server=tcp:devdbinstance01.database.windows.net,1433;'
    r'Database=MyBankCardsManager;'
    r'Uid=ServerAdminPro;'
    r'Pwd=S3cure#Adm!nPr0;'
    r'Encrypt=yes;'
    r'TrustServerCertificate=no;'
    r'Connection Timeout=30;'
)
cnxn = pypyodbc.connect(conn_str)
print(cnxn)

#Can get this connection string from Azure portal


mytables=open(MainFile,'r',encoding="utf8",errors='ignore')

mydb=cnxn
cursorObject = mydb.cursor()




myT=list(mytables)

def IntervalSplitter(size,x):

    modu=size%x
    chunk=int((size-modu)/x)
    start=0
    end=chunk
    intervals=[[0 for i in range(2)] for i in range(x)]
    for i in range(x):
        if i==0:
            intervals[i][0]=start
            intervals[i][1]=end
        else:
            intervals[i][0]=intervals[i-1][1]
            intervals[i][1]=intervals[i-1][1]+end
    intervals[x-1][1]+=modu
    return (intervals)




cO=[0 for i in range(MaxThreads)]
mydbc=[0 for i in range(MaxThreads)]
seenError=[False for i in range(MaxThreads)]
connectionString=a+b+c+d


printLock=threading.Lock()
def MultiThreadedInsertion(insertQuery,allrows,i):
    
    if mydbc[i]==0 and not seenError[i]:
        
        mydbc[i]=pypyodbc.connect(conn_str, autocommit=True)
        cO[i]=mydbc[i].cursor()
        seenError[i]=False
        
        
    try:
        cO[i].executemany(insertQuery,allrows)
    except Exception as e:
        printLock.acquire()
        print(f">>Exception: Thread {i} Terminated Midway Insertion",e)
        seenError[i]=True
        printLock.release()
        #print(type(e))



def ParallelInsertion(insertQuery,allrows,threads):
    x=threads
    
    intervals=IntervalSplitter(len(allrows),x)
    #print("Thread(s) Load:",intervals)
    t=[0 for i in range(threads)]
    for i in range(threads):
        #print("creating Thread-",i)
        t[i] = threading.Thread(target=MultiThreadedInsertion, args=(insertQuery,allrows[intervals[i][0]:intervals[i][1]],i,))

    print(f"Parallel Insertion Stared with {threads} Threads")
    print(f"Thread Load: {intervals[0][1]+1} rows/Thread\n")
    for i in range(threads):
        t[i].start()
  
    for i in range(threads):
        t[i].join()
    print("Parallel Insertion Done!")
    
#Finding List Of Tables present in the database
cursorObject.execute("SELECT sobjects.name FROM sysobjects sobjects WHERE sobjects.xtype = 'U'")
myresult = cursorObject.fetchall()
allTables=[]
for i in myresult:
    allTables.append(i[0])
def ConvertXLSXtoCSV(t):
    dfs = pd.read_excel(t)
    df=pd.DataFrame(dfs)
    x=t.split('/')
    y=x[-1]
    y=y.split('.')
    y[-1]="csv"
    y='.'.join(y)
    x[-1]=y
    x='/'.join(x)
    df.to_csv(x,index=False)
    return x

for i in myT:
    try:
        t=i.split('\n')
        t=t[0]
        if t=='' or t==' ':
            continue
        print("---------------------Starting and Analysing New table-----------------------\n")

        fields = []
        rows = []
        if "xlsx" in t:
            t=ConvertXLSXtoCSV(t)
        with codecs.open(t, 'r',encoding="utf-8",errors='ignore') as csvfile:
            csvreader = csv.reader(csvfile, delimiter=delim) #¬
            fields = next(csvreader)
            for row in csvreader:
                #print(len(row))
                rows.append(row)
        #print(rows)
        #print("Full Path of CSV:\n",t)
        t=t.split('/')
        t=t[-1]
        t=t.split('.')
        t=t[0]
        print("Table Name:",t)
        j=i.split('\n')
        currentT=list(rows)

        unnamed=0
        for i in range(len(fields)):
            if fields[i]=='':
                unnamed+=1
                fields[i]=f'unnamed{unnamed}'
        cols=fields
        
        mycolslengths=[]
        for row in range(len(currentT)):
            currentT[row].append(str(row))
        rows=currentT
        fields.append('SourceFileRowOrder')
        for eachrow in currentT:
            mycolslengths.append(len(eachrow))
        if min(mycolslengths)!=max(mycolslengths):
            print("All columns lengths:\n",mycolslengths,"\nMin Value: ",min(mycolslengths),"\nMax Value:",max(mycolslengths))
            raise Exception("Inconsistant Number of Columns in the Table")
        print("\nNumber of Columns:",len(cols))#,"\nList of Columns:\n",cols)
        print("Number of Rows: ",len(rows))
        sourcerowcount=len(rows)
        tablename=t
        if tablename in allTables:
            countQuery='SELECT count(*) from "'+tablename+'"'
            cursorObject.execute(countQuery)
            myresult = cursorObject.fetchall()
            targetrowcount=myresult[0][0]
            if (sourcerowcount-targetrowcount)==0:
                print("\nTable already exists and has ",targetrowcount," rows (100% of rows).\nSkipping Current Table.")
                time.sleep(2)
                continue
            
        datatypes=['EMPTYSTRING' for i in range(len(cols))]
        maxisizes=[0 for i in range(len(cols))]

        for eachrow in currentT:       
            row=eachrow
            currentdatatypes=[0 for i in range(len(row))]
            currentsizes=[0 for i in range(len(row))]
            x=-1
            for i in row:
                x+=1
                currentsizes[x]=len(i)
                try:
                    currentdatatypes[x]=whatisit(i)
                except Exception as e:
                    print(i,e)
                    input('')
            for i in range(len(row)):
                if precedence.index(datatypes[i])>precedence.index(currentdatatypes[i]):
                    datatypes[i]=currentdatatypes[i]                        
                maxisizes[i]=max(currentsizes[i],maxisizes[i])
                
        for i in range(len(maxisizes)):
            maxisizes[i]+=10
            if maxisizes[i]>4000:
                maxisizes[i]='MAX'        
        
        
        for i in range(len(datatypes)):
            if datatypes[i]=='EMPTYSTRING':
                datatypes[i]='VARCHAR(5)'
            elif datatypes[i]=='VARCHAR':
                datatypes[i]='NVARCHAR('+str(maxisizes[i])+')'
        
    
        floatCorrection=[]
        for i in range(len(datatypes)):
            if datatypes[i]=='INT' or datatypes[i]=='BIGINT':
                #print(cols[i])
                floatCorrection.append(i)

        for i in floatCorrection:
            for j in range(len(rows)):
                if rows[j][i]!='':
                    rows[j][i]=str(int(float(rows[j][i])))

        print("Datatypes of Columns Computed.\n")
        #print("\nData types list of Table:\n",datatypes)
        p='CREATE TABLE "'+tablename+'" ( '
        columns="("
        #print("Column Names:\n",cols)
        for i in range(len(cols)-1):
            c=cols[i]
            if len(c)>128:
                c=c[0:128]
                cols[i]=c
            p+='"'+cols[i]+'"'
            p+=" "
            p+=datatypes[i]
            p+=","
            columns+=","
        c=cols[len(cols)-1]
        if len(c)>128:
            c=c[0:128]
            cols[i]=c
        p+='"'+cols[len(cols)-1]+'"'
        columns+='"'+cols[len(cols)-1]+'"'
        p+=" "
        p+=datatypes[len(cols)-1]
        p+=");"
        columns+=")"

        print("\nCreate Table Query:\n",p)
        #-------------------------------------------------------------------FINE------------------
        if tablename in allTables:
            countQuery='SELECT count(*) from "'+tablename+'"'
            cursorObject.execute(countQuery)
            myresult = cursorObject.fetchall()
            targetrowcount=myresult[0][0]
            if targetrowcount==0:
                print("Table schema already exists, Inserting rows.")
            elif (sourcerowcount-targetrowcount)==0:
                print("Table already exists and has ",targetrowcount," rows (100% of rows).\nSkipping Current Table.")
                time.sleep(2)
                continue
            elif (sourcerowcount-targetrowcount)>0:
                #######################Deal with failure recovery################################
                print(f"\nTable already exists and has {targetrowcount} rows ({round((targetrowcount/sourcerowcount)*100,1)}% of rows).\n")
                print(f"Inserting remaining {sourcerowcount-targetrowcount} records.\n\n")
                existingRowsQuery=f'select SourceFileRowOrder from [{tablename}]'
                cursorObject.execute(existingRowsQuery)
                existingRowsQueryResult=cursorObject.fetchall()
                existingTargetRowsIDs=[]
                for i in existingRowsQueryResult:
                    existingTargetRowsIDs.append(str(i[0]))
                existingTargetRowsIDs=set(existingTargetRowsIDs)
                #print(existingTargetRowsIDs)
                def filterrows(sourcerow):
                    if sourcerow[-1] not in existingTargetRowsIDs:
                        return True
                    else:
                        return False
                rows=list(filter(filterrows, rows))
                #print(f"1) Filtered number of rows: {len(rows)}")
                pass
                
        else:
            try:
                cursorObject.execute(p)
                cursorObject.commit()
                cnxn.commit()
            except Exception as e:
                print(e)
                print("ERROR: Couldn't Create Table! Skipping Current Table.\n")
                continue
        insertQuery='insert into "'+tablename+'" '+' values ('
        for i in range(len(cols)-1):
            insertQuery+="?,"
        insertQuery+="?)"

        print("\nInsert Query:\n",insertQuery)
        x=-1
        print("\nPlease wait while the data is being inserted!!\n")
        for i in range(len(rows)):
            for j in range(len(rows[0])):
                if rows[i][j]=='':
                    rows[i][j]=None
        allrows=[]
        #print(f"2) Filtered number of rows: {len(rows)}")
        for i in rows:   
            newrow=tuple(i)
            allrows.append(newrow)

        try:
            #print(f"3) Filtered number of allrows: {len(allrows)}")
            ParallelInsertion(insertQuery,allrows,threads=MaxThreads)
        except Exception as e:
            print(e)
            print("ERROR:Couldn't Insert Complete Data!!! :(")
            continue
        else:
            countQuery='SELECT count(*) from "'+tablename+'"'
            cursorObject.execute(countQuery)
            myresult = cursorObject.fetchall()
            targetrowcount=myresult[0][0]
            print(f"\nTABLE LOADING DONE {round((targetrowcount/sourcerowcount)*100,1)}%")
        cnxn.commit()
    except Exception as e:
        print("Error!!\n",e)
        #print("ERROR:Some error other than creating table and inserting rows")
        continue

