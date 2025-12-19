-- =====================================================
-- 超市前台销售系统 - 数据库建表脚本
-- 数据库名: supermarket_db
-- 字符集: utf8mb4
-- =====================================================

-- 创建数据库
CREATE DATABASE IF NOT EXISTS supermarket_db DEFAULT CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;
USE supermarket_db;

-- =====================================================
-- 一、用户与权限模块
-- =====================================================

-- 1.1 系统用户表 (sys_user)
CREATE TABLE sys_user (
    user_id INT PRIMARY KEY AUTO_INCREMENT COMMENT '用户ID',
    username VARCHAR(50) NOT NULL UNIQUE COMMENT '用户名',
    password VARCHAR(64) NOT NULL COMMENT '密码(MD5加密)',
    real_name VARCHAR(50) COMMENT '真实姓名',
    phone VARCHAR(20) COMMENT '手机号',
    role ENUM('admin', 'cashier', 'goods_manager', 'after_sale') NOT NULL COMMENT '角色: admin-系统管理员, cashier-收银员, goods_manager-商品管理员, after_sale-售后管理员',
    status ENUM('active', 'disabled') DEFAULT 'active' COMMENT '状态: active-正常, disabled-禁用',
    create_time DATETIME DEFAULT CURRENT_TIMESTAMP COMMENT '创建时间',
    update_time DATETIME DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP COMMENT '更新时间',
    INDEX idx_username (username),
    INDEX idx_role (role)
) ENGINE=InnoDB COMMENT='系统用户表';

-- 1.2 用户操作日志表 (sys_user_log)
CREATE TABLE sys_user_log (
    log_id INT PRIMARY KEY AUTO_INCREMENT COMMENT '日志ID',
    user_id INT NOT NULL COMMENT '用户ID',
    operation VARCHAR(100) NOT NULL COMMENT '操作内容',
    operation_time DATETIME DEFAULT CURRENT_TIMESTAMP COMMENT '操作时间',
    ip_address VARCHAR(50) COMMENT 'IP地址',
    FOREIGN KEY (user_id) REFERENCES sys_user(user_id)
) ENGINE=InnoDB COMMENT='用户操作日志表';

-- =====================================================
-- 二、会员管理模块
-- =====================================================

-- 2.1 会员等级规则表 (member_level_rule)
CREATE TABLE member_level_rule (
    rule_id INT PRIMARY KEY AUTO_INCREMENT COMMENT '规则ID',
    level_name VARCHAR(20) NOT NULL COMMENT '等级名称',
    level_code ENUM('normal', 'silver', 'gold') NOT NULL UNIQUE COMMENT '等级代码: normal-普通会员, silver-银卡会员, gold-金卡会员',
    min_consume DECIMAL(12,2) DEFAULT 0 COMMENT '升级所需最低累计消费金额',
    min_points INT DEFAULT 0 COMMENT '升级所需最低积分',
    discount_rate DECIMAL(3,2) DEFAULT 1.00 COMMENT '折扣比例(如0.95表示95折)',
    points_rate INT DEFAULT 1 COMMENT '积分比例(每消费1元获得积分数)',
    create_time DATETIME DEFAULT CURRENT_TIMESTAMP COMMENT '创建时间',
    update_time DATETIME DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP COMMENT '更新时间'
) ENGINE=InnoDB COMMENT='会员等级规则表';

-- 2.2 会员表 (member)
CREATE TABLE member (
    member_id INT PRIMARY KEY AUTO_INCREMENT COMMENT '会员ID',
    user_id INT COMMENT '关联用户ID(可选)',
    card_no VARCHAR(20) NOT NULL UNIQUE COMMENT '会员卡号',
    name VARCHAR(50) NOT NULL COMMENT '会员姓名',
    phone VARCHAR(20) COMMENT '手机号',
    address VARCHAR(200) COMMENT '地址',
    level_code ENUM('normal', 'silver', 'gold') DEFAULT 'normal' COMMENT '会员等级',
    total_consume DECIMAL(12,2) DEFAULT 0 COMMENT '累计消费金额',
    total_points INT DEFAULT 0 COMMENT '当前积分',
    status ENUM('active', 'disabled') DEFAULT 'active' COMMENT '状态: active-正常, disabled-禁用',
    create_time DATETIME DEFAULT CURRENT_TIMESTAMP COMMENT '注册时间',
    update_time DATETIME DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP COMMENT '更新时间',
    FOREIGN KEY (user_id) REFERENCES sys_user(user_id),
    INDEX idx_card_no (card_no),
    INDEX idx_phone (phone),
    INDEX idx_level (level_code)
) ENGINE=InnoDB COMMENT='会员表';

