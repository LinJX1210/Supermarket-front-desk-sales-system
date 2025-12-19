# 超市前台销售系统 - ER图说明

## 一、总体ER图描述

### 1.1 实体清单（共21个）

本系统共有21个实体，按模块划分如下：

**用户权限模块（2个）：** sys_user（系统用户）、sys_user_log（用户操作日志）

**会员管理模块（5个）：** member_level_rule（会员等级规则）、member（会员）、member_change_log（会员变更记录）、gift（礼品）、points_exchange_record（积分兑换记录）

**商品管理模块（7个）：** goods_category（商品分类）、shelf_area（货架区域）、shelf（货架）、goods（商品）、inventory（库存）、goods_operation_log（商品操作记录）、stock_in_record（入库记录）

**收银管理模块（3个）：** order_info（订单）、order_detail（订单明细）、payment_record（支付记录）

**退货管理模块（3个）：** return_record（退货记录）、return_detail（退货明细）、quality_feedback（质量反馈）

**系统通知模块（1个）：** sys_notification（系统通知）

### 1.2 总体关系描述

**sys_user（系统用户）的关系：**
- sys_user 与 sys_user_log 是一对多关系：一个用户产生多条操作日志
- sys_user 与 member 是一对一关系（可选）：一个用户可关联一个会员账号
- sys_user 与 order_info 是一对多关系：一个收银员创建多个订单
- sys_user 与 return_record 是一对多关系：一个售后管理员处理多个退货
- sys_user 与 quality_feedback 是一对多关系：一个商品管理员处理多条质量反馈
- sys_user 与 goods_operation_log 是一对多关系：一个操作员产生多条商品操作记录
- sys_user 与 member_change_log 是一对多关系：一个操作员产生多条会员变更记录
- sys_user 与 stock_in_record 是一对多关系：一个操作员产生多条入库记录
- sys_user 与 points_exchange_record 是一对多关系：一个操作员处理多条积分兑换
- sys_user 与 sys_notification 是一对多关系：一个用户收到多条系统通知

**member_level_rule（会员等级规则）的关系：**
- member_level_rule 与 member 是一对多关系：一个等级规则对应多个会员

**member（会员）的关系：**
- member 与 member_change_log 是一对多关系：一个会员有多条变更记录
- member 与 order_info 是一对多关系：一个会员有多个消费订单
- member 与 points_exchange_record 是一对多关系：一个会员有多条积分兑换记录

**goods_category（商品分类）的关系：**
- goods_category 与 goods_category 是自关联关系：通过parent_id实现课-类-种三级分类
- goods_category 与 goods 是一对多关系：一个分类下有多个商品

**shelf_area（货架区域）的关系：**
- shelf_area 与 shelf 是一对多关系：一个区域有多个货架

**shelf（货架）的关系：**
- shelf 与 goods 是一对多关系：一个货架上放置多个商品

**goods（商品）的关系：**
- goods 与 inventory 是一对一关系：一个商品对应一条库存记录
- goods 与 goods_operation_log 是一对多关系：一个商品有多条操作记录
- goods 与 stock_in_record 是一对多关系：一个商品有多条入库记录
- goods 与 order_detail 是一对多关系：一个商品出现在多个订单明细中
- goods 与 return_detail 是一对多关系：一个商品出现在多个退货明细中
- goods 与 quality_feedback 是一对多关系：一个商品可能有多条质量反馈

**gift（礼品）的关系：**
- gift 与 points_exchange_record 是一对多关系：一个礼品被多次兑换

**order_info（订单）的关系：**
- order_info 与 order_detail 是一对多关系：一个订单有多个商品明细
- order_info 与 payment_record 是一对多关系：一个订单有多条支付记录（支持混合支付）
- order_info 与 return_record 是一对多关系：一个订单可能有多次退货记录
- order_info 与 points_exchange_record 是一对多关系：一个订单可能关联积分抵扣记录

**order_detail（订单明细）的关系：**
- order_detail 与 return_detail 是一对多关系：一个订单明细可能被多次部分退货

**return_record（退货记录）的关系：**
- return_record 与 return_detail 是一对多关系：一个退货记录有多个退货商品明细
- return_record 与 quality_feedback 是一对多关系：一个退货记录可能产生多条质量反馈

---

