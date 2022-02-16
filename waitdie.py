#SAAHIL ANANDE

#1001855308



import pandas as pd

transtable = pd.DataFrame(columns=['transid','tstamp','status','itemslocked'])

locktable = pd.DataFrame(columns=['item','state','lockingtransacion'])

blocktable = pd.DataFrame(columns=['transid','item','operation','lockingtransacion'])

tstamp = 0

infile = []



def main(operation,ids):

    global tstamp
    global transtable

    outputfile.write("Command :"+operation+ ""+ids+"")
    outputfile.write('\n')


    if operation== 'b':
        transid = ids
        tstamp = tstamp + 1
        if transcheck(transid) == 0:
           begin(transid, tstamp)


    if operation== 'r':
        transid = ids
        tstamp = tstamp + 1
        dataitem = items.split('(')[1][0]
        if transcheck(transid) == 1:
            status = getstatus(transid)
            if status == 'active':
                read(transid,dataitem)
            if status == 'aborted':
                outputfile.write('Transaction ' + transid + ' is already Aborted. No changes in tables')
                outputfile.write('\n')
            if status == 'blocked':
                outputfile.write("Operation " + items[0] + " added to queue as transaction " + transid + " is in " + status + " state")
                outputfile.write('\n')
                queue(transid,dataitem,operation)


    if operation == 'w':
            transid = ids
            tstamp = tstamp + 1
            dataitem = items.split('(')[1][0]
            if transcheck(transid) == 1:
                status = getstatus(transid)
                if status == 'active':
                    write(transid,dataitem)
                if status == 'aborted':
                    outputfile.write('Transaction ' + transid + ' is already Aborted. No changes in tables')
                    outputfile.write('\n')
                if status == 'blocked':
                    outputfile.write("Operation " + items[0] + " added to queue as transaction " + transid + " is in " + status + " state")
                    outputfile.write('\n')
                    queue(transid,dataitem,operation)

    if operation== 'e':
        transid = ids
        tstamp = tstamp + 1
        if transcheck(transid) == 1:
            status = getstatus(transid)
            if status == 'blocked':
                outputfile.write("Operation " + items[0] + " added to queue as transaction " + transid + " is in " + status + " state")
                outputfile.write('\n')
                executeque(transid,operation)
            if status == 'aborted':
                outputfile.write('Transaction ' + transid + ' is already Aborted. No changes in tables')
                outputfile.write('\n')
            if status == 'commited':
                outputfile.write('Transaction: '+transid +' is already committed')
                outputfile.write('\n')

            else:
                outputfile.write("transcation "+transid+" commited")
                outputfile.write('\n')
                commit(transid)


def transcheck(id):
    global transtable
    check = transtable.loc[transtable['transid'] == id,['transid','tstamp','status','itemslocked']]

    if check.size !=0:
         return 1
    return 0

def getstatus(id):
    global transtable
    check = transtable.loc[transtable['transid'] == id, ['transid','tstamp','status','itemslocked']]

    return check['status'].to_list()[0]

def begin(id,time):

    global transtable
    global locktable
    global blocktable

    outputfile.write("Transaction Begins with ID : " + id + " :Record is added to Transaction Table with TID= " + id + " and timestamp= " + str(time) + " and state = active")
    outputfile.write('\n')

    transtable = transtable.append(pd.Series([id, time, 'active', 'none'], index=transtable.columns ), ignore_index=True)

def read(id, data):
    global transtable
    global locktable

    #check if the data is in the locked in the locktable

    lockcheck = locktable.loc[locktable['item'] == data,['item','state','lockingtransacion']]

    # if data exist check or read or write lock
    if lockcheck.size > 0:
        flag = False
        for items in lockcheck.iterrows():
            if items[1][0] == data and items[1][1] == 'wl':
                flag = True
                break
        if flag:
            #if the lock is state is write lock perform wait and die
            wait(id,data,'r')

        else:
            # if the lock is state is read lock shared the lock
            outputfile.write("Transaction " + id + " acquired a read lock on data item " + data + "sharing from another transcation")
            outputfile.write('\n')
            locktable = locktable.append(pd.Series([data, 'rl', id], index=locktable.columns), ignore_index=True)

    else:
        #if data is not locked by any transcation give rl to this transaction
        outputfile.write("Transaction " + id + " acquired a read lock on data item " + data )
        outputfile.write('\n')
        locktable = locktable.append(pd.Series([data, 'rl', id], index=locktable.columns), ignore_index=True)