-- 2.3 会员信息变更记录表 (member_change_log)
CREATE TABLE member_change_log (
    log_id INT PRIMARY KEY AUTO_INCREMENT COMMENT '日志ID',
    member_id INT NOT NULL COMMENT '会员ID',
    change_type VARCHAR(50) NOT NULL COMMENT '变更类型: info-信息变更, level_up-升级, level_down-降级, points-积分变动',
    old_value VARCHAR(200) COMMENT '变更前值',
    new_value VARCHAR(200) COMMENT '变更后值',
    change_reason VARCHAR(200) COMMENT '变更原因',
    operator_id INT COMMENT '操作人ID',
    change_time DATETIME DEFAULT CURRENT_TIMESTAMP COMMENT '变更时间',
    FOREIGN KEY (member_id) REFERENCES member(member_id),
    FOREIGN KEY (operator_id) REFERENCES sys_user(user_id)
) ENGINE=InnoDB COMMENT='会员信息变更记录表';

-- =====================================================
-- 三、商品管理模块
-- =====================================================

-- 3.1 商品分类表 (goods_category)
CREATE TABLE goods_category (
    category_id INT PRIMARY KEY AUTO_INCREMENT COMMENT '分类ID',
    category_name VARCHAR(50) NOT NULL COMMENT '分类名称',
    parent_id INT DEFAULT NULL COMMENT '父分类ID',
    level TINYINT NOT NULL COMMENT '层级: 1-课, 2-类, 3-种',
    sort_order INT DEFAULT 0 COMMENT '排序号',
    delete_flag TINYINT DEFAULT 0 COMMENT '删除标记: 0-正常, 1-已删除',
    create_time DATETIME DEFAULT CURRENT_TIMESTAMP COMMENT '创建时间',
    update_time DATETIME DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP COMMENT '更新时间',
    FOREIGN KEY (parent_id) REFERENCES goods_category(category_id),
    INDEX idx_parent (parent_id),
    INDEX idx_level (level)
) ENGINE=InnoDB COMMENT='商品分类表(课-类-种)';

-- 3.2 货架区域表 (shelf_area)
CREATE TABLE shelf_area (
    area_id INT PRIMARY KEY AUTO_INCREMENT COMMENT '区域ID',
    area_code VARCHAR(10) NOT NULL UNIQUE COMMENT '区域编码(如A, B, C)',
    area_name VARCHAR(50) COMMENT '区域名称',
    description VARCHAR(200) COMMENT '区域描述',
    create_time DATETIME DEFAULT CURRENT_TIMESTAMP COMMENT '创建时间'
) ENGINE=InnoDB COMMENT='货架区域表';

-- 3.3 货架表 (shelf)
CREATE TABLE shelf (
    shelf_id INT PRIMARY KEY AUTO_INCREMENT COMMENT '货架ID',
    area_id INT NOT NULL COMMENT '所属区域ID',
    shelf_code VARCHAR(20) NOT NULL UNIQUE COMMENT '货架编码(区-架-层, 如A-01-02)',
    shelf_no VARCHAR(10) NOT NULL COMMENT '货架号',
    layer_no VARCHAR(10) NOT NULL COMMENT '层号',
    capacity INT DEFAULT 100 COMMENT '容量',
    create_time DATETIME DEFAULT CURRENT_TIMESTAMP COMMENT '创建时间',
    FOREIGN KEY (area_id) REFERENCES shelf_area(area_id),
    INDEX idx_area (area_id)
) ENGINE=InnoDB COMMENT='货架表';

-- 3.4 商品表 (goods)
CREATE TABLE goods (
    goods_id INT PRIMARY KEY AUTO_INCREMENT COMMENT '商品ID',
    barcode VARCHAR(50) NOT NULL UNIQUE COMMENT '商品条码',
    goods_name VARCHAR(100) NOT NULL COMMENT '商品名称',
    category_id INT NOT NULL COMMENT '分类ID(种级别)',
    unit VARCHAR(20) DEFAULT '个' COMMENT '单位',
    is_weighted TINYINT DEFAULT 0 COMMENT '是否散装称重: 0-否, 1-是',
    price DECIMAL(10,2) NOT NULL COMMENT '销售单价',
    cost_price DECIMAL(10,2) COMMENT '成本价',
    shelf_id INT COMMENT '货架ID',
    shelf_status ENUM('pending_shelf', 'on_shelf', 'off_shelf', 'pending_inspect', 'suspend_sale') DEFAULT 'pending_shelf' COMMENT '上架状态: pending_shelf-待上架, on_shelf-在架, off_shelf-已下架, pending_inspect-待质检, suspend_sale-暂停销售',
    discount DECIMAL(3,2) DEFAULT 1.00 COMMENT '临时折扣(如0.8表示8折)',
    discount_start DATETIME COMMENT '折扣开始时间',
    discount_end DATETIME COMMENT '折扣结束时间',
    off_shelf_reason VARCHAR(200) COMMENT '下架原因',
    create_time DATETIME DEFAULT CURRENT_TIMESTAMP COMMENT '创建时间',
    update_time DATETIME DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP COMMENT '更新时间',
    FOREIGN KEY (category_id) REFERENCES goods_category(category_id),
    FOREIGN KEY (shelf_id) REFERENCES shelf(shelf_id),
    INDEX idx_barcode (barcode),
    INDEX idx_category (category_id),
    INDEX idx_shelf_status (shelf_status)
) ENGINE=InnoDB COMMENT='商品表';