## 二、组员1（组长）ER图 - 收银管理 + 系统框架

### 2.1 涉及实体

组员1负责的核心实体有6个：sys_user（系统用户）、sys_user_log（用户操作日志）、order_info（订单）、order_detail（订单明细）、payment_record（支付记录）、sys_notification（系统通知）。

另外需要关联使用2个其他组员的实体：member（会员，组员3负责）、goods（商品，组员2负责）。

### 2.2 实体关系描述

**sys_user（系统用户）：**
- sys_user 与 sys_user_log 是一对多关系：一个用户产生多条操作日志，通过user_id关联。
- sys_user 与 order_info 是一对多关系：一个收银员（cashier_id）创建多个订单。
- sys_user 与 sys_notification 是一对多关系：一个用户（target_user_id）收到多条系统通知。

**order_info（订单）：**
- order_info 与 order_detail 是一对多关系：一个订单包含多个商品明细，通过order_id关联。
- order_info 与 payment_record 是一对多关系：一个订单可以有多条支付记录（支持现金+银行卡混合支付），通过order_id关联。
- order_info 与 member 是多对一关系：多个订单属于同一个会员，通过member_id关联，非会员消费时member_id为空。

**order_detail（订单明细）：**
- order_detail 与 goods 是多对一关系：多个订单明细关联同一个商品，通过goods_id关联。

### 2.3 关键属性说明

order_info的order_status属性有6个取值：pending_pay（待结账）、hanged（挂单中）、completed（已完成）、cancelled（已撤销）、full_returned（已整单退货）、part_returned（部分退货）。

payment_record的payment_type属性有4个取值：cash（现金）、bank_card（银行卡）、coupon（赠券）、points（积分）。transaction_type属性有2个取值：pay（支付）、refund（退款）。

---

## 三、组员2 ER图 - 商品管理 + 库存管理

### 3.1 涉及实体

组员2负责的核心实体有7个：goods_category（商品分类）、shelf_area（货架区域）、shelf（货架）、goods（商品）、inventory（库存）、goods_operation_log（商品操作记录）、stock_in_record（入库记录）。

另外需要接收组员4的quality_feedback（质量反馈）来处理商品下架。

### 3.2 实体关系描述

**goods_category（商品分类）：**
- goods_category 与自身是自关联关系：通过parent_id字段实现课-类-种三级分类结构。level=1表示课（如食品课），level=2表示类（如膨化食品类），level=3表示种（如雪饼）。
- goods_category 与 goods 是一对多关系：一个分类（种级别）下有多个商品，通过category_id关联。

**shelf_area（货架区域）：**
- shelf_area 与 shelf 是一对多关系：一个区域（如A区）包含多个货架，通过area_id关联。

**shelf（货架）：**
- shelf 与 goods 是一对多关系：一个货架上放置多个商品，通过shelf_id关联。货架编码格式为"区-架-层"，如A-01-02。

**goods（商品）：**
- goods 与 inventory 是一对一关系：每个商品对应唯一一条库存记录，通过goods_id关联。
- goods 与 goods_operation_log 是一对多关系：一个商品有多条操作记录（上架、下架、移架、调价等），通过goods_id关联。
- goods 与 stock_in_record 是一对多关系：一个商品有多条入库记录，通过goods_id关联。
- goods 与 quality_feedback 是一对多关系：一个商品可能收到多条质量反馈，通过goods_id关联（与组员4交互）。

### 3.3 关键属性说明

goods_category的level属性有3个取值：1（课）、2（类）、3（种）。delete_flag属性用于软删除：0（正常）、1（已删除）。

goods的shelf_status属性有5个取值：pending_shelf（待上架）、on_shelf（在架）、off_shelf（已下架）、pending_inspect（待质检）、suspend_sale（暂停销售）。is_weighted属性标识是否为散装称重商品：0（否）、1（是）。

inventory的stock_status属性有3个取值：sufficient（充足）、stock_shortage（库存短缺）、shelf_shortage（在架短缺）。stock_warning和shelf_warning分别为库存警戒值和在架警戒值。

---

## 四、组员3 ER图 - 会员管理 + 用户权限

### 4.1 涉及实体

组员3负责的核心实体有6个：sys_user（系统用户，与组员1共用）、member_level_rule（会员等级规则）、member（会员）、member_change_log（会员变更记录）、gift（礼品）、points_exchange_record（积分兑换记录）。

