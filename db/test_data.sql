-- =====================================================
-- 超市前台销售系统 - 测试数据
-- 执行前请先执行 schema.sql 创建表结构
-- =====================================================

USE supermarket_db;

-- =====================================================
-- 0. 清理已有测试数据（按外键依赖顺序删除）
-- =====================================================
SET FOREIGN_KEY_CHECKS = 0;

-- 使用 TRUNCATE 或 DELETE，忽略不存在的表
DELETE IGNORE FROM payment_record;
DELETE IGNORE FROM order_detail;
DELETE IGNORE FROM order_info;
DELETE IGNORE FROM gift;
DELETE IGNORE FROM member;
DELETE IGNORE FROM inventory;
DELETE IGNORE FROM goods;
DELETE IGNORE FROM shelf;
DELETE IGNORE FROM shelf_area;
DELETE IGNORE FROM goods_category;
DELETE FROM sys_user WHERE username != 'admin';

SET FOREIGN_KEY_CHECKS = 1;

-- =====================================================
-- 1. 系统用户数据
-- =====================================================
-- 密码都是 123456 (MD5: e10adc3949ba59abbe56e057f20f883e)

-- 先删除已有数据（如果存在）
DELETE FROM sys_user WHERE username IN ('cashier01', 'cashier02', 'goods01', 'aftersale01');

-- 更新admin用户
UPDATE sys_user SET real_name='系统管理员', phone='13800000001' WHERE username='admin';

-- 插入其他用户
INSERT INTO sys_user (username, password, real_name, phone, role, status) VALUES
('cashier01', 'e10adc3949ba59abbe56e057f20f883e', '张小红', '13800000002', 'cashier', 'active');
INSERT INTO sys_user (username, password, real_name, phone, role, status) VALUES
('cashier02', 'e10adc3949ba59abbe56e057f20f883e', '李小明', '13800000003', 'cashier', 'active');
INSERT INTO sys_user (username, password, real_name, phone, role, status) VALUES
('goods01', 'e10adc3949ba59abbe56e057f20f883e', '王大力', '13800000004', 'goods_manager', 'active');
INSERT INTO sys_user (username, password, real_name, phone, role, status) VALUES
('aftersale01', 'e10adc3949ba59abbe56e057f20f883e', '赵小芳', '13800000005', 'after_sale', 'active');

-- =====================================================
-- 2. 商品分类数据 (课-类-种 三级分类)
-- =====================================================

-- 一级分类（课）
INSERT INTO goods_category (category_id, category_name, parent_id, level, sort_order) VALUES
(1, '食品', NULL, 1, 1),
(2, '日用品', NULL, 1, 2),
(3, '饮料', NULL, 1, 3);

-- 二级分类（类）
INSERT INTO goods_category (category_id, category_name, parent_id, level, sort_order) VALUES
(11, '休闲零食', 1, 2, 1),
(12, '粮油调味', 1, 2, 2),
(13, '乳制品', 1, 2, 3),
(21, '洗护用品', 2, 2, 1),
(22, '纸品', 2, 2, 2),
(31, '碳酸饮料', 3, 2, 1),
(32, '果汁饮料', 3, 2, 2),
(33, '茶饮料', 3, 2, 3);

-- 三级分类（种）
INSERT INTO goods_category (category_id, category_name, parent_id, level, sort_order) VALUES
(111, '薯片', 11, 3, 1),
(112, '饼干', 11, 3, 2),
(113, '糖果', 11, 3, 3),
(121, '食用油', 12, 3, 1),
(122, '酱油', 12, 3, 2),
(131, '纯牛奶', 13, 3, 1),
(132, '酸奶', 13, 3, 2),
(211, '洗发水', 21, 3, 1),
(212, '沐浴露', 21, 3, 2),
(221, '卷纸', 22, 3, 1),
(222, '抽纸', 22, 3, 2),
(311, '可乐', 31, 3, 1),
(312, '雪碧', 31, 3, 2),
(321, '橙汁', 32, 3, 1),
(331, '绿茶', 33, 3, 1),
(332, '红茶', 33, 3, 2);

-- =====================================================
-- 3. 货架区域和货架数据
-- =====================================================

INSERT INTO shelf_area (area_id, area_code, area_name, description) VALUES
(1, 'A', '食品区', '各类食品'),
(2, 'B', '日用品区', '日常用品'),
(3, 'C', '饮料区', '各类饮料');

