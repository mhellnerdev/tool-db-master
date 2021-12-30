from flask import render_template, request, redirect, url_for
from tooldb.main import executeQuery, executeReadQuery, executeReadQueryAll, connection
from tooldb import app


#return main wip page
@app.route("/wip")
def wip():
    query = "SELECT * FROM wip"
    wipTable = executeReadQueryAll(connection, query)
    invalid = request.args.get("invalid")
    if(invalid):
        invalid = int(invalid)
    return render_template("wip.html", wipTable=wipTable, invalid = invalid)

#submit new wip information to the database, return "edit wip" page to build contents of wip
@app.route("/addWipSubmit")
def addWipSubmit():
    wipNum = request.args.get("wipNum")
    wipRev = request.args.get("wipRev")
    list = (wipNum, wipRev)
    query = "SELECT number FROM wip" 
    wipList = executeReadQueryAll(connection, query)
    wipNums = [i[0] for i in wipList]
    insert = ("""
    INSERT INTO wip (number, rev)
    VALUES (?,?)
    """)
    if(wipNum in wipNums):
        return redirect(url_for('wip', invalid = 1))
    else:
        executeQuery(connection, insert, list)
        idQuery = "SELECT last_insert_rowid();"
        wipId = executeReadQueryAll(connection, idQuery)
        return redirect(url_for('wipEdit', wipId=wipId))

#from wipEdit: adds a work instruction to the present wip
@app.route("/addWiToWip")
def addWiToWip():
    wipId = request.args.get("wipId")
    inspectionId = request.args.get("inspectionId")
    last = request.args.get("last")
    line = request.args.get("line")
    if not last:
        sequence = 1
    else:
        sequence = last
    list = (wipId, inspectionId, sequence, line)
    query = ("""
    INSERT INTO matchWiWip (wipId, inspectionId, sequence, line)
    VALUES (?,?,?,?)
    """)
    executeQuery(connection, query, list)
    return redirect(url_for('wipEdit', wipId = wipId))

#from wipEdit: removes an existing wip/wi association
@app.route("/deleteWiFromWip")
def deleteWiFromWip():
    id = request.args.get("id")
    idInt = int(id)
    wipId = request.args.get("wipId")
    line = request.args.get("line")
    delete = ("""
    DELETE FROM matchWiWip
    WHERE id = ? 
    """)
    executeQuery(connection, delete, (idInt,))

    query = "SELECT * FROM matchWiWip WHERE wipId=? AND line=? ORDER BY sequence"
    table = executeReadQuery(connection, query, (wipId,line))
    col = [row[3] for row in table]
    for i in range(len(col)):
        if col[i] != (i+1):
            update = "UPDATE matchWiWip SET sequence=? WHERE id=? "
            list = (i+1, table[i][0])
            executeQuery(connection, update, list)

    return redirect(url_for('wipEdit', wipId=wipId))