另外需要与组员1的order_info（订单）关联，记录会员消费和积分抵扣。

### 4.2 实体关系描述

**sys_user（系统用户）：**
- sys_user 与 member 是一对一关系（可选）：一个系统用户可以关联一个会员账号，通过user_id关联。会员也可以不关联系统用户。

**member_level_rule（会员等级规则）：**
- member_level_rule 与 member 是一对多关系：一个等级规则对应多个会员，通过level_code关联。

**member（会员）：**
- member 与 member_change_log 是一对多关系：一个会员有多条信息变更记录（包括信息修改、升级、降级、积分变动），通过member_id关联。
- member 与 order_info 是一对多关系：一个会员有多个消费订单，通过member_id关联（与组员1交互）。
- member 与 points_exchange_record 是一对多关系：一个会员有多条积分兑换记录，通过member_id关联。

**gift（礼品）：**
- gift 与 points_exchange_record 是一对多关系：一个礼品可以被多个会员兑换多次，通过gift_id关联。

**points_exchange_record（积分兑换记录）：**
- points_exchange_record 与 order_info 是多对一关系：当积分用于抵扣消费时，关联对应的订单，通过order_id关联（与组员1交互）。

### 4.3 关键属性说明

member_level_rule的level_code属性有3个取值：normal（普通会员）、silver（银卡会员）、gold（金卡会员）。discount_rate为折扣比例（如0.95表示95折），points_rate为积分比例（每消费1元获得的积分数）。

member的level_code属性记录当前会员等级，total_consume记录累计消费金额，total_points记录当前可用积分。status属性有2个取值：active（正常）、disabled（禁用）。

member_change_log的change_type属性有4个取值：info（信息变更）、level_up（升级）、level_down（降级）、points（积分变动）。

points_exchange_record的exchange_type属性有2个取值：gift（兑换礼品）、cash（抵扣现金）。

---

## 五、组员4 ER图 - 退货管理 + 查询统计

### 5.1 涉及实体

组员4负责的核心实体有3个：return_record（退货记录）、return_detail（退货明细）、quality_feedback（质量反馈）。

需要关联使用其他组员的实体：order_info（订单，组员1）、order_detail（订单明细，组员1）、goods（商品，组员2）、member（会员，组员3）、sys_user（系统用户，组员1）。

### 5.2 实体关系描述

**return_record（退货记录）：**
- return_record 与 order_info 是多对一关系：多个退货记录关联同一个原订单（部分退货场景下一个订单可能多次退货），通过order_id关联（与组员1交互）。
- return_record 与 sys_user 是多对一关系：多个退货记录由同一个售后管理员处理，通过operator_id关联。
- return_record 与 return_detail 是一对多关系：一个退货记录包含多个退货商品明细，通过return_id关联。
- return_record 与 quality_feedback 是一对多关系：一个退货记录可能产生多条质量反馈（多个商品都有质量问题），通过return_id关联。

**return_detail（退货明细）：**
- return_detail 与 order_detail 是多对一关系：退货明细关联原订单中的商品明细，通过order_detail_id关联（与组员1交互）。
- return_detail 与 goods 是多对一关系：退货明细关联商品信息，通过goods_id关联（与组员2交互）。

**quality_feedback（质量反馈）：**
- quality_feedback 与 goods 是多对一关系：质量反馈关联问题商品，通过goods_id关联。商品管理员（组员2）根据反馈处理商品下架。
- quality_feedback 与 sys_user 是多对一关系：质量反馈由商品管理员处理，通过handler_id关联。

### 5.3 关键属性说明

return_record的return_type属性有2个取值：full（整单退货）、part（部分退货）。return_reason属性有5个取值：quality_issue（质量问题）、no_reason_7day（7天无理由）、spec_mismatch（规格不符）、damaged（损坏）、other（其他）。points_deducted记录本次退货扣减的会员积分。

return_detail的goods_status属性有4个取值：to_stock（转入库存）、pending_inspect（待质检）、off_shelf（已下架）、repaired（修缮后上架）。非质量问题的商品转入库存，质量问题商品进入待质检状态。