INSERT INTO shelf (shelf_id, area_id, shelf_code, shelf_no, layer_no, capacity) VALUES
(1, 1, 'A-01-01', '01', '01', 100),
(2, 1, 'A-01-02', '01', '02', 100),
(3, 1, 'A-02-01', '02', '01', 100),
(4, 2, 'B-01-01', '01', '01', 80),
(5, 2, 'B-01-02', '01', '02', 80),
(6, 3, 'C-01-01', '01', '01', 120),
(7, 3, 'C-01-02', '01', '02', 120);

-- =====================================================
-- 4. 商品数据
-- =====================================================

INSERT INTO goods (goods_id, barcode, goods_name, category_id, unit, is_weighted, price, cost_price, shelf_id, shelf_status, discount) VALUES
-- 薯片类
(1, '6901234567001', '乐事原味薯片75g', 111, '袋', 0, 8.50, 5.00, 1, 'on_shelf', 1.00),
(2, '6901234567002', '乐事黄瓜味薯片75g', 111, '袋', 0, 8.50, 5.00, 1, 'on_shelf', 1.00),
(3, '6901234567003', '品客原味薯片110g', 111, '罐', 0, 15.90, 10.00, 1, 'on_shelf', 0.90),
-- 饼干类
(4, '6901234567004', '奥利奥原味夹心饼干97g', 112, '盒', 0, 9.90, 6.00, 1, 'on_shelf', 1.00),
(5, '6901234567005', '好丽友派6枚装', 112, '盒', 0, 12.80, 8.00, 1, 'on_shelf', 1.00),
-- 糖果类
(6, '6901234567006', '阿尔卑斯棒棒糖10支', 113, '袋', 0, 6.50, 4.00, 2, 'on_shelf', 1.00),
(7, '6901234567007', '徐福记酥心糖500g', 113, '袋', 0, 25.90, 18.00, 2, 'on_shelf', 1.00),
-- 食用油
(8, '6901234567008', '金龙鱼调和油5L', 121, '桶', 0, 69.90, 55.00, 3, 'on_shelf', 1.00),
(9, '6901234567009', '鲁花花生油1.8L', 121, '桶', 0, 79.90, 65.00, 3, 'on_shelf', 1.00),
-- 酱油
(10, '6901234567010', '海天生抽500ml', 122, '瓶', 0, 12.90, 8.00, 3, 'on_shelf', 1.00),
(11, '6901234567011', '李锦记蒸鱼豉油750ml', 122, '瓶', 0, 18.50, 12.00, 3, 'on_shelf', 1.00),
-- 纯牛奶
(12, '6901234567012', '伊利纯牛奶250ml*12', 131, '箱', 0, 45.00, 35.00, 2, 'on_shelf', 1.00),
(13, '6901234567013', '蒙牛纯牛奶250ml*16', 131, '箱', 0, 55.00, 42.00, 2, 'on_shelf', 1.00),
-- 酸奶
(14, '6901234567014', '安慕希原味酸奶205g*12', 132, '箱', 0, 65.00, 50.00, 2, 'on_shelf', 1.00),
(15, '6901234567015', '莫斯利安原味酸奶200g*6', 132, '组', 0, 35.00, 26.00, 2, 'on_shelf', 1.00),
-- 洗发水
(16, '6901234567016', '海飞丝去屑洗发水400ml', 211, '瓶', 0, 39.90, 28.00, 4, 'on_shelf', 1.00),
(17, '6901234567017', '潘婷乳液修护洗发水500ml', 211, '瓶', 0, 45.90, 32.00, 4, 'on_shelf', 1.00),
-- 沐浴露
(18, '6901234567018', '力士沐浴露500ml', 212, '瓶', 0, 29.90, 20.00, 4, 'on_shelf', 1.00),
(19, '6901234567019', '舒肤佳沐浴露720ml', 212, '瓶', 0, 35.90, 25.00, 4, 'on_shelf', 1.00),
-- 卷纸
(20, '6901234567020', '维达卷纸10卷装', 221, '提', 0, 25.90, 18.00, 5, 'on_shelf', 1.00),
(21, '6901234567021', '清风卷纸12卷装', 221, '提', 0, 29.90, 21.00, 5, 'on_shelf', 1.00),
-- 抽纸
(22, '6901234567022', '心相印抽纸3包装', 222, '组', 0, 15.90, 10.00, 5, 'on_shelf', 1.00),
(23, '6901234567023', '维达抽纸4包装', 222, '组', 0, 19.90, 13.00, 5, 'on_shelf', 1.00),
-- 可乐
(24, '6901234567024', '可口可乐500ml', 311, '瓶', 0, 3.50, 2.00, 6, 'on_shelf', 1.00),
(25, '6901234567025', '可口可乐2L', 311, '瓶', 0, 7.90, 5.00, 6, 'on_shelf', 1.00),
(26, '6901234567026', '百事可乐500ml', 311, '瓶', 0, 3.50, 2.00, 6, 'on_shelf', 1.00),
-- 雪碧
(27, '6901234567027', '雪碧500ml', 312, '瓶', 0, 3.50, 2.00, 6, 'on_shelf', 1.00),
(28, '6901234567028', '雪碧2L', 312, '瓶', 0, 7.90, 5.00, 6, 'on_shelf', 1.00),
-- 橙汁
(29, '6901234567029', '美汁源果粒橙450ml', 321, '瓶', 0, 4.50, 2.80, 7, 'on_shelf', 1.00),
(30, '6901234567030', '汇源100%橙汁1L', 321, '盒', 0, 12.90, 8.00, 7, 'on_shelf', 1.00),
-- 茶饮料
(31, '6901234567031', '康师傅绿茶500ml', 331, '瓶', 0, 3.50, 2.00, 7, 'on_shelf', 1.00),
(32, '6901234567032', '统一绿茶500ml', 331, '瓶', 0, 3.50, 2.00, 7, 'on_shelf', 1.00),
(33, '6901234567033', '康师傅冰红茶500ml', 332, '瓶', 0, 3.50, 2.00, 7, 'on_shelf', 1.00),
(34, '6901234567034', '统一冰红茶500ml', 332, '瓶', 0, 3.50, 2.00, 7, 'on_shelf', 1.00);

