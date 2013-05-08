#!/usr/bin/python
# -*- coding: utf-8 -*-

from bottle import route, run, post, request, response, abort
import dbHelper
import json


@route('/')
@route('/hello')
def hello():
    return dbHelper.getInfo()


def get_post_json():
    try:
        return json.load(request.body)
    except ValueError:
        abort(400, 'Bad request: Could not decode request body(expected JSON).')


@route('/login')
def login():
    username = request.forms.get('username')
    password = request.forms.get('password')
    if dbHelper.check_user_cret(username, password):
        response.set_cookie('acount', username, "", path="")
        return "you're welcome!"
    else:
        return "login's failed!"


@route('/restricted')
def restricted_are():
    # get client ip address
    # remoteip = request.environ.get('REMOTE_ADDR')
    username = request.get_cookie("account", secret='', path="")
    if username:
        return "Welcome agent!"


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
        str = fmtContent("", 'failed', result[result.find(':') + 1:])
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
        str = fmtContent("", 'failed', result[result.find(':') + 1:])
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
            if len(content['data']) > 0:
                masterDict = content['data'][0]['records']
            #这里需要判断是否存在[1]的数据
            if len(content['data']) > 1:
                detailCount = int(content['data'][1]['count'])
                detailDict = content['data'][1]['records']
            else:
                detailCount = 0
                detailDict = {}
    except ValueError:
        abort(400, 'Bad request: Could not decode request body(expected JSON).')
    result = dbHelper.uploadCheckRecord(masterDict, detailCount, detailDict)
    #print(result)
    if result[0:6] == "error:":
        str = fmtContent("", 'failed', result[result.find(':') + 1:])
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
        # This is dangerous for big files
        raw = data.file.read()
        key = data.filename

    print('key: ' + key)
    filesize = len(raw)
    print(filesize)
    #print(type(raw))
    result = dbHelper.uploadCheckRecordPic(key, raw)
    print(result)
    if result[0:6] == "error:":
        str = fmtContent("", 'failed', result[result.find(':') + 1:])
    else:
        str = fmtContent(result)
    print(str)
    return str


@route('/showpic')
def showpic():
    response.set_header("Content-type", "image/PNG")
    return dbHelper.showPic()


def fmtContent(data, status='succeed', error=''):
    return '{"status":"' + status + '","error":"' + error \
        + '","data":[' + data + ']}'


if __name__ == "__main__":
    run(host="192.168.100.200", port=8080, debug=True, reloader=True)