def write(id,data):
    global transtable
    global locktable

    # check if the data is in the locked in the locktable

    lockcheck = locktable.loc[locktable['item'] == data, ['item', 'state', 'lockingtransacion']]

    for x in lockcheck.iterrows():
        getstatefromlock = x[1][1]

        getlockingtransaction = x[1][2]


    #if the data is not locked give the transaction write lock
    if lockcheck.size == 0:
        outputfile.write("Transaction " + id + " acquired a read lock on data item " + data)
        outputfile.write('\n')
        locktable = locktable.append(pd.Series([data, 'wl', id], index=locktable.columns), ignore_index=True)

    #if the data is read lock upgrade the lock to write lock
    if lockcheck.size > 0 and getstatefromlock == 'rl' and getlockingtransaction == id:
        outputfile.write("Transaction " + id + " upgraded from read lock to write lock on data item " + data)
        outputfile.write('\n')
        #update the lock in the locktable
        locktable.loc[locktable['item'] == data, ['state']] = 'wl'

    #if the data is write lock or readlock by another transation
    else:

        wait(id,data,'w')


def wait(id,data,operation):

    global locktable
    global transtable
    global blocktable

    # check if the data is in the locked in the locktable

    check = locktable.loc[locktable['item'] == data, ['item', 'state', 'lockingtransacion']]

    #getholdingid = check['lockingtransacion'].to_list()[0]

    for x in check['lockingtransacion'].to_list():
        if x != id:

            #get the timestamps for current and lockholding trancation
            search = transtable.loc[transtable['transid'] == id, ['transid', 'tstamp', 'status', 'itemslocked']]

            currentts = search['tstamp'].to_list()[0]

            search2 = transtable.loc[transtable['transid'] == x, ['transid', 'tstamp', 'status', 'itemslocked']]

            holdingts = search2['tstamp'].to_list()[0]

            #compare the time stamps if the older transcation requesting lock the current transcation abort itself
            if currentts > holdingts:
                outputfile.write("Transaction " + id + " is aborted (state = Aborted)")
                outputfile.write('\n')
                abort(id)
            #if the current transcation is requesting lock it is allow to wait
            else:
                outputfile.write("Transaction " + id + "goes into blocked state (state = blocked)")
                outputfile.write('\n')
                transtable.loc[transtable['transid'] == id, ['status']] = 'blocked'
                blocktable = blocktable.append(pd.Series([id, data, operation, x], index=blocktable.columns),ignore_index=True)


def queue(id,data,trans):
    global blocktable

    #add the transcation in the queue
    list = blocktable.loc[blocktable['transid'] == id,['transid','item','operation','lockingtransacion']]
    for operation in list['lockingtransacion'].to_list():
        blocktable = blocktable.append(pd.Series([id, data, trans, operation], index=blocktable.columns ), ignore_index=True)

def executeque(id,trans):
    global blocktable

    #remove the transation from the queue
    list = blocktable.loc[blocktable['transid'] == id,['transid','item','operation','lockingtransacion']]
    for operation in list['lockingtransacion'].to_list():
        blocktable = blocktable.append(pd.Series([id, '', trans, operation], index=blocktable.columns ), ignore_index=True)

