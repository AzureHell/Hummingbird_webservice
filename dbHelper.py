#!/usr/bin/python
# -*- coding: utf-8 -*-

import sys
import time
import pyodbc
import chardet
import locale


locale.setlocale(locale.LC_ALL, "en_US.UTF-8")
# 数据交互


def getConn():
    # mac 下使用模式
    return pyodbc.connect('DRIVER={mssql};Server=192.168.56.101,1433;\
        DATABASE=qchelper;UID=sa;PWD=123;TDS_Version=8.0;CHARSET=UTF8;')
    # windows 下使用模式
    # return pyodbc.connect('DRIVER={SQL Server};Server=.;\
    #     DATABASE=qchelper;UID=qchelper;PWD=1qaz2wsx;')


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
    sql = "select top 1 sUserID, sUserName, sPasswordMD5 from smUser"
    rows = sqlQuery(getConn(), sql)
    
    for row in rows:
        return row[0] + " : " + row[1] + ',defaultencoding:' \
            + sys.getdefaultencoding()


def check_user_cret(username, password):
    sql = "select top 1 sUserID, sUserName, sPasswordMD5 \
        from smUser where sUserID = '%s' " % (username)
    rows = sqlQuery(getConn(), sql)
    #1 row only
    for row in rows:
        if row.sPasswordMD5 == password:
            return True
    return False


def checkUser(username, password):
    sql = "select top 1 sUserID, sUserName, sPasswordMD5 \
        from smUser \
        where sUserID = '%s' " % (username)
    print(sql)
    print password
    rows = sqlQuery(getConn(), sql)
    for row in rows:
        if not row.sPasswordMD5 or row.sPasswordMD5 == "":
            return 'error:password is null!'
        elif row.sPasswordMD5 == password:
            return '{"user_id":"' + str(row.sUserID) + '","user_name":"' \
                + row.sUserName + '"}'
    return 'error:not record!'


def downloadCheckPlan(sQCUserID, iID):
    jsonresult = ''
    record_count = 0
    sql = "select iID, iFactoryID, sOrderNo, sStyleNo, sProductID, \
        dRequestCheck, sCheckItemDesc, sQCUserID, sUserID, bApproved \
        from qmCheckPlan \
        where sQCUserID = '%s' and iID > %s \
        and bApproved = 1" % (sQCUserID, iID)
    rows = sqlQuery(getConn(), sql)
    for row in rows:
        #临时用这种方法处理下
        if row.sCheckItemDesc:
            sCheckItemDesc = \
                row.sCheckItemDesc[:row.sCheckItemDesc.find(u'\x00')]
        else:
            sCheckItemDesc = ""
            # sCheckItemDesc = "1.产前检查 2.品质检查 3.包装检查"
        stra = '{"iID":"' + str(row.iID) + '","iFactoryID":"' \
            + str(row.iFactoryID) \
            + '","sOrderNo":"' + row.sOrderNo + '","sStyleNo":"' \
            + row.sStyleNo \
            + '","sProductID":"' + row.sProductID + '","dRequestCheck":"' \
            + str(row.dRequestCheck) + '","sCheckItemDesc":"' \
            + sCheckItemDesc \
            + '","sQCUserID":"' + str(row.sQCUserID) + '","sUserID":"' \
            + str(row.sUserID) + '","bApproved":"' + str(row.bApproved) + '"}'
        if jsonresult != '':
            jsonresult += ',' + stra
        else:
            jsonresult = stra
        record_count += 1
    if jsonresult != "":
        jsonresult = '{"table":"qmCheckPlan","count":"' + str(record_count) \
            + '","records":[' + jsonresult + ']}'
    else:
        jsonresult = "error:no record!"
    return jsonresult


def fieldisNull(x):
    if x == "null":
        return x
    else:
        return "'" + x + "'"


