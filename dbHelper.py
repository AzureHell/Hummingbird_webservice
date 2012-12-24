#!/usr/bin/python
# -*- coding: utf-8 -*-

import sys, time
import re
import pyodbc
import chardet
import locale

locale.setlocale(locale.LC_ALL,"en_US.UTF-8")
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
        return pyodbc.connect('DRIVER={mssql};Server=192.168.56.101,1433;DATABASE=qchelper;UID=sa;PWD=123;TDS_Version=8.0;CHARSET=UTF8;')
        #return pyodbc.connect('DRIVER={SQL Server};Server=.;DATABASE=qchelper;UID=qchelper;PWD=1qaz2wsx;')
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
    rows = sqlQuery(getConn(), changeSqlForDb("select #mssql# sUserID, sUserName, sPasswordMD5 from smUser #sqlite3#", mssql="top 1", sqlite3="limit 1"))
    
    for row in rows:
        return row[0] + " : " + row[1] + ',defaultencoding:' + sys.getdefaultencoding()

def check_user_cret(username, password):
    sql = changeSqlForDb("select #mssql# sUserID, sUserName, sPasswordMD5 from smUser where sUserID = '%s' #sqlite3#"%(username), mssql="top 1", sqlite3="limit 1")
    rows = sqlQuery(getConn(), sql)
    #1 row only
    for row in rows:
        if row.sPasswordMD5 == password:
            return True
    return False

def checkUser(username, password):
    sql = changeSqlForDb("select #mssql# sUserID, sUserName, sPasswordMD5 from smUser where sUserID = '%s' #sqlite3#"%(username), mssql="top 1", sqlite3="limit 1")
    rows = sqlQuery(getConn(), sql)
    for row in rows:
        if row.sPasswordMD5 == None:
            return 'error:password is null!'
        elif row.sPasswordMD5 == password:
            return '{"user_id":"'+str(row.sUserID)+'","user_name":"'+row.sUserName+'"}'
    return 'error:not record!'

