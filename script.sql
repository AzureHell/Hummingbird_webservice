--创建测试数据库
--create database qchelper
go
use qchelper
go

if object_id('dbo.users') is not null
    drop table dbo.users
create table Users (
    user_id int,
    user_name varchar(50),
    password varchar(50)
);
go
--QC计划表
if object_id('dbo.qmCheckPlan') is not null
    drop table dbo.qmCheckPlan
create table qmCheckPlan (
    iID int,
    iFactoryID int,
    sOrderNo varchar(50),
    sStyleNO varchar(50),
    --本厂款号
    sProductID varchar(50),
    --要求检验时间
    dRequestCheck datetime,
    --检验项目描述
    sCheckItemDesc varchar(500),
    --QC检验人，指出该计划单分配给哪位QC
    sQCUserID varchar(50),
    sUserID varchar(50),
    --增加审核字段，1表示审核，0表示草稿。数据同步只同步状态为1的数据
    bApproved bit
);
go
--QC检验表，
if object_id('dbo.qmCheckRecordMst') is not null
    drop table dbo.qmCheckRecordMst
create table qmCheckRecordMst (
    iID int identity(1,1) primary key,
    iFactoryID int,
    sOrderNo varchar(50),
    sStyleNO varchar(50),
    sProductID varchar(50),
    --检验项目编号
    iItemID int,
    --填写的检验时间
    dChecdedDate datetime,
    --检验总结
    sRemark varchar(500),
    datetime_rec datetime,
    datetime_delete datetime,
    datetime_upload datetime,
    --Android上的检验记录主键ID
    id_upload int,
    --Android端上传的用户ID
    user_id_opt int
);
go
--QC检验明细，主要用户存储检验图片，一个检验项目会对应多张检验图片
if object_id('dbo.qmCheckRecordDtl') is not null
    drop table dbo.qmCheckRecordDtl
create table qmCheckRecordDtl (
    iID int,
    iMstID int,
    --文件名称，该字段是用于同步文件时使用的，与业务没有关系。
    --在同步数据时会在这里生成一个文件名称:用户ID+主表ID+当前记录ID.png
    --在同步完数据后同步图片时会根据该名称将图片写到响应的bPhoto字段中
    sFileName varchar(50),
    --用于存储图片，因为pyodbc的原因该字段只支持image类型
    bPhoto image,
    dCreateDate datetime,
    datetime_delete datetime
);
go
select * from users;
go
--插入测试用户
insert into users
select 1, 'test', '85786DB87A98DECD'; --两次MD5加密，该密码为：123
go
select iID, iFactoryID, sOrderNo, sStyleNo, sProductID, dRequestCheck, sCheckItemDesc, sQCUserID, sUserID from qmcheckplan;
go
--插入测试数据
insert into qmCheckPlan(iID, iFactoryID, sOrderNo, sStyleNo, sProductID, dRequestCheck, sCheckItemDesc, sQCUserID, sUserID, bApproved)
select 1, 12, 'SC010', 'QX7886', 'P0000001', '2012-11-22', '1.产前检查 2.品质检查 3.包装检查', '1', '1', 1;
insert into qmCheckPlan(iID, iFactoryID, sOrderNo, sStyleNo, sProductID, dRequestCheck, sCheckItemDesc, sQCUserID, sUserID, bApproved)
select 2, 12, 'SC011', 'TX7001', 'P0000002', '2012-11-28', '1.产前检查 2.品质检查 3.包装检查', '1', '1', 1;
insert into qmCheckPlan(iID, iFactoryID, sOrderNo, sStyleNo, sProductID, dRequestCheck, sCheckItemDesc, sQCUserID, sUserID, bApproved)
select 3, 18, 'SC011', 'YW0006', 'P0000003', '2012-11-30', '1.产前检查 2.品质检查 3.包装检查', 'test', '1', 1;
insert into qmCheckPlan(iID, iFactoryID, sOrderNo, sStyleNo, sProductID, dRequestCheck, sCheckItemDesc, sQCUserID, sUserID, bApproved)
select 4, 12, 'SC012', 'QX1111', 'P0000004', '2012-12-08', '1.产前检查 2.品质检查 3.包装检查', '1', '1', 1;
insert into qmCheckPlan(iID, iFactoryID, sOrderNo, sStyleNo, sProductID, dRequestCheck, sCheckItemDesc, sQCUserID, sUserID, bApproved)
select 5, 20, 'SC012', 'UK1256', 'P0000005', '2012-12-12', '1.产前检查 2.品质检查 3.包装检查', 'U001', '1', 1;
insert into qmCheckPlan(iID, iFactoryID, sOrderNo, sStyleNo, sProductID, dRequestCheck, sCheckItemDesc, sQCUserID, sUserID, bApproved)
select 6, 22, 'SC022', 'LP6589', 'P0000006', '2012-12-22', '1.产前检查 2.品质检查 3.包装检查', 'U001', '1', 1;
go