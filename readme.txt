v0.2 20220520
增加爬取市面手机型号功能

v0.3 20220523
增加产品条码打印功能
修复市面手机型号搜索bug

v0.3.1 20220524
修复抓取参数报错问题

v0.3.2 20220525
修复解除型号绑定bug
修改绑定方式

v0.4 20220607
增加图表数据
增加手机型号详情抓取

v0.5
修复手机型号详情抓取bug
增加帐号报表app
v0.51
修复excel模板问题

v0.6
修复抓取手机型号详情bug

v0.61
修复celery bug
v0.62
修复price track bug
v0.63.2
修复product model抓取bug

v0.7
增加fbm管理app
v0.71
修复利润计算，增加产品链接，导入时产品销量计算
v0.72
添加在途库存查询
v0.73
export shengde,编辑批次号，保存打包运单
v0.74
export purchase
v0.75
packing manage
v0.76
product image
v0.77
修复运单问题，店铺资金统计
v0.8
图片大小处理
运单逻辑完善，重量完善
权限处理
筛选项处理
v0.81
订单日期筛选，中转仓优化，bug修复
v0.82
shengde export image
v0.9
1.增加操作日志 2.增加权限功能 3.其它bug修复
v0.92
1.中转仓发fbm增加物流编号,中转到仓日期修改为预约日期
2.增加fbm库存盘点，状态修改
3.财务管理操作日志
4.导入订单与所选店铺不一致处理
5.店铺销量统计
6.订单销量图表

v0.93
1.增加更新产品库产品参数同步到未发货运单
2.移除抓取mercado链接任务

v0.94
1.发仓运单增加计划数量
2.增加采购管理模块

v0.95
1.店铺中转占用统计修复bug
2.修复销售订单导入问题
3.增加发仓运单质检表导出
v0.95.1
修复fbm库存中转仓数量bug
采购管理数据核查增加成本价
v0.96
1.运单增加遗弃清单
2.增加权限设置
3.增加产品itemID修改同步到未发货运单
v0.96.1
修复运单包装信息缺失问题

v1.0
1.增加首页
2.运单增加附件
3.运单页面优化
4.运单发货前检查库存是否足够
5.自动标新品，批次号修改
6.运单增加店铺额度限制
7.增加upc号码池

v1.0.5
1.采购管理增加产品详情快速链接
2.修复收支管理统计bug
3.增加导出收支明细
4.修复上传附件bug
v1.0.5.1
修复导出收支明细bug
v1.0.7
修复采购管理重发操作，运单重复发货bug
v1.0.8
修改待采购数量显示

v1.1
增加补货推荐
修复运单新品标签bug
增加运单发货数量变动检查
增加运单入仓核查筛选
v1.1.1
修复订单上传bug
v1.1.2
增加采购管理产品名称排序
v1.1.3
fbm库存增加本地备货情况
运单列表增加排序
v1.1.4
增加中转额度计算，更新若干
v1.1.5
修复管理员编辑运单，成员账号看不到bug
优化运单发货库存扣除
v1.1.6
修复fbm运单修改时店铺额度检查bug
优化中转运单拼箱箱数问题
v1.1.7
运单增加发货变动清单标识
v1.2
产品增加若干报关信息字段
变动清单管理
优化导入订单库存扣除策略
产品库删除限制
重发操作限制
v1.2.1
修复运单显示权限bug
v1.2.2
变动清单增加保留功能
V1.2.3
店铺库存在途显示修改
增加物流跟踪
v1.3
增加多平台
增加微草物流导出
增加noon平台订单导入
修改产品图片上传大小
财务管理提现币种优化
增加库存日志
增加系统登录记录，网站关闭设置
v1.3.1
修复noon订单上传bug
增加app版本控制
v1.3.2
优化noon订单上传
v1.3.3
增加打印物流标签接口
修复中转仓发fbm平台字段缺失问题
v1.3.4
增加物流交运对接
v1.3.5
修复美客多订单利润更新问题
v.1.3.6
再次修复美客多订单利润更新问题
v1.3.7
更新noon，美客多上传模板
v1.3.8
再次更新美客多上传模板
v1.3.9
店铺归属权转移
v1.4.0
增加fbm库存同步中转库存
增加运单物流对账
v1.4.1
增加采购管理库存迁移
增加运单异常状态
订单上传增加标题行自定义
v1.4.2
修改产品上传模板
v1.4.3
修复外汇资金显示问题，精度
修改运单批次号同时修改文件夹名称
增加店铺费用,显示，导出
增加ozon订单导入
v1.4.4
修改产品销量计算时间（时差）
修改每天订单销量状态过滤（弃用）
v1.4.5
修复oz订单上传bug
v1.4.6
修复店铺数据计算bug
订单详情显示优化
v1.4.7
更新美客多订单上传模板
v1.4.8
更新noon，ozon订单上传模板
v1.4.9
更新ozon订单上传状态bug
v1.5.0
增加利润计算工具
v1.5.5
增加产品开发app
增加邮编分区查询
增加oz运单导出
v1.5.6
增加关联列表
修复部分bug
增加部分字段
v1.5.7
增加开发产品订单
v1.5.8
开发产品增加跨境开关选项
修复oz装箱单导出问题
v1.5.9
修复oz上传订单取消状态问题
v1.6.0
增加批量查询邮编
v1.6.1
修复开发产品包含跨境号发布bug
v1.6.1a
修复ml上传订单格式问题
v1.6.2
新增导出OZ物流箱唛号映射表，跨箱装箱表
v1.6.3
ml导入订单改进
v1.6.4
修复oz结算上传表
v1.6.5
修复oz费用上传
v1.6.6
修复ml订单上传格式
v1.6.7
增加sd cookies设置
v1.6.8
修复ml订单上传格式 postage 和 fees 字段
v1.6.9
增加ml产品复制功能
修复物流对账货品运费没有均摊问题
v1.6.10
修复复制产品图片导致的bug
v1.6.11
修复oz费用上传问题
v1.6.12
增加打印upc标签
v1.6.13
修复新平台链接问题