#returns wip edit page
@app.route("/wipEdit")
def wipEdit():
    wipId = request.args.get("wipId")
    line = request.args.get("line")
    printPage = request.args.get("print")
    queryWip = ("""
    SELECT inspection.owner, matchWiWip.sequence, inspection.workstation, inspection.wiText, inspection.samples,
    inspection.description, inspection.instrument, inspection.criteria, matchWiWip.id, wip.number, inspection.line
    FROM ((matchWiWip
    INNER JOIN inspection ON inspection.id = matchWiWip.inspectionId)
    INNER JOIN wip ON wip.id = matchWiWip.wipId)
    WHERE wip.id = ?
    ORDER BY inspection.line, sequence
    """)
    queryWiAll = (""" 
    SELECT inspection.owner, inspection.id, inspection.workstation, inspection.wiText, inspection.samples,
    inspection.description, inspection.instrument, inspection.criteria, inspection.line
    FROM inspection
    """)
    wipTable = executeReadQuery(connection, queryWip, (wipId,))
    wiAllTable = executeReadQueryAll(connection, queryWiAll)
    wipNum = wipTable[0][9]
    shaftTable = [row for row in wipTable if row[10]=="shaft"]
    bodyTable = [row for row in wipTable if row[10]=="body"]
    
    mainLineTable = [row for row in wipTable if row[10]=="main line"]
    packTable = [row for row in wipTable if row[10]=="pack"]
    #make list of step numbers from the wipTable
    shaftSteps = [int(i[1]) for i in shaftTable]
    bodySteps = [int(i[1]) for i in bodyTable]
    mainLineSteps = [int(i[1]) for i in mainLineTable]
    packSteps = [int(i[1]) for i in packTable]
    values = {}
    #if there are items in the wiptable, loop through and check if multiple steps
    if shaftSteps:
        shaftSequence = []
        for a in list(set(shaftSteps)):
            shaftSequence.append(shaftSteps.index(a))
        shaftList = []
        for a in shaftSequence:
            shaftList.append(shaftSteps.count(shaftSteps[a]))
        values['shaftList'] = shaftList
        values['shaftSequence'] = shaftSequence
        values['shaftTable'] = shaftTable
        values['shaftLast'] = shaftSteps[-1] + 1

    if bodySteps:
        bodySequence = []
        for a in list(set(bodySteps)):
            bodySequence.append(bodySteps.index(a))
        bodyList = []
        for a in bodySequence:
            bodyList.append(bodySteps.count(bodySteps[a]))
        values['bodyList'] = bodyList
        values['bodySequence'] = bodySequence
        values['bodyTable'] = bodyTable
        values['bodyLast'] = bodySteps[-1] + 1

    if mainLineSteps:
        mainLineSequence = []
        for a in list(set(mainLineSteps)):
            mainLineSequence.append(mainLineSteps.index(a))
        mainLineList = []
        for a in mainLineSequence:
            mainLineList.append(mainLineSteps.count(mainLineSteps[a]))
        values['mainLineList'] = mainLineList
        values['mainLineSequence'] = mainLineSequence
        values['mainLineTable'] = mainLineTable
        values['mainLineLast'] = mainLineSteps[-1] + 1

    if packSteps:
        packSequence = []
        for a in list(set(packSteps)):
            packSequence.append(packSteps.index(a))
        packList = []
        for a in packSequence:
            packList.append(packSteps.count(packSteps[a]))
        values['packList'] = packList
        values['packSequence'] = packSequence
        values['packTable'] = packTable
        values['packLast'] = packSteps[-1] + 1

    shaftTableAll = [row for row in wiAllTable if row[8]=="shaft"]
    shaftIdAll = [int(i[1]) for i in shaftTableAll]
    shaftStepsAll = [1]
    count = 1
    for i in range(len(shaftIdAll)-1):
        if shaftIdAll[i+1] == shaftIdAll[i]:
            pass
        else:
            count = count + 1
        shaftStepsAll.append(count)

    shaftSequenceAll = []
    for a in list(set(shaftStepsAll)):
        shaftSequenceAll.append(shaftStepsAll.index(a))
    shaftListAll = []
    for a in shaftSequenceAll:
        shaftListAll.append(shaftStepsAll.count(shaftStepsAll[a]))

    values['shaftTableAll'] = shaftTableAll
    values['shaftListAll'] = shaftListAll
    values['shaftLastAll'] = shaftStepsAll[-1] + 1
    values['shaftSequenceAll'] = shaftSequenceAll

    bodyTableAll = [row for row in wiAllTable if row[8]=="body"]
    bodyIdAll = [int(i[1]) for i in bodyTableAll]
    bodyStepsAll = [1]
    count = 1
    for i in range(len(bodyIdAll)-1):
        if bodyIdAll[i+1] == bodyIdAll[i]:
            pass
        else:
            count = count + 1
        bodyStepsAll.append(count)

    bodySequenceAll = []
    for a in list(set(bodyStepsAll)):
        bodySequenceAll.append(bodyStepsAll.index(a))
    bodyListAll = []
    for a in bodySequenceAll:
        bodyListAll.append(bodyStepsAll.count(bodyStepsAll[a]))

    values['bodyTableAll'] = bodyTableAll
    values['bodyListAll'] = bodyListAll
    values['bodyLastAll'] = bodyStepsAll[-1] + 1
    values['bodySequenceAll'] = bodySequenceAll

    mainLineTableAll = [row for row in wiAllTable if row[8]=="main line"]
    mainLineIdAll = [int(i[1]) for i in mainLineTableAll]
    mainLineStepsAll = [1]
    count = 1
    for i in range(len(mainLineIdAll)-1):
        if mainLineIdAll[i+1] == mainLineIdAll[i]:
            pass
        else:
            count = count + 1
        mainLineStepsAll.append(count)

    mainLineSequenceAll = []
    for a in list(set(mainLineStepsAll)):
        mainLineSequenceAll.append(mainLineStepsAll.index(a))
    mainLineListAll = []
    for a in mainLineSequenceAll:
        mainLineListAll.append(mainLineStepsAll.count(mainLineStepsAll[a]))

    values['mainLineTableAll'] = mainLineTableAll
    values['mainLineListAll'] = mainLineListAll
    values['mainLineLastAll'] = mainLineStepsAll[-1] + 1
    values['mainLineSequenceAll'] = mainLineSequenceAll

    packTableAll = [row for row in wiAllTable if row[8]=="pack"]
    packIdAll = [int(i[1]) for i in packTableAll]
    packStepsAll = [1]
    count = 1
    for i in range(len(packIdAll)-1):
        if packIdAll[i+1] == packIdAll[i]:
            pass
        else:
            count = count + 1
        packStepsAll.append(count)

    packSequenceAll = []
    for a in list(set(packStepsAll)):
        packSequenceAll.append(packStepsAll.index(a))
    packListAll = []
    for a in packSequenceAll:
        packListAll.append(packStepsAll.count(packStepsAll[a]))

    values['packTableAll'] = packTableAll
    values['packListAll'] = packListAll
    values['packLastAll'] = packStepsAll[-1] + 1
    values['packSequenceAll'] = packSequenceAll

    values['wipNum'] = wipNum
    values['wipId'] = wipId
    values['line'] = line
    values['wiAllTable'] = wiAllTable

    if(printPage == 1):
        return render_template("wipEdit.html", **values)
    return render_template("wipEdit.html", **values)