def downloadCheckPlan(sQCUserID, iID):
    jsonresult = ''
    record_count = 0
    sql = "select iID, iFactoryID, sOrderNo, sStyleNo, sProductID, dRequestCheck, sCheckItemDesc, sQCUserID, sUserID, bApproved from qmCheckPlan where sQCUserID = '%s' and iID > %s and bApproved = 1"%(sQCUserID, iID)
    rows = sqlQuery(getConn(), sql)
    for row in rows:
        #临时用这种方法处理下
        if row.sCheckItemDesc != None:
            sCheckItemDesc = row.sCheckItemDesc[:row.sCheckItemDesc.find(u'\x00')]
        else:
            sCheckItemDesc = ""
        stra = '{"iID":"'+str(row.iID)+'","iFactoryID":"'+str(row.iFactoryID)+'","sOrderNo":"'+row.sOrderNo+'","sStyleNo":"'+row.sStyleNo+'","sProductID":"' \
            + row.sProductID+'","dRequestCheck":"'+str(row.dRequestCheck)+'","sCheckItemDesc":"'+sCheckItemDesc+'","sQCUserID":"' \
            + str(row.sQCUserID)+'","sUserID":"'+str(row.sUserID)+'","bApproved":"'+str(row.bApproved)+'"}'
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
    # sql = ""
    # sql += "merge qmCheckRecordMst as t "
    # sql += "using (select " + fieldisNull(masterDict[0]['iFactoryID'])
    # sql += " iFactoryID," + fieldisNull(masterDict[0]['sOrderNo'])
    # sql += " sOrderNo," + fieldisNull(masterDict[0]['sStyleNo'])
    # sql += " sStyleNo," + fieldisNull(masterDict[0]['sProductID'])
    # sql += " sProductID," + fieldisNull(masterDict[0]['iItemID'])
    # sql += " iItemID," + fieldisNull(masterDict[0]['dCheckedDate'])
    # sql += " dCheckedDate," + fieldisNull(masterDict[0]['sRemark'])
    # sql += " sRemark," + fieldisNull(masterDict[0]['sUserID'])
    # sql += " sUserID," + fieldisNull(masterDict[0]['datetime_rec'])
    # sql += " datetime_rec," + fieldisNull(masterDict[0]['datetime_modify'])
    # sql += " datetime_modify," + fieldisNull(masterDict[0]['datetime_delete'])
    # sql += " datetime_delete," + fieldisNull(time.strftime("%Y-%m-%d %H:%M:%S", time.localtime()))
    # sql += " datetime_upload," + fieldisNull(masterDict[0]['uMobileKey'])
    # sql += " uMobileKey "
    # sql += " ) as s (iFactoryID,sOrderNo,sStyleNo,sProductID,iItemID,dCheckedDate,sRemark,sUserID,datetime_rec,datetime_modify,datetime_delete,datetime_upload,uMobileKey) "
    # sql += " on s.uMobileKey = t.uMobileKey "
    # sql += "when matched then "
    # sql += " update set t.dCheckedDate = s.dCheckedDate, t.sRemark = s.sRemark, t.datetime_modify = s.datetime_modify, t.datetime_delete = s.datetime_delete, t.datetime_upload = s.datetime_upload "
    # sql += "when not matched then "
    # sql += " insert (iFactoryID, sOrderNo, sStyleNo, sProductID, iItemID, dCheckedDate, sRemark, sUserID, datetime_rec, datetime_modify, datetime_delete, datetime_upload, uMobileKey) "
    # sql += " values (s.iFactoryID, s.sOrderNo, s.sStyleNo, s.sProductID, s.iItemID, s.dCheckedDate, s.sRemark, s.sUserID, s.datetime_rec, s.datetime_modify, s.datetime_delete, s.datetime_upload, s.uMobileKey) "
    # sql += ";"

    sql = "if not exists (select top 1 1 from qmCheckRecordMst where uMobileKey = " + fieldisNull(masterDict[0]['uMobileKey']) + ") "
    sql += "insert into qmCheckRecordMst(iFactoryID, sOrderNo, sStyleNo, sProductID "
    sql += ", iItemID, dCheckedDate, sRemark, sUserID, datetime_rec, datetime_modify, datetime_delete, datetime_upload, uMobileKey "
    sql += ") "
    sql += "select " + fieldisNull(masterDict[0]['iFactoryID'])
    sql += "," + fieldisNull(masterDict[0]['sOrderNo'])
    sql += "," + fieldisNull(masterDict[0]['sStyleNo'])
    sql += "," + fieldisNull(masterDict[0]['sProductID'])
    sql += "," + fieldisNull(masterDict[0]['iItemID'])
    sql += "," + fieldisNull(masterDict[0]['dCheckedDate'])
    sql += "," + fieldisNull(masterDict[0]['sRemark'])
    sql += "," + fieldisNull(masterDict[0]['sUserID'])
    sql += "," + fieldisNull(masterDict[0]['datetime_rec'])
    sql += "," + fieldisNull(masterDict[0]['datetime_modify'])
    sql += "," + fieldisNull(masterDict[0]['datetime_delete'])
    sql += "," + fieldisNull(time.strftime("%Y-%m-%d %H:%M:%S", time.localtime()))
    sql += "," + fieldisNull(masterDict[0]['uMobileKey'])
    sql += " else update qmCheckRecordMst set " 
    sql += " dCheckedDate = " + fieldisNull(masterDict[0]['dCheckedDate'])
    sql += ",sRemark = " + fieldisNull(masterDict[0]['sRemark'])
    sql += ",datetime_modify = " + fieldisNull(masterDict[0]['datetime_modify'])
    sql += ",datetime_delete = " + fieldisNull(masterDict[0]['datetime_delete'])
    sql += ",datetime_upload = " + fieldisNull(time.strftime("%Y-%m-%d %H:%M:%S", time.localtime()))
    sql += " where uMobileKey = " + fieldisNull(masterDict[0]['uMobileKey'])
    sql += ";"

    for i in range(0, detailCount):
        # sql += "merge qmCheckRecordDtl as t "
        # sql += "using (select isnull((select max(iId) from qmCheckRecordMst where uMobileKey = "+fieldisNull(masterDict[0]['uMobileKey'])
        # sql += " ), 0) as iMstID "
        # sql += " ," + fieldisNull(detailDict[i]['dCreateDate'])
        # sql += " ," + fieldisNull(detailDict[i]['datetime_modify'])
        # sql += " ," + fieldisNull(detailDict[i]['datetime_delete'])
        # sql += " ," + fieldisNull(detailDict[i]['uMobileKey'])
        # sql += " ) as s (iMstID,dCreateDate,datetime_modify,datetime_delete,uMobileKey) "
        # sql += " on s.uMobileKey = t.uMobileKey "
        # sql += "when matched then "
        # sql += " update set t.datetime_modify = s.datetime_modify, t.datetime_delete = s.datetime_delete "
        # sql += "when not matched then "
        # sql += " insert (iMstID, dCreateDate, datetime_modify, datetime_delete, uMobileKey) "
        # sql += " values (s.iMstID, s.dCreateDate, s.datetime_modify, s.datetime_delete, s.uMobileKey) "
        # sql += ";"
        sql += "if not exists (select top 1 1 from qmCheckRecordDtl where uMobileKey = " + fieldisNull(detailDict[i]['uMobileKey']) + ") "
        sql += "insert into qmCheckRecordDtl(iMstID, dCreateDate, datetime_modify, datetime_delete, uMobileKey)"
        sql += "select isnull((select max(iId) from qmCheckRecordMst where uMobileKey = "+fieldisNull(masterDict[0]['uMobileKey'])
        sql += " ), 0) as iMstID "
        sql += "," + fieldisNull(detailDict[i]['dCreateDate'])
        sql += "," + fieldisNull(detailDict[i]['datetime_modify'])
        sql += "," + fieldisNull(detailDict[i]['datetime_delete'])
        sql += "," + fieldisNull(detailDict[i]['uMobileKey'])
        sql += " else update qmCheckRecordDtl set "
        sql += " datetime_modify = " + fieldisNull(detailDict[i]['datetime_modify'])
        sql += ",datetime_delete = " + fieldisNull(detailDict[i]['datetime_delete'])
        sql += " where uMobileKey = " + fieldisNull(detailDict[i]['uMobileKey'])
        sql += ";"

    print(sql)
    sqlExcute(getConn(), sql.encode('utf-8'))

    sql = ""
    sql += "select #mssql# datetime_upload from qmCheckRecordMst "
    sql += " where uMobileKey = '" + masterDict[0]["uMobileKey"] + "' #sqlite3# ;"
    sql = changeSqlForDb(sql, mssql = "top 1", sqlite3 = "limit 1")
    print(sql)
    rows = sqlQuery(getConn(), sql.encode('utf-8'))
    #只有一条记录
    record_string = ""
    record_count = 0
    for row in rows:
        record_string += '{"uMobileKey":"' + str(masterDict[0]["uMobileKey"]) + '", "datetime_upload":"' + str(row.datetime_upload) + '"}'
        record_count += 1
    result = '{"table":"qmCheckRecordMst","count":"' + str(record_count) + '","records":['+record_string+']}'
    return result

