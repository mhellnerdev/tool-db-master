from flask import render_template, request, redirect, url_for, jsonify
from tooldb.main import executeQuery, executeReadQuery, executeReadQueryAll, connection
from tooldb import app
from datetime import datetime
import re
import glob
import subprocess


#return main tools page
@app.route("/tools")
def tools():
    query = "SELECT * FROM tools"
    toolTable = executeReadQueryAll(connection, query)
    invalid = request.args.get("invalid")
    if(invalid):
        invalid = int(invalid)
    return render_template("tools.html", toolTable=toolTable, invalid = invalid)

#submit new tool info to database, return "edit tool" page to add additional information to the tool
@app.route("/addToolSubmit")
def addToolSubmit():
    tool = request.args.get("toolNum")
    description = request.args.get("toolDesc")
    location = request.args.get("toolLoc")
    list = (tool, description, location)
    query = "SELECT number FROM tools"
    toolList = executeReadQueryAll(connection, query)
    toolNums = [i[0] for i in toolList]
    insert = ("""
    INSERT INTO tools (number, description, location)
    VALUES (?,?,?)
    """)
    if(tool in toolNums):
        return redirect(url_for('tools', invalid = 1))
    else:
        executeQuery(connection, insert, list)
        return redirect(url_for('toolEdit', toolNum=tool))

#submit information added or edited on the "edit tool" page to the database, return the same "edit tool page" 
@app.route("/updateTool")
def updateTool():
    id = request.args.get("id")
    number = request.args.get("number")
    description = request.args.get("description")
    location = request.args.get("location")
    obsolete = request.args.get("obsolete",type=int)
    inventory = request.args.get("inventory",type=int)
    issue = request.args.get("issue",type=int)

    list = (description, location, obsolete, inventory, issue, id)
    query = ("""
    UPDATE tools
    SET description = ?, location = ?, obsolete = ?, inventory = ?, issue = ?
    WHERE id = ?
    """)
    executeQuery(connection, query, list)
    return jsonify({'success' : number})

#from toolEdit: deletes the tool entry and any tool/wi match entries
@app.route("/deleteTool")
def deleteTool():
    toolId = request.args.get("toolId")
    id=int(toolId)
    print(f'id:{id}')
    print(type(id))
    toolQuery = "DELETE FROM tools WHERE id = ?"
    matchQuery = "DELETE FROM matchToolsWi WHERE toolId = ?"
    executeQuery(connection, toolQuery, (id,))
    executeQuery(connection, matchQuery, (id,))
    return redirect(url_for('tools'))

#from toolEdit: associates a work instruction to the present tool
@app.route("/addWiToTool")
def addWiToTool():
    wiId = request.args.get("wiId")
    toolId = request.args.get("toolId")
    toolNum = request.args.get("toolNum")
    list = (wiId, toolId)
    query = ("""
    INSERT INTO matchToolsWi (wiId, toolId)
    VALUES (?,?)
    """)
    executeQuery(connection, query, list)
    return redirect(url_for('toolEdit', toolNum=toolNum))

#from toolEdit: removes an existing tool/wi association
@app.route("/deleteWiFromTool")
def deleteWiFromTool():
    wiId = request.args.get("wiId")
    toolId = request.args.get("toolId")
    toolNum = request.args.get("toolNum")
    query = ("""
    DELETE FROM matchToolsWi
    WHERE toolId = ? AND wiId = ? 
    """)
    logQuery = ("""
    INSERT INTO matchToolsWiLog (toolId, wiId)
    VALUES (?,?)
    """)
    executeQuery(connection, query, (toolId, wiId))
    executeQuery(connection, logQuery, (toolId, wiId))
    return redirect(url_for('toolEdit', toolNum=toolNum))

#returns tool edit page
@app.route("/toolEdit")
def toolEdit():
    tool = request.args.get("toolNum")
    queryTool = ("""
    SELECT * FROM tools 
    WHERE tools.number = ? 
    """)
    # queryWi = (""" 
    # SELECT DISTINCT wi.*
    # FROM ((matchToolsWi
    # INNER JOIN tools ON tools.id = matchToolsWi.toolId)
    # INNER JOIN wi ON wi.id = matchToolsWi.wiId)
    # where tools.number = ? """)
    # queryWiAll = (""" 
    # SELECT DISTINCT wi.*
    # FROM ((matchToolsWi
    # INNER JOIN tools ON tools.id = matchToolsWi.toolId)
    # INNER JOIN wi ON wi.id = matchToolsWi.wiId)
    # where tools.number != ? """)
    queryNotes = ("""
    SELECT * FROM toolNotes
    WHERE toolId = ?
    """)
    queryLog = ("""
    SELECT wi.*
    FROM ((matchToolsWiLog 
    INNER JOIN tools ON tools.id = matchToolsWiLog.toolId)
    INNER JOIN wi ON wi.id = matchToolsWiLog.wiId)
    WHERE toolId = ?    
    """)

    toolTable = executeReadQuery(connection, queryTool, (tool,))
    toolId = toolTable[0][0]
    print(toolId)
    # wiTable = executeReadQuery(connection, queryWi, (tool,))
    # wiAllTable = executeReadQuery(connection, queryWiAll, (tool,))
    notesTable = executeReadQuery(connection, queryNotes, (toolId,))
    logTable = executeReadQuery(connection, queryLog, (toolId,))
    return render_template("toolEdit.html", toolTable = toolTable, notesTable = notesTable, logTable = logTable)

#opens a PDF from a given tool number
@app.route("/openToolPdf")
def openToolPdf():
    toolNum = request.args.get("toolNum")

    directory = re.match(r"(^\d{3}-\d{2}-\d{3}).*",toolNum).group(1)
    list = glob.glob(f"M:\\399-TOOLS-EQUIP\\{directory}*\\*pdf*\\{toolNum}*.pdf")
    if not list:
        list = glob.glob(f"M:\\399-TOOLS-EQUIP\\{directory}*\\{toolNum}*.pdf")
        if not list:
            return '', 204
        else:
            file = list[0]
            subprocess.Popen([file],shell=True)
            return '', 204
    else:
        file = list[0]
        subprocess.Popen([file],shell=True)
        return '', 204

@app.route("/addToolNote")
def addToolNote():
    num = request.args.get('toolNumNote')
    id = request.args.get('toolIdNote')
    note = request.args.get('note')
    name = request.args.get('name')
    dt = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
    vals = (id, note, name, dt)
    query = ("""
    INSERT INTO toolNotes (toolId,note,name,date)
    values (?,?,?,?)
    """)
    executeQuery(connection, query, vals)
    return redirect(url_for('toolEdit', toolNum=num))

@app.route("/deleteToolNote")
def deleteToolNote():
    id = request.args.get('noteId')
    num = request.args.get('toolNum')
    query = " DELETE FROM toolNotes WHERE id = ?"
    executeQuery(connection, query, (id,))
    return redirect(url_for('toolEdit', toolNum = num))