-- 3.5 库存表 (inventory)
CREATE TABLE inventory (
    inventory_id INT PRIMARY KEY AUTO_INCREMENT COMMENT '库存ID',
    goods_id INT NOT NULL UNIQUE COMMENT '商品ID',
    stock_num INT DEFAULT 0 COMMENT '库存数量(仓库)',
    on_shelf_num INT DEFAULT 0 COMMENT '在架数量',
    stock_warning INT DEFAULT 10 COMMENT '库存警戒值',
    shelf_warning INT DEFAULT 5 COMMENT '在架警戒值',
    stock_status ENUM('sufficient', 'stock_shortage', 'shelf_shortage') DEFAULT 'sufficient' COMMENT '库存状态: sufficient-充足, stock_shortage-库存短缺, shelf_shortage-在架短缺',
    update_time DATETIME DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP COMMENT '更新时间',
    FOREIGN KEY (goods_id) REFERENCES goods(goods_id),
    INDEX idx_status (stock_status)
) ENGINE=InnoDB COMMENT='库存表';

-- 3.6 商品操作记录表 (goods_operation_log)
CREATE TABLE goods_operation_log (
    log_id INT PRIMARY KEY AUTO_INCREMENT COMMENT '日志ID',
    goods_id INT NOT NULL COMMENT '商品ID',
    operation_type VARCHAR(50) NOT NULL COMMENT '操作类型: on_shelf-上架, off_shelf-下架, move_shelf-移架, price_change-调价, discount_set-设置折扣',
    old_value VARCHAR(200) COMMENT '变更前值',
    new_value VARCHAR(200) COMMENT '变更后值',
    operator_id INT COMMENT '操作人ID',
    operation_time DATETIME DEFAULT CURRENT_TIMESTAMP COMMENT '操作时间',
    remark VARCHAR(200) COMMENT '备注',
    FOREIGN KEY (goods_id) REFERENCES goods(goods_id),
    FOREIGN KEY (operator_id) REFERENCES sys_user(user_id)
) ENGINE=InnoDB COMMENT='商品操作记录表';

-- =====================================================
-- 四、订单与收银模块
-- =====================================================

-- 4.1 订单表 (order_info)
CREATE TABLE order_info (
    order_id INT PRIMARY KEY AUTO_INCREMENT COMMENT '订单ID',
    order_no VARCHAR(30) NOT NULL UNIQUE COMMENT '订单号',
    member_id INT COMMENT '会员ID(非会员为空)',
    cashier_id INT NOT NULL COMMENT '收银员ID',
    total_amount DECIMAL(12,2) NOT NULL COMMENT '订单总金额',
    discount_amount DECIMAL(12,2) DEFAULT 0 COMMENT '折扣金额',
    actual_amount DECIMAL(12,2) NOT NULL COMMENT '实付金额',
    points_earned INT DEFAULT 0 COMMENT '本单获得积分',
    points_used INT DEFAULT 0 COMMENT '本单使用积分',
    order_status ENUM('pending_pay', 'hanged', 'completed', 'cancelled', 'full_returned', 'part_returned') DEFAULT 'pending_pay' COMMENT '订单状态: pending_pay-待结账, hanged-挂单中, completed-已完成, cancelled-已撤销, full_returned-已整单退货, part_returned-部分退货',
    create_time DATETIME DEFAULT CURRENT_TIMESTAMP COMMENT '创建时间',
    complete_time DATETIME COMMENT '完成时间',
    FOREIGN KEY (member_id) REFERENCES member(member_id),
    FOREIGN KEY (cashier_id) REFERENCES sys_user(user_id),
    INDEX idx_order_no (order_no),
    INDEX idx_member (member_id),
    INDEX idx_status (order_status),
    INDEX idx_create_time (create_time)
) ENGINE=InnoDB COMMENT='订单表';