-- =====================================================
-- 5. 库存数据
-- =====================================================

INSERT INTO inventory (goods_id, stock_num, on_shelf_num, stock_warning, shelf_warning, stock_status) VALUES
(1, 100, 50, 20, 10, 'sufficient'),
(2, 15, 8, 20, 10, 'stock_shortage'),
(3, 60, 30, 15, 8, 'sufficient'),
(4, 90, 45, 20, 10, 'sufficient'),
(5, 10, 5, 15, 8, 'stock_shortage'),
(6, 120, 60, 25, 12, 'sufficient'),
(7, 50, 25, 15, 8, 'sufficient'),
(8, 5, 3, 10, 5, 'stock_shortage'),
(9, 25, 12, 10, 5, 'sufficient'),
(10, 80, 40, 20, 10, 'sufficient'),
(11, 60, 30, 15, 8, 'sufficient'),
(12, 40, 20, 15, 8, 'sufficient'),
(13, 35, 18, 15, 8, 'sufficient'),
(14, 30, 15, 12, 6, 'sufficient'),
(15, 45, 22, 15, 8, 'sufficient'),
(16, 50, 25, 15, 8, 'sufficient'),
(17, 40, 20, 12, 6, 'sufficient'),
(18, 55, 28, 15, 8, 'sufficient'),
(19, 45, 22, 15, 8, 'sufficient'),
(20, 60, 30, 20, 10, 'sufficient'),
(21, 50, 25, 18, 9, 'sufficient'),
(22, 80, 40, 25, 12, 'sufficient'),
(23, 70, 35, 22, 11, 'sufficient'),
(24, 200, 100, 50, 25, 'sufficient'),
(25, 80, 40, 25, 12, 'sufficient'),
(26, 180, 90, 50, 25, 'sufficient'),
(27, 190, 95, 50, 25, 'sufficient'),
(28, 75, 38, 25, 12, 'sufficient'),
(29, 150, 75, 40, 20, 'sufficient'),
(30, 60, 30, 20, 10, 'sufficient'),
(31, 160, 80, 45, 22, 'sufficient'),
(32, 140, 70, 40, 20, 'sufficient'),
(33, 155, 78, 45, 22, 'sufficient'),
(34, 145, 72, 40, 20, 'sufficient');

-- =====================================================
-- 6. 会员数据
-- =====================================================

