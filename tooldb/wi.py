from flask import render_template, request, redirect, url_for
from tooldb.main import executeQuery, executeReadQuery, executeReadQueryAll, connection
from tooldb import app
import re
import glob
import subprocess



#return main work instructions page
@app.route("/wi")
def wi():
    query = "SELECT * FROM wi"
    wiTable = executeReadQueryAll(connection, query)
    invalid = request.args.get("invalid")
    if(invalid):
        invalid = int(invalid)
    return render_template("wi.html", wiTable=wiTable, invalid = invalid)


#submit new work instruction information to the database, return "edit wi" page to add additional information to the wi
@app.route("/addWiSubmit")
def addWiSubmit():
    wi = request.args.get("wiNum")
    description = request.args.get("wiDesc")
    location = request.args.get("wiLoc")
    list = (wi, description, location)
    query = "SELECT number FROM wi" 
    wiList = executeReadQueryAll(connection, query)
    wiNums = [i[0] for i in wiList]
    insert = ("""
    INSERT INTO wi (number, description, workstation)
    VALUES (?,?,?)
    """)
    if(wi in wiNums):
        return redirect(url_for('wi', invalid = 1))
    else:
        executeQuery(connection, insert, list)
        return redirect(url_for('wiEdit', wiNum=wi))

#submit information added or edited on the "edit wi" page to the database, return the same "edit wi page" 
@app.route("/updateWi")
def updateWi():
    id = request.args.get("wiId")
    number = request.args.get("wiNum")
    description = request.args.get("wiDesc")
    location = request.args.get("wiLoc")
    list = (description, location, id)
    query = ("""
    UPDATE wi
    SET description = ?, workstation = ?
    WHERE id = ?
    """)
    executeQuery(connection, query, list)
    return redirect(url_for('wiEdit', wiNum=number))

#from wiEdit: deletes the work instruction entry and any tool/wi match entries
@app.route("/deleteWi")
def deleteWi():
    wiId = request.args.get("wiId")
    id=int(wiId)
    print(f'id:{id}')
    print(type(id))
    wiQuery = "DELETE FROM wi WHERE id = ?"
    matchQuery = "DELETE FROM matchToolsWi WHERE wiId = ?"
    executeQuery(connection, wiQuery, (id,))
    executeQuery(connection, matchQuery, (id,))
    return redirect(url_for('wi'))

#from wiEdit: associates a tool to the present work instruction
@app.route("/addToolToWi")
def addToolToWi():
    toolId = request.args.get("toolId")
    wiId = request.args.get("wiId")
    wiNum = request.args.get("wiNum")
    list = (wiId, toolId)
    query = ("""
    INSERT INTO matchToolsWi (wiId, toolId)
    VALUES (?,?)
    """)
    executeQuery(connection, query, list)
    return redirect(url_for('wiEdit', wiNum=wiNum))

#from wiEdit: removes an existing tool/wi association
@app.route("/deleteToolFromWi")
def deleteToolFromWi():
    toolId = request.args.get("toolId")
    wiId = request.args.get("wiId")
    wiNum = request.args.get("wiNum")
    query = ("""
    DELETE FROM matchToolsWi
    WHERE wiId = ? AND toolId = ? 
    """)
    executeQuery(connection, query, (wiId, toolId))
    return redirect(url_for('wiEdit', wiNum=wiNum))

#retrns work instruction edit page
@app.route("/wiEdit")
def wiEdit():
    wi = request.args.get("wiNum")
    queryWi = ("""
    SELECT * FROM wi 
    WHERE wi.number = ? """)
    queryTool = (""" 
    SELECT tools.*
    FROM ((matchToolsWi
    INNER JOIN tools ON tools.id = matchToolsWi.toolId)
    INNER JOIN wi ON wi.id = matchToolsWi.wiId)
    where wi.number = ? """)
    queryToolAll = (""" 
    SELECT DISTINCT tools.*
    FROM ((matchToolsWi
    INNER JOIN tools ON tools.id = matchToolsWi.toolId)
    INNER JOIN wi ON wi.id = matchToolsWi.wiId)
    where wi.number != ? """)

    wiTable = executeReadQuery(connection, queryWi, (wi,))
    toolTable = executeReadQuery(connection, queryTool, (wi,))
    toolAllTable = executeReadQuery(connection, queryToolAll, (wi,))

    return render_template("wiEdit.html",  wiTable = wiTable, toolTable = toolTable, toolAllTable = toolAllTable)

#opens a PDF from a given wi number
@app.route("/openWiPdf")
def openWiPdf():
    wiNum = request.args.get("wiNum")

    directory = re.match(r"(^\d{3}-\d{2}-\d{3}).*",wiNum).group(1)
    list = glob.glob(f"M:\\399-TOOLS-EQUIP\\{directory}*\\*pdf*\\{wiNum}*.pdf")
    if not list:
        print('not list 1')
        list = glob.glob(f"M:\\399-TOOLS-EQUIP\\{directory}*\\{wiNum}*.pdf")
        if not list:
            print('not list 2')
            return '', 204
        else:
            file = list[0]
            print(file)
            subprocess.Popen([file],shell=True)
            return '', 204
    else:
        file = list[0]
        print(file)
        subprocess.Popen([file],shell=True)
        return '', 204