-- 4.2 订单明细表 (order_detail)
CREATE TABLE order_detail (
    detail_id INT PRIMARY KEY AUTO_INCREMENT COMMENT '明细ID',
    order_id INT NOT NULL COMMENT '订单ID',
    goods_id INT NOT NULL COMMENT '商品ID',
    goods_name VARCHAR(100) NOT NULL COMMENT '商品名称(冗余)',
    barcode VARCHAR(50) NOT NULL COMMENT '商品条码(冗余)',
    unit_price DECIMAL(10,2) NOT NULL COMMENT '单价',
    quantity DECIMAL(10,3) NOT NULL COMMENT '数量/重量',
    discount DECIMAL(3,2) DEFAULT 1.00 COMMENT '折扣',
    subtotal DECIMAL(12,2) NOT NULL COMMENT '小计金额',
    is_returned TINYINT DEFAULT 0 COMMENT '是否已退货: 0-否, 1-是',
    returned_quantity DECIMAL(10,3) DEFAULT 0 COMMENT '已退货数量',
    FOREIGN KEY (order_id) REFERENCES order_info(order_id),
    FOREIGN KEY (goods_id) REFERENCES goods(goods_id),
    INDEX idx_order (order_id)
) ENGINE=InnoDB COMMENT='订单明细表';

-- 4.3 支付记录表 (payment_record)
CREATE TABLE payment_record (
    payment_id INT PRIMARY KEY AUTO_INCREMENT COMMENT '支付ID',
    order_id INT NOT NULL COMMENT '订单ID',
    payment_type ENUM('cash', 'bank_card', 'coupon', 'points') NOT NULL COMMENT '支付方式: cash-现金, bank_card-银行卡, coupon-赠券, points-积分',
    amount DECIMAL(12,2) NOT NULL COMMENT '支付金额',
    transaction_type ENUM('pay', 'refund') DEFAULT 'pay' COMMENT '交易类型: pay-支付, refund-退款',
    payment_time DATETIME DEFAULT CURRENT_TIMESTAMP COMMENT '支付时间',
    FOREIGN KEY (order_id) REFERENCES order_info(order_id),
    INDEX idx_order (order_id)
) ENGINE=InnoDB COMMENT='支付记录表';

-- =====================================================
-- 五、退货管理模块
-- =====================================================

-- 5.1 退货记录表 (return_record)
CREATE TABLE return_record (
    return_id INT PRIMARY KEY AUTO_INCREMENT COMMENT '退货ID',
    return_no VARCHAR(30) NOT NULL UNIQUE COMMENT '退货单号',
    order_id INT NOT NULL COMMENT '原订单ID',
    return_type ENUM('full', 'part') NOT NULL COMMENT '退货类型: full-整单退货, part-部分退货',
    refund_amount DECIMAL(12,2) NOT NULL COMMENT '退款金额',
    points_deducted INT DEFAULT 0 COMMENT '扣减积分',
    return_reason ENUM('quality_issue', 'no_reason_7day', 'spec_mismatch', 'damaged', 'other') NOT NULL COMMENT '退货原因: quality_issue-质量问题, no_reason_7day-7天无理由, spec_mismatch-规格不符, damaged-损坏, other-其他',
    reason_detail VARCHAR(500) COMMENT '原因详情/质量问题描述',
    quality_photo VARCHAR(500) COMMENT '质量问题照片路径',
    operator_id INT NOT NULL COMMENT '售后管理员ID',
    return_status ENUM('pending', 'completed', 'rejected') DEFAULT 'completed' COMMENT '退货状态',
    create_time DATETIME DEFAULT CURRENT_TIMESTAMP COMMENT '退货时间',
    FOREIGN KEY (order_id) REFERENCES order_info(order_id),
    FOREIGN KEY (operator_id) REFERENCES sys_user(user_id),
    INDEX idx_return_no (return_no),
    INDEX idx_order (order_id)
) ENGINE=InnoDB COMMENT='退货记录表';

-- 5.2 退货明细表 (return_detail)
CREATE TABLE return_detail (
    detail_id INT PRIMARY KEY AUTO_INCREMENT COMMENT '明细ID',
    return_id INT NOT NULL COMMENT '退货ID',
    order_detail_id INT NOT NULL COMMENT '原订单明细ID',
    goods_id INT NOT NULL COMMENT '商品ID',
    return_quantity DECIMAL(10,3) NOT NULL COMMENT '退货数量',
    refund_amount DECIMAL(12,2) NOT NULL COMMENT '退款金额',
    return_reason ENUM('quality_issue', 'no_reason_7day', 'spec_mismatch', 'damaged', 'other') NOT NULL COMMENT '退货原因',
    goods_status ENUM('to_stock', 'pending_inspect', 'off_shelf', 'repaired') DEFAULT 'to_stock' COMMENT '商品去向: to_stock-转入库存, pending_inspect-待质检, off_shelf-已下架, repaired-修缮后上架',
    FOREIGN KEY (return_id) REFERENCES return_record(return_id),
    FOREIGN KEY (order_detail_id) REFERENCES order_detail(detail_id),
    FOREIGN KEY (goods_id) REFERENCES goods(goods_id),
    INDEX idx_return (return_id)
) ENGINE=InnoDB COMMENT='退货明细表';

