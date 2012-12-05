#!/usr/local/bin/python
# -*- coding: utf-8 -*-
# Created on 2011-10-01
import sys, time, json
import re
import pyodbc

# 数据交互

def get_db_type():
    return "mssql"
    #return "sqlite3"

def changeSqlForDb(sql, **matchs):
    # 替换当前选择的数据库位置的内容
    sql = sql.replace("#"+get_db_type()+"#", matchs[get_db_type()])
    # 替换其他数据库位置的内容为空白
    db_type_re = re.compile("#[a-z]+[0-9]+#")
    sql = db_type_re.sub("", sql)
    # 返回
    return sql

def getConn():
    if get_db_type() == "mssql":
        #return pyodbc.connect('DSN=qchelper;UID=sa;PWD=123;')
        #return pyodbc.connect('DRIVER={mssql};Server=192.168.56.101,1433;DATABASE=qchelper;UID=sa;PWD=123;TDS_Version=8.0')
        return pyodbc.connect('DRIVER={SQL Server};Server=.;DATABASE=qchelper;UID=qchelper;PWD=1qaz2wsx;')
    elif get_db_type() == "sqlite3":
        return pyodbc.connect('DSN=qchelper;')

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
    rec_set = sqlQuery(getConn(), changeSqlForDb("select #mssql# sUserID, sUserName, sPasswordMD5 from smUser #sqlite3#", mssql="top 1", sqlite3="limit 1"))
    
    for rec_one in rec_set:
        return rec_one[0] + " : " + rec_one[1] + ',defaultencoding:' + sys.getdefaultencoding()

def checkUser(username, password):
    sql = changeSqlForDb("select #mssql# sUserID, sUserName, sPasswordMD5 from smUser where sUserID = '%s' #sqlite3#"%(username), mssql="top 1", sqlite3="limit 1")
    rec_set = sqlQuery(getConn(), sql)
    for rec_one in rec_set:
        if rec_one.sPasswordMD5 == None:
            return 'error:password is null!'
        return '{"user_id":"'+str(rec_one.sUserID)+'","user_name":"'+rec_one.sUserName+'"}'
    return 'error:not record!'

def downloadCheckPlan(sQCUserID, iID):
    jsonresult = ''
    record_count = 0
    sql = "select iID, iFactoryID, sOrderNo, sStyleNo, sProductID, dRequestCheck, sCheckItemDesc, sQCUserID, sUserID, bApproved from qmCheckPlan where sQCUserID = '%s' and iID > %s and bApproved = 1"%(sQCUserID, iID)
    rec_set = sqlQuery(getConn(), sql)
    for rec_one in rec_set:
        stra = '{"iID":"'+str(rec_one.iID)+'","iFactoryID":"'+str(rec_one.iFactoryID)+'","sOrderNo":"'+rec_one.sOrderNo+'","sStyleNo":"'+rec_one.sStyleNo+'","sProductID":"' \
            +rec_one.sProductID+'","dRequestCheck":"'+str(rec_one.dRequestCheck)+'","sCheckItemDesc":"'+rec_one.sCheckItemDesc+'","sQCUserID":"'+str(rec_one.sQCUserID)+'","sUserID":"'+str(rec_one.sUserID)+'","bApproved":"'+str(rec_one.bApproved)+'"}'
            #+rec_one.sProductID+'","dRequestCheck":"'+str(rec_one.dRequestCheck)+'","sCheckItemDesc":"'+rec_one.sCheckItemDesc.decode( "GB2312")+'","sQCUserID":"'+str(rec_one.sQCUserID)+'","sUserID":"'+str(rec_one.sUserID)+'","bApproved":"'+str(rec_one.bApproved)+'"}'
        if jsonresult <> '':
            jsonresult += ',' + stra
        else:
            jsonresult = stra
        record_count += 1
    if jsonresult <> "":
        jsonresult = '{"table":"qmCheckPlan","count":"'+str(record_count)+'","records":['+jsonresult+']}'
    else:
        jsonresult = "error:no record!"
    return jsonresult

