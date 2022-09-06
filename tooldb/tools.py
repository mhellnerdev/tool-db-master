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
    VALUES (%s,%s,%s)
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
    SET description = %s, location = %s, obsolete = %s, inventory = %s, issue = %s
    WHERE id = %s
    """)
    executeQuery(connection, query, list)
    return jsonify({'success' : number})

#from toolEdit: deletes the tool entry
@app.route("/deleteTool")
def deleteTool():
    toolId = request.args.get("toolId")
    id=int(toolId)
    print(f'id:{id}')
    print(type(id))
    toolQuery = "DELETE FROM tools WHERE id = %s"
    executeQuery(connection, toolQuery, (id,))
    return redirect(url_for('tools'))

#returns tool edit page
@app.route("/toolEdit")
def toolEdit():
    tool = request.args.get("toolNum")
    queryTool = ("""
    SELECT * FROM tools 
    WHERE tools.number = %s 
    """)
    queryNotes = ("""
    SELECT * FROM toolNotes
    WHERE toolId = %s
    """)
    toolTable = executeReadQuery(connection, queryTool, (tool,))
    toolId = toolTable[0][0]
    print(toolId)
    notesTable = executeReadQuery(connection, queryNotes, (toolId,))
    return render_template("toolEdit.html", toolTable = toolTable, notesTable = notesTable)

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
    values (%s,%s,%s,%s)
    """)
    executeQuery(connection, query, vals)
    return redirect(url_for('toolEdit', toolNum=num))

@app.route("/deleteToolNote")
def deleteToolNote():
    id = request.args.get('noteId')
    num = request.args.get('toolNum')
    query = " DELETE FROM toolNotes WHERE id = %s"
    executeQuery(connection, query, (id,))
    return redirect(url_for('toolEdit', toolNum = num))