-- 5.3 质量问题反馈表 (quality_feedback)
CREATE TABLE quality_feedback (
    feedback_id INT PRIMARY KEY AUTO_INCREMENT COMMENT '反馈ID',
    return_id INT NOT NULL COMMENT '退货ID',
    goods_id INT NOT NULL COMMENT '商品ID',
    barcode VARCHAR(50) NOT NULL COMMENT '商品条码',
    problem_desc VARCHAR(500) COMMENT '问题描述',
    photo_path VARCHAR(500) COMMENT '问题照片路径',
    feedback_status ENUM('pending', 'processing', 'completed') DEFAULT 'pending' COMMENT '反馈状态: pending-待处理, processing-处理中, completed-已完成',
    handle_result ENUM('batch_off_shelf', 'single_off_shelf', 'repair', 'no_action') COMMENT '处理结果: batch_off_shelf-批量下架, single_off_shelf-单个下架, repair-修缮, no_action-无需处理',
    handle_remark VARCHAR(500) COMMENT '处理备注',
    handler_id INT COMMENT '处理人(商品管理员)ID',
    create_time DATETIME DEFAULT CURRENT_TIMESTAMP COMMENT '创建时间',
    handle_time DATETIME COMMENT '处理时间',
    last_remind_time DATETIME COMMENT '上次提醒时间',
    FOREIGN KEY (return_id) REFERENCES return_record(return_id),
    FOREIGN KEY (goods_id) REFERENCES goods(goods_id),
    FOREIGN KEY (handler_id) REFERENCES sys_user(user_id),
    INDEX idx_status (feedback_status)
) ENGINE=InnoDB COMMENT='质量问题反馈表';

-- =====================================================
-- 六、积分兑换模块
-- =====================================================

-- 6.1 礼品表 (gift)
CREATE TABLE gift (
    gift_id INT PRIMARY KEY AUTO_INCREMENT COMMENT '礼品ID',
    gift_name VARCHAR(100) NOT NULL COMMENT '礼品名称',
    gift_desc VARCHAR(500) COMMENT '礼品描述',
    points_required INT NOT NULL COMMENT '所需积分',
    stock_num INT DEFAULT 0 COMMENT '库存数量',
    status ENUM('active', 'inactive') DEFAULT 'active' COMMENT '状态: active-可兑换, inactive-已下架',
    create_time DATETIME DEFAULT CURRENT_TIMESTAMP COMMENT '创建时间',
    update_time DATETIME DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP COMMENT '更新时间'
) ENGINE=InnoDB COMMENT='礼品表';

-- 6.2 积分兑换记录表 (points_exchange_record)
CREATE TABLE points_exchange_record (
    record_id INT PRIMARY KEY AUTO_INCREMENT COMMENT '记录ID',
    member_id INT NOT NULL COMMENT '会员ID',
    exchange_type ENUM('gift', 'cash') NOT NULL COMMENT '兑换类型: gift-礼品, cash-抵扣现金',
    gift_id INT COMMENT '礼品ID(兑换礼品时)',
    points_used INT NOT NULL COMMENT '使用积分',
    cash_amount DECIMAL(10,2) COMMENT '抵扣金额(抵扣现金时)',
    order_id INT COMMENT '关联订单ID(抵扣现金时)',
    operator_id INT COMMENT '操作人ID',
    exchange_time DATETIME DEFAULT CURRENT_TIMESTAMP COMMENT '兑换时间',
    FOREIGN KEY (member_id) REFERENCES member(member_id),
    FOREIGN KEY (gift_id) REFERENCES gift(gift_id),
    FOREIGN KEY (order_id) REFERENCES order_info(order_id),
    FOREIGN KEY (operator_id) REFERENCES sys_user(user_id),
    INDEX idx_member (member_id)
) ENGINE=InnoDB COMMENT='积分兑换记录表';

-- =====================================================
-- 七、商品入库模块
-- =====================================================