quality_feedback的feedback_status属性有3个取值：pending（待处理）、processing（处理中）、completed（已完成）。handle_result属性有4个取值：batch_off_shelf（批量下架同条码商品）、single_off_shelf（仅下架该商品）、repair（修缮后上架）、no_action（无需处理）。last_remind_time用于实现每4小时提醒商品管理员处理的机制。

---

## 六、模块间交互关系

### 6.1 组员1与组员2的交互

组员1的order_detail（订单明细）通过goods_id关联组员2的goods（商品）。收银结账时，组员1需要调用组员2的库存接口，扣减对应商品的在架数量（inventory表的on_shelf_num字段）。

### 6.2 组员1与组员3的交互

组员1的order_info（订单）通过member_id关联组员3的member（会员）。收银时，组员1需要调用组员3的会员接口，获取会员折扣比例，并在结账后累计会员消费金额和积分，同时检查是否触发会员升级。

### 6.3 组员4与组员1的交互

组员4的return_record（退货记录）通过order_id关联组员1的order_info（订单），return_detail（退货明细）通过order_detail_id关联组员1的order_detail（订单明细）。退货时需要查询原订单信息，退款方式需与原支付方式一致。

### 6.4 组员4与组员2的交互

组员4的quality_feedback（质量反馈）通过goods_id关联组员2的goods（商品）。当退货原因为质量问题时，组员4提交质量反馈，组员2的商品管理员收到通知后处理商品下架或修缮。退货完成后，非质量问题的商品需要恢复库存（调用组员2的库存接口）。

### 6.5 组员4与组员3的交互

退货时，组员4需要调用组员3的会员接口，扣减会员对应的消费积分。如果扣减后积分或累计消费低于当前等级标准，需触发会员降级逻辑。

### 6.6 组员3与组员1的交互

组员3的points_exchange_record（积分兑换记录）通过order_id关联组员1的order_info（订单）。当会员使用积分抵扣消费时，需要记录关联的订单。

---

## 七、关系汇总表

| 实体1 | 关系 | 实体2 | 关联字段 | 说明 |
|-------|------|-------|----------|------|
| sys_user | 1:N | sys_user_log | user_id | 用户操作日志 |
| sys_user | 1:1 | member | user_id | 可选关联 |
| sys_user | 1:N | order_info | cashier_id | 收银员 |
| sys_user | 1:N | return_record | operator_id | 售后管理员 |
| sys_user | 1:N | quality_feedback | handler_id | 处理人 |
| sys_user | 1:N | goods_operation_log | operator_id | 操作人 |
| sys_user | 1:N | member_change_log | operator_id | 操作人 |
| sys_user | 1:N | stock_in_record | operator_id | 操作人 |
| sys_user | 1:N | points_exchange_record | operator_id | 操作人 |
| sys_user | 1:N | sys_notification | target_user_id | 目标用户 |
| member_level_rule | 1:N | member | level_code | 等级规则 |
| member | 1:N | member_change_log | member_id | 变更记录 |
| member | 1:N | order_info | member_id | 消费订单 |
| member | 1:N | points_exchange_record | member_id | 积分兑换 |
| goods_category | 自关联 | goods_category | parent_id | 父子分类 |
| goods_category | 1:N | goods | category_id | 分类商品 |
| shelf_area | 1:N | shelf | area_id | 区域货架 |
| shelf | 1:N | goods | shelf_id | 货架商品 |
| goods | 1:1 | inventory | goods_id | 库存 |
| goods | 1:N | goods_operation_log | goods_id | 操作记录 |
| goods | 1:N | stock_in_record | goods_id | 入库记录 |
| goods | 1:N | order_detail | goods_id | 订单明细 |
| goods | 1:N | return_detail | goods_id | 退货明细 |
| goods | 1:N | quality_feedback | goods_id | 质量反馈 |
| gift | 1:N | points_exchange_record | gift_id | 兑换记录 |
| order_info | 1:N | order_detail | order_id | 订单明细 |
| order_info | 1:N | payment_record | order_id | 支付记录 |
| order_info | 1:N | return_record | order_id | 退货记录 |
| order_info | 1:N | points_exchange_record | order_id | 积分抵扣 |
| order_detail | 1:N | return_detail | order_detail_id | 退货明细 |
| return_record | 1:N | return_detail | return_id | 退货明细 |
| return_record | 1:N | quality_feedback | return_id | 质量反馈 |
