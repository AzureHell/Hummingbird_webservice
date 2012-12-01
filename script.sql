create database qchelper
go
use qchelper
go
if object_id('dbo.users') is not null
	drop table dbo.users
create table dbo.users (
	user_id int,
	user_name varchar(50),
	password varchar(50)
)
go
--QC计划表
if object_id('dbo.qmCheckPlan') is not null
	drop table dbo.qmCheckPlan
create table dbo.qmCheckPlan (
	iID int,
	iFactoryID int,
	sOrderNo varchar(50),
	sStyleNO varchar(50),
	--本厂款号
	sProductID varchar(50),
	--要求检验时间
	dRequestCheck datetime,
	--检验项目描述
	sCheckItemDesc varchar(max),
	--QC检验人，指出该计划单分配给哪位QC
	sQCUserID varchar(50),
	sUserID varchar(50)
)
go
--QC检验表，
if object_id('dbo.qmCheckRecordMst') is not null
	drop table dbo.qmCheckRecordMst
create table dbo.qmCheckRecordMst (
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
	--对应的Adnroid上的检验
	id_upload int,
	--
	user_id_opt int
)
go
--QC¼ìÑéÃ÷Ï¸£¬ºÍÉÏÃæµÄ±íÖ÷´Ó£¬ÊÇÎªÁË¶àÕÅÍ¼Æ¬µÄÉÏ´«
if object_id('dbo.qmCheckRecordDtl') is not null
	drop table dbo.qmCheckRecordDtl
create table dbo.qmCheckRecordDtl (
	iID int,
	iMstID int,
	--ÒòÎª¶ÀÁ¢µÄÍ¼Æ¬´«Êä£¬ËùÒÔÕâ¸ö×Ö¶ÎÓÃÓÚ¿ØÖÆÍ¼Æ¬µÄ´«ÊäÇé¿ö
	sFileName varchar(50),
	--Í¼Æ¬´æ´¢×Ö¶Î£¬Ö±½Ó´æ´¢ÔÚÊý¾Ý¿âÖÐ
	bPhoto image,
	dCreateDate datetime,
	datetime_delete datetime
)
go
select * from dbo.users
go
--Ä£ÄâÕÊºÅÊý¾Ý
insert into dbo.users
select 1, 'test', '85786DB87A98DECD' --ÃÜÂë£º123
go
select iID, iFactoryID, sOrderNo, sStyleNo, sProductID, dRequestCheck, sCheckItemDesc, sQCUserID, sUserID from qmCheckPlan
go
--Ä£ÄâQC¼Æ»®Êý¾Ý
insert into qmCheckPlan(iID, iFactoryID, sOrderNo, sStyleNo, sProductID, dRequestCheck, sCheckItemDesc, sQCUserID, sUserID)
select 1, 12, 'SC010', 'QX7886', 'P0000001', '2012-11-22', '1£ºÃæÁÏ¡¢¸¨ÁÏÆ·ÖÊÓÅÁ¼£¬·ûºÏ¿Í»§ÒªÇó£»2£º¿îÊ½ÅäÉ«×¼È·ÎÞÎó£»3£º°ü×°ÃÀ¹Û¡¢Åä±ÈÕýÈ·¡£', '1', '1'
insert into qmCheckPlan(iID, iFactoryID, sOrderNo, sStyleNo, sProductID, dRequestCheck, sCheckItemDesc, sQCUserID, sUserID)
select 2, 12, 'SC011', 'TX7001', 'P0000002', '2012-11-28', '1£ºÃæÁÏ¡¢¸¨ÁÏÆ·ÖÊÓÅÁ¼£¬·ûºÏ¿Í»§ÒªÇó£»2£ºË®Ï´É«ÀÎ¶È£»3£º°ü×°ÃÀ¹Û¡¢Åä±ÈÕýÈ·¡£', '1', '1'
insert into qmCheckPlan(iID, iFactoryID, sOrderNo, sStyleNo, sProductID, dRequestCheck, sCheckItemDesc, sQCUserID, sUserID)
select 3, 18, 'SC011', 'YW0006', 'P0000003', '2012-11-30', '1¡¢¶ÔÉ«×¼È·£¬´ó»õ²¼µÄÑÕÉ«ºÍÈ·ÈÏÉ«µÄÉ«²îÖÁÉÙÓ¦ÔÚ3.5¼¶Ö®ÄÚ£¬²¢Ðè¾­¿Í»§È·ÈÏ; 2¡¢¿îÊ½ÅäÉ«×¼È·ÎÞÎó; 3¡¢°ü×°ÃÀ¹Û¡¢Åä±ÈÕýÈ·.', 'test', '1'
insert into qmCheckPlan(iID, iFactoryID, sOrderNo, sStyleNo, sProductID, dRequestCheck, sCheckItemDesc, sQCUserID, sUserID)
select 4, 12, 'SC012', 'QX1111', 'P0000004', '2012-12-08', '1£º²úÆ·¸É¾»¡¢Õû½à¡¢ÂôÏàºÃ£»2£º¿îÊ½ÅäÉ«×¼È·ÎÞÎó£»3£º°ü×°ÃÀ¹Û¡¢Åä±ÈÕýÈ·£»4£ºÃæÁÏ¡¢¸¨ÁÏÆ·ÖÊÓÅÁ¼£¬·ûºÏ¿Í»§ÒªÇó¡£', '1', '1'
insert into qmCheckPlan(iID, iFactoryID, sOrderNo, sStyleNo, sProductID, dRequestCheck, sCheckItemDesc, sQCUserID, sUserID)
select 5, 20, 'SC012', 'UK1256', 'P0000005', '2012-12-12', '1¡¢²úÆ·¸É¾»¡¢Õû½à¡¢ÂôÏàºÃ; 2¡¢¿îÊ½ÅäÉ«×¼È·ÎÞÎó; 3¡¢°ü×°ÃÀ¹Û¡¢Åä±ÈÕýÈ·; 4¡¢Ë®Ï´É«ÀÎ¶È; 5¡¢ÃæÁÏ¡¢¸¨ÁÏÆ·ÖÊÓÅÁ¼£¬·ûºÏ¿Í»§ÒªÇó.', 'U001', '1'
insert into qmCheckPlan(iID, iFactoryID, sOrderNo, sStyleNo, sProductID, dRequestCheck, sCheckItemDesc, sQCUserID, sUserID)
select 6, 22, 'SC022', 'LP6589', 'P0000006', '2012-12-22', '1¡¢ÃæÁÏ¡¢¸¨ÁÏÆ·ÖÊÓÅÁ¼£¬·ûºÏ¿Í»§ÒªÇó; 2¡¢¿îÊ½ÅäÉ«×¼È·ÎÞÎó; 3¡¢°ü×°ÃÀ¹Û¡¢Åä±ÈÕýÈ·.', 'U001', '1'
go