-- 7.1 入库记录表 (stock_in_record)
CREATE TABLE stock_in_record (
    record_id INT PRIMARY KEY AUTO_INCREMENT COMMENT '入库记录ID',
    goods_id INT NOT NULL COMMENT '商品ID',
    quantity INT NOT NULL COMMENT '入库数量',
    batch_no VARCHAR(50) COMMENT '批次号',
    supplier VARCHAR(100) COMMENT '供应商',
    cost_price DECIMAL(10,2) COMMENT '进货价',
    operator_id INT NOT NULL COMMENT '操作人ID',
    create_time DATETIME DEFAULT CURRENT_TIMESTAMP COMMENT '入库时间',
    remark VARCHAR(200) COMMENT '备注',
    FOREIGN KEY (goods_id) REFERENCES goods(goods_id),
    FOREIGN KEY (operator_id) REFERENCES sys_user(user_id),
    INDEX idx_goods (goods_id),
    INDEX idx_create_time (create_time)
) ENGINE=InnoDB COMMENT='入库记录表';

-- =====================================================
-- 八、系统通知模块
-- =====================================================

-- 8.1 系统通知表 (sys_notification)
CREATE TABLE sys_notification (
    notification_id INT PRIMARY KEY AUTO_INCREMENT COMMENT '通知ID',
    target_user_id INT COMMENT '目标用户ID(空表示广播)',
    target_role ENUM('admin', 'cashier', 'goods_manager', 'after_sale') COMMENT '目标角色',
    notification_type VARCHAR(50) NOT NULL COMMENT '通知类型: stock_warning-库存预警, quality_feedback-质量反馈, member_upgrade-会员升级, member_downgrade-会员降级',
    title VARCHAR(100) NOT NULL COMMENT '通知标题',
    content TEXT COMMENT '通知内容',
    related_id INT COMMENT '关联业务ID',
    is_read TINYINT DEFAULT 0 COMMENT '是否已读: 0-未读, 1-已读',
    create_time DATETIME DEFAULT CURRENT_TIMESTAMP COMMENT '创建时间',
    read_time DATETIME COMMENT '阅读时间',
    FOREIGN KEY (target_user_id) REFERENCES sys_user(user_id),
    INDEX idx_target_user (target_user_id),
    INDEX idx_is_read (is_read)
) ENGINE=InnoDB COMMENT='系统通知表';

-- =====================================================
-- 初始化数据
-- =====================================================

-- 初始化会员等级规则
INSERT INTO member_level_rule (level_name, level_code, min_consume, min_points, discount_rate, points_rate) VALUES
('普通会员', 'normal', 0, 0, 1.00, 1),
('银卡会员', 'silver', 1000, 1000, 0.95, 2),
('金卡会员', 'gold', 5000, 5000, 0.90, 3);

-- 初始化管理员账号 (密码: admin123 的MD5)
INSERT INTO sys_user (username, password, real_name, role, status) VALUES
('admin', 'e10adc3949ba59abbe56e057f20f883e', '系统管理员', 'admin', 'active');

-- =====================================================
-- 九、视图创建
-- =====================================================

-- 9.1 收银员视图

-- 在架商品视图
CREATE VIEW v_goods_on_sale AS
SELECT g.goods_id, g.barcode, g.goods_name, g.price, g.discount, 
       g.discount_start, g.discount_end, g.unit, g.is_weighted,
       i.on_shelf_num, gc.category_name
FROM goods g
JOIN inventory i ON g.goods_id = i.goods_id
JOIN goods_category gc ON g.category_id = gc.category_id
WHERE g.shelf_status = 'on_shelf' AND i.on_shelf_num > 0;

-- 会员信息视图
CREATE VIEW v_member_info AS
SELECT m.member_id, m.card_no, m.name, m.phone, m.level_code,
       m.total_points, mlr.discount_rate, mlr.points_rate
FROM member m
JOIN member_level_rule mlr ON m.level_code = mlr.level_code
WHERE m.status = 'active';

-- 挂单订单视图
CREATE VIEW v_hanged_orders AS
SELECT o.order_id, o.order_no, o.total_amount, o.create_time,
       m.card_no AS member_card, m.name AS member_name
FROM order_info o
LEFT JOIN member m ON o.member_id = m.member_id
WHERE o.order_status = 'hanged';

-- 9.2 商品管理员视图

-- 库存预警视图
CREATE VIEW v_inventory_warning AS
SELECT g.goods_id, g.barcode, g.goods_name, g.shelf_status,
       i.stock_num, i.on_shelf_num, i.stock_warning, i.shelf_warning, i.stock_status,
       s.shelf_code, gc.category_name
FROM goods g
JOIN inventory i ON g.goods_id = i.goods_id
LEFT JOIN shelf s ON g.shelf_id = s.shelf_id
JOIN goods_category gc ON g.category_id = gc.category_id
WHERE i.stock_status IN ('stock_shortage', 'shelf_shortage');

