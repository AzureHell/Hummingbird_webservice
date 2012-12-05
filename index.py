#!/usr/local/bin/python
# -*- coding: utf-8 -*-
## Created on 2011-10-01
from bottle import route, run, get, post, request, response
import dbHelper
import json
import logging

#HTTP_CODES['Request Timeout'] = 100000
#HTTP_CODES['Gateway Timeout'] = 100000


@route('/')
@route('/hello')
def hello():
    return dbHelper.getInfo()

def get_post_json():
    try:
        return json.load(request.body)
    except ValueError:
        abort(400, 'Bad request: Could not decode request body(expected JSON).')

@post('/checkuser')
def checkUser():
    content = request.json
    print(content)
    try:
        #1 rows only
        if content['status'] == 'succeed':
            username = content['data'][0]['user_id']
            password = content['data'][0]['password']
    except ValueError:
        abort(400, 'Bad request: Could not decode request body(expected JSON).')
    #print(username)
    #print(password)
    result = dbHelper.checkUser(username, password)
    print(result)
    if result[0:6] == "error:":
        str = fmtContent("", 'failed', result[result.find(':')+1:])
    else:
        str = fmtContent(result)
    print(str)
    return str

@post('/downloadCheckPlan')
def downloadCheckPlan():
    content = request.json
    print(content)
    try:
        #1 rows only
        if content['status'] == 'succeed':
            sQCUserID = content['data'][0]['sQCUserID']
            iID = content['data'][0]['iID']
    except ValueError:
        abort(400, 'Bad request: Could not decode request body(expected JSON).')
    result = dbHelper.downloadCheckPlan(sQCUserID, iID)
    #print(result)
    if result[0:6] == "error:":
        str = fmtContent("", 'failed', result[result.find(':')+1:])
    else:
        str = fmtContent(result)
    print(str)
    #response.content_type = 'text/html; charset=utf8'
    return str

@post('/uploadCheckRecord')
def uploadCheckRecord():
    content = request.json
    print(content)
    try:
        if content['status'] == 'succeed':
            masterDict = content['data'][0]['records']
            #这里需要判断是否存在[1]的数据
            detailCount = int(content['data'][1]['count'])
            detailDict = content['data'][1]['records']
    except ValueError:
        abort(400, 'Bad request: Could not decode request body(expected JSON).')
    result = dbHelper.uploadCheckRecord(masterDict, detailCount, detailDict)
    #print(result)
    if result[0:6] == "error:":
        str = fmtContent("", 'failed', result[result.find(':')+1:])
    else:
        str = fmtContent(result)
    print(str)
    return str

@post('/uploadCheckRecordPic')
def uploadCheckRecordPic():
    #name = request.froms.name
 
    data = request.files.data
    if data is not None:
        print('ok')
        raw = data.file.read() # This is dangerous for big files
        filename = data.filename

    print('filename: ' + filename)
    filesize = len(raw)
    print(filesize)
    #print(type(raw))
    result = dbHelper.uploadCheckRecordPic(filename, raw)
    print(result)
    if result[0:6] == "error:":
        str = fmtContent("", 'failed', result[result.find(':')+1:])
    else:
        str = fmtContent(result)
    print(str)
    return str

@route('/showpic')
def showpic():
    response.set_header("Content-type", "image/PNG")
    return dbHelper.showPic()

def fmtContent(data, status='succeed', error=''):
    return '{"status":"'+status+'","error":"'+error+'","data":['+data+']}'

run(host="192.168.100.201", port=8080, debug=True)