def abort(id):
    global transtable
    global locktable
    global blocktable

    #update status to aborted in transtable
    transtable.loc[transtable['transid'] == id, ['status']] = 'aborted'

    locktable = locktable.loc[locktable['lockingtransacion'] != id]

    blocktable = blocktable.loc[blocktable['transid'] != id]

    list = blocktable.loc[blocktable['lockingtransacion'] == id,['transid','item','operation','lockingtransacion']]

    for x in list.iterrows():

        tranid = x[1][0]

        dataitem = x[1][1]

        getcount = locktable.loc[(locktable['item'] == dataitem) & (locktable['lockingtransacion'] != tranid)]

        if getcount.size > 0:

            list = blocktable.loc[(blocktable['lockingtransacion'] == id) & (blocktable['transid'] != tranid), ['transid','item','operation','lockingtransacion']]

    for row in list.iterrows():

        tranid = row[1][0]

        dataitem = row[1][1]

        getcountblock = blocktable.loc[(blocktable['transid'] == tranid) & (blocktable['item'] == dataitem)]

        if getcountblock.size > 1:
            blocktable = blocktable.loc[(blocktable['item'] != dataitem) | (blocktable['lockingtransacion'] != id)]
        else:
            #release lock which where locked by the transcation
            blocktable = blocktable.loc[(blocktable['item'] != dataitem) | (blocktable['lockingtransacion'] != id)]
            outputfile.write("Operations " + row[1][2] + " in queue are executed")
            outputfile.write('\n')
            transtable.loc[transtable['transid'] == tranid, ['status']] = 'active'
            main(row[1][2],row[1][0])


def commit(id):
    global transtable
    global locktable
    global blocktable

    #update status to aborted in transtable
    transtable.loc[transtable['transid'] == id, ['status']] = 'commited'

    locktable = locktable.loc[locktable['lockingtransacion'] != id]

    blocktable = blocktable.loc[blocktable['transid'] != id]

    list = blocktable.loc[blocktable['lockingtransacion'] == id,['transid','item','operation','lockingtransacion']]


    for x in list.iterrows():

        tranid = x[1][0]

        dataitem = x[1][1]

        getcount = locktable.loc[(locktable['item'] == dataitem) & (locktable['lockingtransacion'] != tranid)]

        if getcount.size > 0:

            list = blocktable.loc[(blocktable['lockingtransacion'] == id) & (blocktable['transid'] != tranid), ['transid','item','operation','lockingtransacion']]

    for row in list.iterrows():

        tranid = row[1][0]

        dataitem = row[1][1]

        getcountblock = blocktable.loc[(blocktable['transid'] == tranid) & (blocktable['item'] == dataitem)]

        if getcountblock.size > 1:
            blocktable = blocktable.loc[(blocktable['item'] != dataitem) | (blocktable['lockingtransacion'] != id)]
        else:
            # release lock which where locked by the transcation
            blocktable = blocktable.loc[(blocktable['item'] != dataitem) | (blocktable['lockingtransacion'] != id)]
            outputfile.write("Operations " + row[1][2] + " in queue are executed")
            outputfile.write('\n')
            transtable.loc[transtable['transid'] == tranid, ['status']] = 'active'
            main(row[1][2],row[1][0])

    # print("TRANSCARTION TABLE----------------------------------------------------------------------------\n")
    # print(transtable)
    # print("LOCK TABLE ------------------------------------------------------------------------------------\n")
    # print(locktable)
    # print("BLOCK TABLE -----------------------------------------------------------------------------------\n")
    # print(blocktable)


outputfile = open("output4waitanddie.txt", 'w')

with open('input4.txt', 'r') as file:  # reading the input file
    for line in file.readlines():
        infile.append(line)
        infile = [tr.split(';')[0] for tr in infile]

    for items in infile:
        main(items[0],items[1])

if __name__ == '__main__':
    main(items[0],items[1])
    print("-----------------------------CHECK OUTPUT.txt file-----------------------------------")

#references:

#https://stackoverflow.com/questions/17071871/how-do-i-select-rows-from-a-dataframe-based-on-column-values

#https://github.com/nandini0727/Two-Phase-Locking-Protocol

#https://www.geeksforgeeks.org/introduction-to-timestamp-and-deadlock-prevention-schemes-in-dbms/