-- 待处理质量反馈视图
CREATE VIEW v_pending_quality_feedback AS
SELECT qf.feedback_id, qf.barcode, qf.problem_desc, qf.photo_path,
       qf.create_time, qf.last_remind_time,
       g.goods_name, rr.return_no
FROM quality_feedback qf
JOIN goods g ON qf.goods_id = g.goods_id
JOIN return_record rr ON qf.return_id = rr.return_id
WHERE qf.feedback_status = 'pending';

-- 商品分类树视图
CREATE VIEW v_category_tree AS
SELECT c1.category_id, c1.category_name,
       c1.level, c1.parent_id,
       c2.category_name AS parent_name
FROM goods_category c1
LEFT JOIN goods_category c2 ON c1.parent_id = c2.category_id
WHERE c1.delete_flag = 0;

-- 9.3 售后管理员视图

-- 可退货订单视图
CREATE VIEW v_returnable_orders AS
SELECT o.order_id, o.order_no, o.member_id, o.total_amount, 
       o.actual_amount, o.create_time, o.complete_time,
       m.card_no, m.name AS member_name, m.phone
FROM order_info o
LEFT JOIN member m ON o.member_id = m.member_id
WHERE o.order_status = 'completed' 
  AND o.complete_time >= DATE_SUB(NOW(), INTERVAL 7 DAY);

-- 退货记录汇总视图
CREATE VIEW v_return_summary AS
SELECT rr.return_id, rr.return_no, rr.return_type, rr.refund_amount,
       rr.return_reason, rr.create_time,
       o.order_no, m.card_no, m.name AS member_name,
       u.real_name AS operator_name
FROM return_record rr
JOIN order_info o ON rr.order_id = o.order_id
LEFT JOIN member m ON o.member_id = m.member_id
JOIN sys_user u ON rr.operator_id = u.user_id;

-- 9.4 统计报表视图

-- 每日销售汇总视图
CREATE VIEW v_daily_sales AS
SELECT DATE(create_time) AS sale_date,
       COUNT(*) AS order_count,
       SUM(total_amount) AS total_sales,
       SUM(discount_amount) AS total_discount,
       SUM(actual_amount) AS actual_sales
FROM order_info
WHERE order_status = 'completed'
GROUP BY DATE(create_time);

-- 商品销售排行视图
CREATE VIEW v_goods_sales_rank AS
SELECT g.goods_id, g.barcode, g.goods_name, gc.category_name,
       SUM(od.quantity) AS total_quantity,
       SUM(od.subtotal) AS total_amount
FROM order_detail od
JOIN goods g ON od.goods_id = g.goods_id
JOIN goods_category gc ON g.category_id = gc.category_id
JOIN order_info o ON od.order_id = o.order_id
WHERE o.order_status = 'completed'
GROUP BY g.goods_id, g.barcode, g.goods_name, gc.category_name;

-- 会员消费排行视图
CREATE VIEW v_member_consume_rank AS
SELECT m.member_id, m.card_no, m.name, m.level_code,
       m.total_consume, m.total_points,
       COUNT(o.order_id) AS order_count
FROM member m
LEFT JOIN order_info o ON m.member_id = o.member_id AND o.order_status = 'completed'
GROUP BY m.member_id, m.card_no, m.name, m.level_code, m.total_consume, m.total_points;

-- =====================================================
-- 十、数据库用户与权限（需要root权限执行）
-- =====================================================

-- 注意：以下SQL需要使用root用户执行
-- 如果不需要多用户权限控制，可以跳过此部分