def uploadCheckRecord(masterDict, detailCount, detailDict):
    sql = "if not exists (select top 1 1 from qmCheckRecordMst \
        where uMobileKey = " + fieldisNull(masterDict[0]['uMobileKey']) + ") "
    sql += "insert into qmCheckRecordMst(iFactoryID, sOrderNo, \
        sStyleNo, sProductID "
    sql += ", iItemID, dCheckedDate, sRemark, sUserID, datetime_rec, \
        datetime_modify, datetime_delete, datetime_upload, uMobileKey "
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
    sql += "," + fieldisNull(time.strftime("%Y-%m-%d %H:%M:%S",
        time.localtime()))
    sql += "," + fieldisNull(masterDict[0]['uMobileKey'])
    sql += " else update qmCheckRecordMst set "
    sql += " dCheckedDate = " + fieldisNull(masterDict[0]['dCheckedDate'])
    sql += ",sRemark = " + fieldisNull(masterDict[0]['sRemark'])
    sql += ",datetime_modify = " \
        + fieldisNull(masterDict[0]['datetime_modify'])
    sql += ",datetime_delete = " \
        + fieldisNull(masterDict[0]['datetime_delete'])
    sql += ",datetime_upload = " \
        + fieldisNull(time.strftime("%Y-%m-%d %H:%M:%S", time.localtime()))
    sql += " where uMobileKey = " + fieldisNull(masterDict[0]['uMobileKey'])
    sql += ";"

    for i in range(0, detailCount):
        sql += "if not exists (select top 1 1 from qmCheckRecordDtl \
            where uMobileKey = " + fieldisNull(detailDict[i]['uMobileKey']) \
            + ") "
        sql += "insert into qmCheckRecordDtl(iMstID, dCreateDate, \
            datetime_modify, datetime_delete, uMobileKey)"
        sql += "select isnull((select max(iId) from qmCheckRecordMst \
            where uMobileKey = " + fieldisNull(masterDict[0]['uMobileKey'])
        sql += " ), 0) as iMstID "
        sql += "," + fieldisNull(detailDict[i]['dCreateDate'])
        sql += "," + fieldisNull(detailDict[i]['datetime_modify'])
        sql += "," + fieldisNull(detailDict[i]['datetime_delete'])
        sql += "," + fieldisNull(detailDict[i]['uMobileKey'])
        sql += " else update qmCheckRecordDtl set "
        sql += " datetime_modify = " \
            + fieldisNull(detailDict[i]['datetime_modify'])
        sql += ",datetime_delete = " \
            + fieldisNull(detailDict[i]['datetime_delete'])
        sql += " where uMobileKey = " \
            + fieldisNull(detailDict[i]['uMobileKey'])
        sql += ";"

    print(sql)
    sqlExcute(getConn(), sql.encode('utf-8'))

    sql = ""
    sql += "select top 1 datetime_upload from qmCheckRecordMst "
    sql += " where uMobileKey = '" + masterDict[0]["uMobileKey"] \
        + "' ;"
    print(sql)
    rows = sqlQuery(getConn(), sql.encode('utf-8'))
    #只有一条记录
    record_string = ""
    record_count = 0
    for row in rows:
        record_string += '{"uMobileKey":"' + str(masterDict[0]["uMobileKey"]) \
            + '", "datetime_upload":"' + str(row.datetime_upload) + '"}'
        record_count += 1
    result = '{"table":"qmCheckRecordMst","count":"' + str(record_count) \
        + '","records":[' + record_string + ']}'
    return result


def uploadCheckRecordPic(key, raw):
    if uploadPic("qmCheckRecordDtl", "bPhoto", "uMobileKey", key, raw):
        return "{}"
    return "{}"


def uploadPic(table_name, field_name, key_name, key, raw):
    """
    统一的图片上传函数，只支持插入到表中的image字段，其他字段类型会报错
    """
    try:
        con = getConn()
        cur = con.cursor()
        sql = "update " + table_name + " set " + field_name + " = ? where " \
            + key_name + " = ?"
        cur.execute(sql, (pyodbc.Binary(raw), key))
    except Exception, e:
        raise e
        return False
    finally:
        con.commit()
        con.close()

    return True


def showPic():
    con = getConn()
    cur = con.cursor()

    sql = "select top 1 bPhoto from qmCheckRecordDtl"
    cur.execute(sql)
    x = cur.fetchall()
    for r in x:
        return r.bPhoto
    con.close()


def test():
    sql = "select iID, iFactoryID, sOrderNo, sStyleNo, sProductID, \
        dRequestCheck, sCheckItemDesc, sQCUserID, sUserID, bApproved \
        from qmCheckPlan"
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
