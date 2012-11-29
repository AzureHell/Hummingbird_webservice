#!/usr/local/bin/python
# -*- coding: utf-8 -*-
# Created on 2011-10-01
import pyodbc
import json
import time

def getConn():
    return pyodbc.connect('DRIVER={SQL Server};Server=.;DATABASE=qchelper;UID=qchelper;PWD=1qaz2wsx')

def sqlQuery(conn, sql):
    cursor = conn.cursor()
    cursor.execute(sql)
    x = cursor.fetchall()
    #cursor.close()
    conn.close()
    return x
def sqlExcute(conn, sql):
    cursor = conn.cursor()
    cursor.execute(sql)
    conn.commit()
    #cursor.close()
    conn.close()
    return 1


def getInfo():
    recSet = sqlQuery(getConn(), "select top 1 user_name, password from dbo.users")

    print("中文".encode('utf8'))
    
    for recOne in recSet:
        return recOne[0] + " : " + recOne[1] + ',defaultencoding:' + sys.getdefaultencoding()

def checkUser(username, password):
    recSet = sqlQuery(getConn(), "select top 1 user_id,user_name from dbo.users where user_name = '%s' and password = '%s'"%(username, password))    
    if recSet.count > 0:
        #1 rows only
        for recOne in recSet:
            return '{"user_id":"'+str(recOne.user_id)+'","user_name":"'+recOne.user_name+'"}'
    else:
        return 'error:not return count!'

def downloadCheckPlan(sQCUserID, iID):
    jsonresult = ''
    record_count = 0
    sql = "select iID, iFactoryID, sOrderNo, sStyleNo, sProductID, dRequestCheck, sCheckItemDesc, sQCUserID, sUserID from qmCheckPlan where sQCUserID = '%s' and iID > %s and bApproved = 1"%(sQCUserID, iID)
    recSet = sqlQuery(getConn(), sql)
    for recOne in recSet:
        stra = '{"iID":"'+str(recOne.iID)+'","iFactoryID":"'+str(recOne.iFactoryID)+'","sOrderNo":"'+recOne.sOrderNo+'","sStyleNo":"'+recOne.sStyleNo+'","sProductID":"' \
            +recOne.sProductID+'","dRequestCheck":"'+str(recOne.dRequestCheck)+'","sCheckItemDesc":"'+recOne.sCheckItemDesc.decode( "GB2312")+'","sQCUserID":"'+str(recOne.sQCUserID)+'","sUserID":"'+str(recOne.sUserID)+'","bApproved":"'+str(recOne.bApproved)+'"}'
        if jsonresult <> '':
            jsonresult += ',' + stra
        else:
            jsonresult = stra
        record_count += 1
    jsonresult = '{"table":"qmCheckPlan","count":"'+str(record_count)+'","records":['+jsonresult+']}'
    return jsonresult

def fieldisNull(x):
    if x == 'null':
        return x
    else:
        return "'" + x + "'"

def uploadCheckRecord(masterDict, detailCount, detailDict):
    sql = "declare @MstID table (iMstID int);\n"
    sql += "insert into [dbo].[qmCheckRecordMst](iFactoryID, sOrderNo, sStyleNo, sProductID "
    sql += ", iItemID, dChecdedDate, sRemark, datetime_rec, datetime_delete, datetime_upload, id_upload, user_id_opt "
    sql += ") output inserted.iID into @MstID \n"
    sql += "select " + fieldisNull(masterDict[0]['iFactoryID'])
    sql += "," + fieldisNull(masterDict[0]['sOrderNo'])
    sql += "," + fieldisNull(masterDict[0]['sStyleNo'])
    sql += "," + fieldisNull(masterDict[0]['sProductID'])
    sql += "," + fieldisNull(masterDict[0]['iItemID'])
    sql += "," + fieldisNull(masterDict[0]['dChecdedDate'])
    sql += "," + fieldisNull(masterDict[0]['sRemark'])
    sql += "," + fieldisNull(masterDict[0]['datetime_rec'])
    sql += "," + fieldisNull(masterDict[0]['datetime_delete'])
    sql += ",'" + time.strftime("%Y-%m-%d %H:%M:%S", time.localtime())
    sql += "'," + fieldisNull(masterDict[0]['iID'])
    sql += "," + fieldisNull(masterDict[0]['user_id_opt'])
    sql += ";\n"
    
    for i in range(0, detailCount):
        sql += "insert into [dbo].[qmCheckRecordDtl](iID, iMstID, sFileName, dCreateDate, datetime_delete) \n "
        sql += "select " + fieldisNull(detailDict[i]['iID'])
        sql += ", (select top 1 iMstID from @MstID) as iMstID "
        sql += "," + fieldisNull(detailDict[i]['sFileName'])
        sql += "," + fieldisNull(detailDict[i]['dCreaimestamp'])
        sql += "," + fieldisNull(detailDict[i]['datetime_delete'])
        sql += ";\n"
        
    print(sql)
    sqlExcute(getConn(), sql)

    sql = "select top 1 id_upload, user_id_opt, datetime_upload from dbo.qmCheckRecordMst with(nolock) \n"
    sql += " where user_id_opt = " + masterDict[0]["user_id_opt"]
    sql += " and id_upload = " + masterDict[0]["iID"]
    sql += " order by datetime_upload desc;\n"
    print(sql)
    recSet = sqlQuery(getConn(), sql)
    for recOne in recSet:
        result = '{"iID":"' + str(recOne.id_upload) + '", "user_id_opt":"' + str(recOne.user_id_opt) + '", "datetime_upload":"' + str(recOne.datetime_upload) + '"}'
        result = '{"table":"qmCheckRecordMst","count":"1","records":['+result+']}'
    return result

def uploadCheckRecordPic(fileName, raw):
    con = getConn()
    cur = con.cursor()

    sql = "update [dbo].[qmCheckRecordDtl] set bPhoto = ?, sFileName = sFileName + '.finished' where sFileName = ?"
    cur.execute(sql, (pyodbc.Binary(raw),fileName))
    con.commit()
    con.close()

    return "{}"

def showPic():
    con = getConn()
    cur = con.cursor()

    sql = "select top 1 bPhoto from dbo.qmCheckRecordDtl with(nolock)"
    cur.execute(sql)
    x = cur.fetchall()
    for r in x:
        return r.bPhoto
    con.close()

if __name__ == "__main__":
    print(getInfo())