/*
-- 创建数据库用户
CREATE USER 'sm_admin'@'localhost' IDENTIFIED BY 'admin_password';
CREATE USER 'sm_cashier'@'localhost' IDENTIFIED BY 'cashier_password';
CREATE USER 'sm_goods_manager'@'localhost' IDENTIFIED BY 'goods_password';
CREATE USER 'sm_after_sale'@'localhost' IDENTIFIED BY 'aftersale_password';

-- 系统管理员：所有权限
GRANT ALL PRIVILEGES ON supermarket_db.* TO 'sm_admin'@'localhost';

-- 收银员权限
GRANT SELECT ON supermarket_db.member TO 'sm_cashier'@'localhost';
GRANT SELECT ON supermarket_db.member_level_rule TO 'sm_cashier'@'localhost';
GRANT SELECT ON supermarket_db.goods TO 'sm_cashier'@'localhost';
GRANT SELECT ON supermarket_db.inventory TO 'sm_cashier'@'localhost';
GRANT SELECT, INSERT, UPDATE ON supermarket_db.order_info TO 'sm_cashier'@'localhost';
GRANT SELECT, INSERT ON supermarket_db.order_detail TO 'sm_cashier'@'localhost';
GRANT SELECT, INSERT ON supermarket_db.payment_record TO 'sm_cashier'@'localhost';
GRANT UPDATE (total_consume, total_points) ON supermarket_db.member TO 'sm_cashier'@'localhost';
GRANT UPDATE (on_shelf_num, stock_status) ON supermarket_db.inventory TO 'sm_cashier'@'localhost';
GRANT INSERT ON supermarket_db.member_change_log TO 'sm_cashier'@'localhost';
GRANT SELECT ON supermarket_db.v_goods_on_sale TO 'sm_cashier'@'localhost';
GRANT SELECT ON supermarket_db.v_member_info TO 'sm_cashier'@'localhost';
GRANT SELECT ON supermarket_db.v_hanged_orders TO 'sm_cashier'@'localhost';

-- 商品管理员权限
GRANT SELECT, INSERT, UPDATE ON supermarket_db.goods_category TO 'sm_goods_manager'@'localhost';
GRANT SELECT, INSERT ON supermarket_db.shelf_area TO 'sm_goods_manager'@'localhost';
GRANT SELECT, INSERT ON supermarket_db.shelf TO 'sm_goods_manager'@'localhost';
GRANT SELECT, INSERT, UPDATE ON supermarket_db.goods TO 'sm_goods_manager'@'localhost';
GRANT SELECT, INSERT, UPDATE ON supermarket_db.inventory TO 'sm_goods_manager'@'localhost';
GRANT SELECT, INSERT ON supermarket_db.goods_operation_log TO 'sm_goods_manager'@'localhost';
GRANT SELECT, INSERT ON supermarket_db.stock_in_record TO 'sm_goods_manager'@'localhost';
GRANT SELECT, UPDATE ON supermarket_db.quality_feedback TO 'sm_goods_manager'@'localhost';
GRANT SELECT ON supermarket_db.sys_notification TO 'sm_goods_manager'@'localhost';
GRANT SELECT ON supermarket_db.v_inventory_warning TO 'sm_goods_manager'@'localhost';
GRANT SELECT ON supermarket_db.v_pending_quality_feedback TO 'sm_goods_manager'@'localhost';
GRANT SELECT ON supermarket_db.v_category_tree TO 'sm_goods_manager'@'localhost';

-- 售后管理员权限
GRANT SELECT ON supermarket_db.member TO 'sm_after_sale'@'localhost';
GRANT SELECT ON supermarket_db.order_info TO 'sm_after_sale'@'localhost';
GRANT SELECT ON supermarket_db.order_detail TO 'sm_after_sale'@'localhost';
GRANT SELECT ON supermarket_db.payment_record TO 'sm_after_sale'@'localhost';
GRANT SELECT ON supermarket_db.goods TO 'sm_after_sale'@'localhost';
GRANT SELECT, INSERT ON supermarket_db.return_record TO 'sm_after_sale'@'localhost';
GRANT SELECT, INSERT ON supermarket_db.return_detail TO 'sm_after_sale'@'localhost';
GRANT SELECT, INSERT ON supermarket_db.quality_feedback TO 'sm_after_sale'@'localhost';
GRANT INSERT ON supermarket_db.payment_record TO 'sm_after_sale'@'localhost';
GRANT UPDATE (order_status) ON supermarket_db.order_info TO 'sm_after_sale'@'localhost';
GRANT UPDATE (is_returned, returned_quantity) ON supermarket_db.order_detail TO 'sm_after_sale'@'localhost';
GRANT UPDATE (total_consume, total_points, level_code) ON supermarket_db.member TO 'sm_after_sale'@'localhost';
GRANT UPDATE (stock_num, on_shelf_num, stock_status) ON supermarket_db.inventory TO 'sm_after_sale'@'localhost';
GRANT INSERT ON supermarket_db.member_change_log TO 'sm_after_sale'@'localhost';
GRANT SELECT ON supermarket_db.v_returnable_orders TO 'sm_after_sale'@'localhost';
GRANT SELECT ON supermarket_db.v_return_summary TO 'sm_after_sale'@'localhost';

-- 统计视图权限
GRANT SELECT ON supermarket_db.v_daily_sales TO 'sm_admin'@'localhost';
GRANT SELECT ON supermarket_db.v_goods_sales_rank TO 'sm_admin'@'localhost';
GRANT SELECT ON supermarket_db.v_member_consume_rank TO 'sm_admin'@'localhost';

-- 刷新权限
FLUSH PRIVILEGES;
*/