INSERT INTO member (member_id, card_no, name, phone, address, level_code, total_consume, total_points, status) VALUES
(1, 'VIP10000001', '张三', '13912345001', '北京市朝阳区xxx小区1号楼', 'gold', 8500.00, 8500, 'active'),
(2, 'VIP10000002', '李四', '13912345002', '北京市海淀区xxx大厦', 'silver', 2300.00, 2300, 'active'),
(3, 'VIP10000003', '王五', '13912345003', '北京市西城区xxx街道', 'silver', 1500.00, 1500, 'active'),
(4, 'VIP10000004', '赵六', '13912345004', '北京市东城区xxx胡同', 'normal', 680.00, 680, 'active'),
(5, 'VIP10000005', '钱七', '13912345005', '北京市丰台区xxx路', 'normal', 320.00, 320, 'active'),
(6, 'VIP10000006', '孙八', '13912345006', '北京市通州区xxx园', 'normal', 150.00, 150, 'active'),
(7, 'VIP10000007', '周九', '13912345007', '北京市大兴区xxx村', 'normal', 50.00, 50, 'active'),
(8, 'VIP10000008', '吴十', '13912345008', '北京市昌平区xxx镇', 'gold', 6200.00, 6200, 'active'),
(9, 'VIP10000009', '郑十一', '13912345009', '北京市顺义区xxx街', 'silver', 1800.00, 1800, 'active'),
(10, 'VIP10000010', '王小明', '13912345010', '北京市房山区xxx路', 'normal', 420.00, 420, 'active');

-- =====================================================
-- 7. 历史订单数据 (已完成订单，用于测试退货)
-- =====================================================

-- 订单1: 金卡会员张三的订单
INSERT INTO order_info (order_id, order_no, member_id, cashier_id, total_amount, discount_amount, actual_amount, points_earned, order_status, create_time, complete_time) VALUES
(1, 'ORD20260105100001', 1, 11, 156.30, 15.63, 140.67, 140, 'completed', '2026-01-05 10:30:00', '2026-01-05 10:32:00');

INSERT INTO order_detail (order_id, goods_id, goods_name, barcode, unit_price, quantity, discount, subtotal, is_returned, returned_quantity) VALUES
(1, 1, '乐事原味薯片75g', '6901234567001', 8.50, 2, 1.00, 17.00, 0, 0),
(1, 12, '伊利纯牛奶250ml*12', '6901234567012', 45.00, 2, 1.00, 90.00, 0, 0),
(1, 24, '可口可乐500ml', '6901234567024', 3.50, 6, 1.00, 21.00, 0, 0),
(1, 22, '心相印抽纸3包装', '6901234567022', 15.90, 1, 1.00, 15.90, 0, 0),
(1, 10, '海天生抽500ml', '6901234567010', 12.90, 1, 0.90, 11.61, 0, 0);

-- 订单2: 银卡会员李四的订单
INSERT INTO order_info (order_id, order_no, member_id, cashier_id, total_amount, discount_amount, actual_amount, points_earned, order_status, create_time, complete_time) VALUES
(2, 'ORD20260105110002', 2, 11, 89.70, 4.49, 85.21, 85, 'completed', '2026-01-05 11:15:00', '2026-01-05 11:18:00');

INSERT INTO order_detail (order_id, goods_id, goods_name, barcode, unit_price, quantity, discount, subtotal, is_returned, returned_quantity) VALUES
(2, 16, '海飞丝去屑洗发水400ml', '6901234567016', 39.90, 1, 1.00, 39.90, 0, 0),
(2, 18, '力士沐浴露500ml', '6901234567018', 29.90, 1, 1.00, 29.90, 0, 0),
(2, 6, '阿尔卑斯棒棒糖10支', '6901234567006', 6.50, 2, 1.00, 13.00, 0, 0),
(2, 31, '康师傅绿茶500ml', '6901234567031', 3.50, 2, 0.95, 6.65, 0, 0);

-- 订单3: 普通会员赵六的订单
INSERT INTO order_info (order_id, order_no, member_id, cashier_id, total_amount, discount_amount, actual_amount, points_earned, order_status, create_time, complete_time) VALUES
(3, 'ORD20260105140003', 4, 12, 52.30, 0, 52.30, 52, 'completed', '2026-01-05 14:20:00', '2026-01-05 14:22:00');

INSERT INTO order_detail (order_id, goods_id, goods_name, barcode, unit_price, quantity, discount, subtotal, is_returned, returned_quantity) VALUES
(3, 4, '奥利奥原味夹心饼干97g', '6901234567004', 9.90, 2, 1.00, 19.80, 0, 0),
(3, 29, '美汁源果粒橙450ml', '6901234567029', 4.50, 3, 1.00, 13.50, 0, 0),
(3, 20, '维达卷纸10卷装', '6901234567020', 25.90, 1, 0.90, 23.31, 0, 0);

-- 订单4: 非会员订单
INSERT INTO order_info (order_id, order_no, member_id, cashier_id, total_amount, discount_amount, actual_amount, points_earned, order_status, create_time, complete_time) VALUES
(4, 'ORD20260105160004', NULL, 11, 35.00, 0, 35.00, 0, 'completed', '2026-01-05 16:45:00', '2026-01-05 16:47:00');