def fieldisNull(x):
    if x == "null":
        return x
    else:
        return "'" + x + "'"

def uploadCheckRecord(masterDict, detailCount, detailDict):
    sql = ""
    sql += "insert into qmCheckRecordMst(iFactoryID, sOrderNo, sStyleNo, sProductID "
    sql += ", iItemID, dChecdedDate, sRemark, datetime_rec, datetime_delete, datetime_upload, id_upload, user_id_by_upload "
    sql += ") "
    sql += "select " + fieldisNull(masterDict[0]['iFactoryID'])
    sql += "," + fieldisNull(masterDict[0]['sOrderNo'])
    sql += "," + fieldisNull(masterDict[0]['sStyleNo'])
    sql += "," + fieldisNull(masterDict[0]['sProductID'])
    sql += "," + fieldisNull(masterDict[0]['iItemID'])
    sql += "," + fieldisNull(masterDict[0]['dChecdedDate'])
    sql += "," + fieldisNull(masterDict[0]['sRemark'])
    sql += "," + fieldisNull(masterDict[0]['datetime_rec'])
    sql += "," + fieldisNull(masterDict[0]['datetime_delete'])
    sql += "," + fieldisNull(time.strftime("%Y-%m-%d %H:%M:%S", time.localtime()))
    sql += "," + fieldisNull(masterDict[0]['iID'])
    sql += "," + fieldisNull(masterDict[0]['user_id_by_upload'])
    sql += ";"

    for i in range(0, detailCount):
        sql += "insert into qmCheckRecordDtl(iID, iMstID, sFileName, dCreateDate, datetime_delete)"
        sql += "select " + fieldisNull(detailDict[i]['iID'])
        sql += ", (select max(iId) from qmCheckRecordMst "
        sql += " where id_upload = "+fieldisNull(masterDict[0]['iID'])
        sql += " and user_id_by_upload = "+fieldisNull(masterDict[0]['user_id_by_upload'])
        sql += " ) as iMstID "
        sql += "," + fieldisNull(detailDict[i]['sFileName'])
        sql += "," + fieldisNull(detailDict[i]['dCreaimestamp'])
        sql += "," + fieldisNull(detailDict[i]['datetime_delete'])
        sql += ";"

    print(sql)
    sqlExcute(getConn(), sql)

    sql = "select #mssql# id_upload, user_id_by_upload, datetime_upload from qmCheckRecordMst "
    sql += " where user_id_by_upload = '" + masterDict[0]["user_id_by_upload"]
    sql += "' and id_upload = '" + masterDict[0]["iID"]
    sql += "' order by datetime_upload desc #sqlite3# ;"
    sql = changeSqlForDb(sql, mssql = "top 1", sqlite3 = "limit 1")
    print(sql)
    rec_set = sqlQuery(getConn(), sql)
    for rec_one in rec_set:
        result = '{"iID":"' + str(rec_one.id_upload) + '", "user_id_by_upload":"' + str(rec_one.user_id_by_upload) + '", "datetime_upload":"' + str(rec_one.datetime_upload) + '"}'
        result = '{"table":"qmCheckRecordMst","count":"1","records":['+result+']}'
    return result

def uploadCheckRecordPic(fileName, raw):
    con = getConn()
    cur = con.cursor()

    sql = "update qmCheckRecordDtl set bPhoto = ?, sFileName = sFileName + '.finished' where sFileName = ?"
    cur.execute(sql, (pyodbc.Binary(raw),fileName))
    con.commit()
    con.close()

    return "{}"

def showPic():
    con = getConn()
    cur = con.cursor()

    sql = "select #mssql# bPhoto from qmCheckRecordDtl #sqlite3#"
    sql = changeSqlForDb(sql, mssql = "top 1", sqlite3 = "limit 1")
    cur.execute(sql)
    x = cur.fetchall()
    for r in x:
        return r.bPhoto
    con.close()

if __name__ == "__main__":
    print(getInfo())