@app.route("/moveWiUp")
def moveWiUp():
    id = request.args.get("id")
    wipId = request.args.get("wipId")
    line = request.args.get("line")
    query = "SELECT * FROM matchWiWip WHERE wipId=? AND line=? ORDER BY sequence"
    list = (int(wipId),line)
    table = executeReadQuery(connection, query, list)
    col = [row[0] for row in table]
    step = col.index(int(id)) + 1
    if (step == 1):
        return '', 204
    else:
        idUp = col[step-2]
        update = "UPDATE matchWiWip SET sequence=? WHERE id=?"          
        list1 = (step, idUp)
        list2 = (step-1, id)
        executeQuery(connection, update, list1)
        executeQuery(connection, update, list2)
        return redirect(url_for('wipEdit', wipId = wipId, line = line))

@app.route("/moveWiDn")
def moveWiDn():
    id = request.args.get("id")
    wipId = request.args.get("wipId")
    line = request.args.get("line")
    query = "SELECT * FROM matchWiWip WHERE wipId=? AND line=? ORDER BY sequence"
    table = executeReadQuery(connection, query, (wipId,line))
    col = [row[0] for row in table]
    step = col.index(int(id)) + 1
    if (int(id) == col[-1]):
        return '', 204
    else:
        idDn = col[step]
        update = "UPDATE matchWiWip SET sequence=? WHERE id=? "          
        list1 = (step, idDn)
        list2 = (step+1, id)
        executeQuery(connection, update, list1)
        executeQuery(connection, update, list2)
        return redirect(url_for('wipEdit', wipId = wipId, line = line))

@app.route("/printWip")
def printWip():
    values = request.args.get("values")
    return render_template("printWip.html", **values)