def uploadCheckRecordPic(key, raw):
    if uploadPic("qmCheckRecordDtl", "bPhoto", "uMobileKey", key, raw):
        return "{}"
    return "{}"

'''
统一的图片上传函数，只支持插入到表中的image字段，其他字段类型会报错
'''
def uploadPic(table_name, field_name, key_name, key, raw):
    try:
        con = getConn()
        cur = con.cursor()
        sql = "update " + table_name + " set " + field_name + " = ? where " + key_name + " = ?"
        cur.execute(sql, (pyodbc.Binary(raw), key))
    except Exception, e:
        raise e
        return false
    finally:
        con.commit()
        con.close()

    return True

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

def test():
    sql = "select iID, iFactoryID, sOrderNo, sStyleNo, sProductID, dRequestCheck, sCheckItemDesc, sQCUserID, sUserID, bApproved from qmCheckPlan"
    rows = sqlQuery(getConn(), sql)

    a = '你'

    print 'defaultencoding:' + sys.getdefaultencoding()
    print locale.getlocale()

    for row in rows:
        print chardet.detect(a)
        print repr(a)
        
        print chardet.detect(row.sCheckItemDesc)
        print repr(row.sCheckItemDesc)
        print row.sCheckItemDesc[:row.sCheckItemDesc.find(u'\x00')]
        #print row.sCheckItemDesc.decode('utf-8', 'ignore')
        

if __name__ == "__main__":
    test()