INSERT INTO order_detail (order_id, goods_id, goods_name, barcode, unit_price, quantity, discount, subtotal, is_returned, returned_quantity) VALUES
(4, 24, '可口可乐500ml', '6901234567024', 3.50, 4, 1.00, 14.00, 0, 0),
(4, 27, '雪碧500ml', '6901234567027', 3.50, 2, 1.00, 7.00, 0, 0),
(4, 33, '康师傅冰红茶500ml', '6901234567033', 3.50, 4, 1.00, 14.00, 0, 0);

-- 订单5: 今天的订单（用于测试退货）
INSERT INTO order_info (order_id, order_no, member_id, cashier_id, total_amount, discount_amount, actual_amount, points_earned, order_status, create_time, complete_time) VALUES
(5, 'ORD20260106090005', 1, 11, 198.50, 19.85, 178.65, 178, 'completed', '2026-01-06 09:30:00', '2026-01-06 09:33:00');

INSERT INTO order_detail (order_id, goods_id, goods_name, barcode, unit_price, quantity, discount, subtotal, is_returned, returned_quantity) VALUES
(5, 8, '金龙鱼调和油5L', '6901234567008', 69.90, 1, 1.00, 69.90, 0, 0),
(5, 14, '安慕希原味酸奶205g*12', '6901234567014', 65.00, 1, 1.00, 65.00, 0, 0),
(5, 3, '品客原味薯片110g', '6901234567003', 15.90, 2, 0.90, 28.62, 0, 0),
(5, 21, '清风卷纸12卷装', '6901234567021', 29.90, 1, 1.00, 29.90, 0, 0);

-- 订单6: 银卡会员的今日订单
INSERT INTO order_info (order_id, order_no, member_id, cashier_id, total_amount, discount_amount, actual_amount, points_earned, order_status, create_time, complete_time) VALUES
(6, 'ORD20260106103006', 3, 12, 125.80, 6.29, 119.51, 119, 'completed', '2026-01-06 10:30:00', '2026-01-06 10:33:00');

INSERT INTO order_detail (order_id, goods_id, goods_name, barcode, unit_price, quantity, discount, subtotal, is_returned, returned_quantity) VALUES
(6, 17, '潘婷乳液修护洗发水500ml', '6901234567017', 45.90, 1, 1.00, 45.90, 0, 0),
(6, 19, '舒肤佳沐浴露720ml', '6901234567019', 35.90, 1, 1.00, 35.90, 0, 0),
(6, 5, '好丽友派6枚装', '6901234567005', 12.80, 2, 1.00, 25.60, 0, 0),
(6, 32, '统一绿茶500ml', '6901234567032', 3.50, 4, 0.95, 13.30, 0, 0);

-- =====================================================
-- 8. 支付记录
-- =====================================================

INSERT INTO payment_record (order_id, payment_type, amount, transaction_type, payment_time) VALUES
(1, 'cash', 140.67, 'pay', '2026-01-05 10:32:00'),
(2, 'bank_card', 85.21, 'pay', '2026-01-05 11:18:00'),
(3, 'cash', 52.30, 'pay', '2026-01-05 14:22:00'),
(4, 'cash', 35.00, 'pay', '2026-01-05 16:47:00'),
(5, 'bank_card', 178.65, 'pay', '2026-01-06 09:33:00'),
(6, 'cash', 119.51, 'pay', '2026-01-06 10:33:00');

-- =====================================================
-- 9. 礼品数据（积分兑换）
-- =====================================================

INSERT INTO gift (gift_id, gift_name, gift_desc, points_required, stock_num, status) VALUES
(1, '精美雨伞', '高品质折叠雨伞', 500, 50, 'active'),
(2, '保温杯', '304不锈钢保温杯500ml', 800, 30, 'active'),
(3, '购物袋', '环保购物袋', 200, 100, 'active'),
(4, '毛巾套装', '纯棉毛巾3条装', 600, 40, 'active'),
(5, '电子秤', '家用厨房电子秤', 1500, 20, 'active');

-- =====================================================
-- 完成提示
-- =====================================================
SELECT '测试数据导入完成！' AS message;
SELECT '用户账号: admin/cashier01/cashier02/goods01/aftersale01' AS accounts;
SELECT '密码统一为: 123456' AS password;
SELECT '会员卡号: VIP10000001 ~ VIP10000010' AS member_cards;
