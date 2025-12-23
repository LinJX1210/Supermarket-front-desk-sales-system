# AI提示词模板

本文档为各组员提供与AI对话的提示词模板，帮助大家更高效地完成开发任务。

---

## 通用背景提示词（所有组员第一次对话时使用）

```
我正在开发一个"超市前台销售系统"课设项目，使用Python + CustomTkinter + MySQL技术栈。

项目结构：
- ui/ 目录存放界面代码
- logic/ 目录存放业务逻辑代码
- db/ 目录存放数据库相关代码
- utils/ 目录存放工具类

数据库连接使用 db/db_conn.py 中的 DBConnection 类，用法：
```python
from db.db_conn import DBConnection

with DBConnection() as db:
    db.execute("SELECT * FROM goods WHERE barcode = %s", (barcode,))
    result = db.fetchone()
```

界面使用 CustomTkinter 库，基本用法：
```python
import customtkinter as ctk

class MyUI(ctk.CTkFrame):
    def __init__(self, parent):
        super().__init__(parent)
        # 创建控件
        self.label = ctk.CTkLabel(self, text="标签")
        self.entry = ctk.CTkEntry(self, placeholder_text="输入框")
        self.button = ctk.CTkButton(self, text="按钮", command=self.on_click)
        # 布局
        self.label.pack(pady=10)
        self.entry.pack(pady=10)
        self.button.pack(pady=10)
    
    def on_click(self):
        pass
```

请基于以上背景帮我完成开发任务。
```

---

## 组员1（组长）提示词 - 收银管理 + 系统框架

### 任务1：开发主界面框架

```
我是组员1，负责收银管理和系统主界面。

请帮我完成 ui/main_ui.py 主界面开发，要求：
1. 左侧是功能导航栏，包含按钮：收银、商品管理、会员管理、退货管理、统计报表
2. 顶部显示当前登录用户名和退出按钮
3. 中间是内容区，点击左侧按钮时动态加载对应模块的界面
4. 根据登录用户的角色（admin/cashier/goods_manager/after_sale）显示不同的导航按钮
5. 窗口大小1200x800

数据库sys_user表结构：
- user_id: 用户ID
- username: 用户名
- password: 密码(MD5)
- real_name: 真实姓名
- role: 角色(admin/cashier/goods_manager/after_sale)
- status: 状态(active/disabled)
```

### 任务2：开发收银界面

```
请帮我完成 ui/cashier_ui.py 收银界面开发，要求：
1. 顶部：条码输入框 + 添加商品按钮
2. 左侧：商品列表（用Treeview显示：商品名、数量、单价、折扣、小计）
3. 右上：会员卡号输入框 + 查询按钮，显示会员姓名、等级、折扣
4. 右中：显示订单总金额、折扣金额、实付金额
5. 右下：支付方式选择（现金/银行卡/赠券）+ 金额输入框
6. 底部按钮：挂单、调单、撤单、结账

散装商品需要额外弹窗输入重量/数量。
```

### 任务3：开发收银结算逻辑

```
请帮我完成 logic/cashier_logic.py 收银结算逻辑，要求：

1. get_goods_by_barcode(barcode): 根据条码查询商品信息
   - 查询goods表，返回商品ID、名称、价格、是否散装、当前折扣
   - 检查商品状态必须是on_shelf，库存on_shelf_num > 0

2. calculate_order_total(order_items, member_id=None): 计算订单金额
   - order_items是列表，每项包含goods_id, quantity
   - 如果有member_id，查询会员折扣
   - 返回总金额、折扣金额、实付金额

3. checkout(order_data): 结账
   - 创建order_info记录，状态设为completed
   - 创建order_detail记录
   - 创建payment_record记录
   - 扣减inventory表的on_shelf_num
   - 如果是会员，累计消费金额和积分，检查是否升级
   - 使用事务保证数据一致性

相关表结构：
- order_info: order_id, order_no, member_id, cashier_id, total_amount, discount_amount, actual_amount, points_earned, order_status, create_time
- order_detail: detail_id, order_id, goods_id, goods_name, barcode, unit_price, quantity, discount, subtotal
- payment_record: payment_id, order_id, payment_type, amount, transaction_type
- inventory: inventory_id, goods_id, stock_num, on_shelf_num
```

### 任务4：开发挂单调单撤单逻辑

```
请帮我完成 logic/cashier_hang_cancel.py 挂单/调单/撤单逻辑：

1. hang_order(order_id): 挂单
   - 更新order_info状态为hanged

2. get_hanged_orders(cashier_id): 获取当前收银员的挂单列表
   - 查询order_status='hanged'的订单

3. recall_order(order_id): 调单
   - 更新order_info状态为pending_pay
   - 返回订单详情供继续结账

4. cancel_order(order_id): 撤单（未结账订单）
   - 更新order_info状态为cancelled
   - 不需要恢复库存（因为还没扣）

order_status枚举值：pending_pay, hanged, completed, cancelled, full_returned
```

### 任务5：开发小票打印功能

```
请帮我完成 utils/print_utils.py 小票打印功能：

1. generate_receipt(order_data): 生成小票内容
   - 包含：店名、订单号、时间、商品列表、总金额、折扣、实付、支付方式、会员信息
   - 返回格式化的字符串

2. print_receipt(content): 打印小票
   - 先保存为txt文件到receipts目录
   - 可选：调用系统打印机打印

3. generate_return_receipt(return_data): 生成退货凭证
   - 包含：退货单号、原订单号、退货商品、退款金额、退货原因

小票格式示例：
================================
      XX超市购物小票
================================
订单号：ORD20241219001
时间：2024-12-19 14:30:00
--------------------------------
商品名称      数量  单价  小计
雪饼           2   5.00  10.00
可乐           1   3.50   3.50
--------------------------------
合计：13.50元
会员折扣：-0.68元
实付：12.82元
支付方式：现金
--------------------------------
会员卡号：VIP00001
本次积分：+12
================================
      谢谢惠顾，欢迎再来
================================
```

---

## 组员2提示词 - 商品管理 + 库存管理

### 任务1：开发商品分类界面

```
我是组员2，负责商品管理和库存管理。

请帮我完成 ui/goods_category_ui.py 商品分类管理界面，要求：
1. 左侧用Treeview显示分类树（课-类-种三级结构）
2. 右侧显示选中分类的详情和编辑表单
3. 按钮：新增分类、修改分类、删除分类（软删除）
4. 新增时需要选择父分类和层级

数据库goods_category表结构：
- category_id: 分类ID
- category_name: 分类名称
- parent_id: 父分类ID（自关联）
- level: 层级(1-课, 2-类, 3-种)
- sort_order: 排序号
- delete_flag: 删除标记(0-正常, 1-已删除)
```

### 任务2：开发商品管理界面

```
请帮我完成 ui/goods_manage_ui.py 商品管理界面，要求：
1. 顶部：搜索框（按条码/名称搜索）+ 筛选下拉框（按状态/分类筛选）
2. 中间：商品列表Treeview（条码、名称、分类、价格、状态、货架位置、库存）
3. 右侧：商品详情编辑区
   - 基本信息：条码、名称、分类（下拉选择种级别）、单位、是否散装
   - 价格信息：售价、成本价、临时折扣、折扣时间
   - 货架信息：货架编码（区-架-层格式，如A-01-02）
4. 底部按钮：新增商品、上架、移架、下架、保存

商品状态shelf_status：pending_shelf(待上架), on_shelf(在架), off_shelf(已下架), pending_inspect(待质检), suspend_sale(暂停销售)
```

### 任务3：开发库存监控界面

```
请帮我完成 ui/inventory_monitor_ui.py 库存监控界面，要求：
1. 顶部：筛选条件（库存状态、分类）
2. 中间：库存列表Treeview
   - 列：商品名称、条码、库存数量、在架数量、库存警戒值、在架警戒值、状态
   - 状态用颜色标识：绿色=充足，红色=短缺
3. 右侧：选中商品的警戒值设置表单
4. 底部：补货按钮（从仓库补货到货架）

库存状态stock_status：sufficient(充足), stock_shortage(库存短缺), shelf_shortage(在架短缺)
```

### 任务4：开发商品分类逻辑

```
请帮我完成 logic/goods_category_logic.py 商品分类逻辑：

1. get_category_tree(): 获取分类树
   - 查询所有delete_flag=0的分类
   - 组装成树形结构返回

2. add_category(name, parent_id, level): 新增分类
   - 校验层级：level=1时parent_id必须为空，level=2/3时parent_id必须存在且父级level正确
   - 插入goods_category表

3. update_category(category_id, name): 修改分类名称
   - 更新category_name

4. delete_category(category_id): 删除分类（软删除）
   - 检查是否有子分类或关联商品
   - 更新delete_flag=1
```

### 任务5：开发商品管理逻辑

```
请帮我完成 logic/goods_manage_logic.py 商品管理逻辑：

1. add_goods(goods_data): 新增商品
   - 插入goods表，状态设为pending_shelf
   - 同时创建inventory记录，初始库存为0

2. on_shelf(goods_id, shelf_code, price): 上架
   - 更新goods表：shelf_status='on_shelf', shelf_id, price
   - 记录goods_operation_log

3. move_shelf(goods_id, new_shelf_code): 移架
   - 更新goods表的shelf_id
   - 记录goods_operation_log

4. off_shelf(goods_id, reason): 下架
   - 更新goods表：shelf_status='off_shelf', off_shelf_reason
   - 记录goods_operation_log

5. update_price(goods_id, new_price): 修改定价
   - 更新goods表的price
   - 记录goods_operation_log（记录旧价格和新价格）

6. set_discount(goods_id, discount, start_time, end_time): 设置临时折扣
   - 更新goods表的discount, discount_start, discount_end
   - 记录goods_operation_log
```

### 任务6：开发库存管理逻辑

```
请帮我完成 logic/inventory_logic.py 库存管理逻辑：

1. get_stock(goods_id): 查询库存
   - 返回stock_num, on_shelf_num, stock_warning, shelf_warning, stock_status

2. reduce_stock(goods_id, num): 扣减库存（收银时调用）
   - 扣减on_shelf_num
   - 检查是否低于警戒值，更新stock_status
   - 使用事务

3. restore_stock(goods_id, num): 恢复库存（退货时调用）
   - 增加on_shelf_num或stock_num（根据退货商品去向）
   - 更新stock_status

4. replenish_shelf(goods_id, num): 补货上架（从仓库到货架）
   - 减少stock_num，增加on_shelf_num
   - 检查库存是否低于警戒值

5. set_warning_value(goods_id, stock_warning, shelf_warning): 设置警戒值
   - 更新inventory表
   - 重新检查并更新stock_status
```

### 任务7：开发库存预警逻辑

```
请帮我完成 logic/inventory_warning.py 库存预警逻辑：

1. check_all_inventory(): 检查所有库存状态
   - 遍历inventory表
   - 对比stock_num和stock_warning，on_shelf_num和shelf_warning
   - 更新stock_status

2. get_shortage_goods(): 获取短缺商品列表
   - 查询stock_status不是sufficient的商品

3. send_warning_notification(goods_list): 发送库存预警通知
   - 向sys_notification表插入通知
   - target_role='goods_manager'
   - notification_type='stock_warning'
```

---

## 组员3提示词 - 会员管理 + 用户权限

### 任务1：开发用户管理界面

```
我是组员3，负责会员管理和用户权限。

请帮我完成 ui/user_manage_ui.py 用户管理界面，要求：
1. 顶部：搜索框 + 角色筛选下拉框
2. 中间：用户列表Treeview（用户名、真实姓名、角色、状态、创建时间）
3. 右侧：用户编辑表单
   - 用户名、密码、真实姓名、手机号
   - 角色下拉框：系统管理员/收银员/商品管理员/售后管理员
   - 状态：正常/禁用
4. 底部按钮：新增用户、保存、禁用用户

角色role枚举：admin, cashier, goods_manager, after_sale
状态status枚举：active, disabled
```

### 任务2：开发会员管理界面

```
请帮我完成 ui/member_manage_ui.py 会员管理界面，要求：
1. 顶部：搜索框（按卡号/手机号/姓名搜索）+ 等级筛选
2. 中间：会员列表Treeview（卡号、姓名、手机、等级、累计消费、当前积分、状态）
3. 右侧：会员详情
   - 基本信息：卡号（自动生成）、姓名、手机、地址
   - 会员信息：等级、累计消费、当前积分（只读）
   - 消费记录列表（最近10条）
4. 底部按钮：新增会员、保存、查看详细消费记录

会员等级level_code：normal(普通), silver(银卡), gold(金卡)
```

### 任务3：开发会员规则管理界面

```
请帮我完成 ui/member_rule_ui.py 会员规则管理界面，要求：
1. 等级规则设置区（表格形式）：
   - 列：等级名称、等级代码、升级所需消费、升级所需积分、折扣比例、积分比例
   - 三行：普通会员、银卡会员、金卡会员
   - 可编辑并保存
2. 积分规则说明区：
   - 显示当前积分规则（1元=X积分）
   - 积分抵扣规则（X积分=1元）

数据库member_level_rule表结构：
- rule_id, level_name, level_code
- min_consume: 升级所需最低累计消费
- min_points: 升级所需最低积分
- discount_rate: 折扣比例(0.95表示95折)
- points_rate: 积分比例(每消费1元获得积分数)
```

### 任务4：开发用户认证逻辑

```
请帮我完成 logic/user_auth_logic.py 用户认证逻辑：

1. login_auth(username, password): 登录认证
   - 查询sys_user表
   - 密码用MD5加密后比对
   - 检查status='active'
   - 返回用户信息或None

2. get_role_permission(role): 获取角色权限
   - 返回该角色可访问的模块列表
   - admin: 全部模块
   - cashier: 收银
   - goods_manager: 商品管理、库存管理
   - after_sale: 退货管理

3. change_password(user_id, old_password, new_password): 修改密码
   - 验证旧密码
   - 更新新密码（MD5加密）

密码加密示例：
import hashlib
md5_password = hashlib.md5(password.encode()).hexdigest()
```

### 任务5：开发用户管理逻辑

```
请帮我完成 logic/user_manage_logic.py 用户管理逻辑：

1. add_user(user_data): 新增用户
   - 检查用户名是否重复
   - 密码MD5加密
   - 插入sys_user表

2. update_user(user_id, user_data): 修改用户
   - 更新用户信息
   - 如果修改了密码，需要MD5加密

3. disable_user(user_id): 禁用用户
   - 更新status='disabled'
   - 不能禁用自己

4. get_user_list(role=None, status=None): 获取用户列表
   - 支持按角色、状态筛选
```

### 任务6：开发会员管理逻辑

```
请帮我完成 logic/member_manage_logic.py 会员管理逻辑：

1. register_member(member_data): 注册会员
   - 生成会员卡号（格式：VIP + 8位数字，如VIP00000001）
   - 初始等级为normal
   - 插入member表

2. update_member(member_id, member_data): 修改会员信息
   - 更新基本信息
   - 记录member_change_log（change_type='info'）

3. query_member(card_no=None, phone=None, name=None): 查询会员
   - 支持按卡号、手机号、姓名模糊查询

4. get_member_consume_records(member_id, limit=10): 获取消费记录
   - 关联order_info表查询
   - 返回最近N条消费记录

5. generate_card_no(): 生成会员卡号
   - 查询当前最大卡号
   - 返回下一个卡号
```

### 任务7：开发会员规则逻辑

```
请帮我完成 logic/member_rule_logic.py 会员规则逻辑：

1. get_all_rules(): 获取所有等级规则
   - 查询member_level_rule表

2. save_rule(rule_data): 保存等级规则
   - 更新member_level_rule表

3. get_member_discount(member_id): 获取会员折扣
   - 查询会员等级
   - 返回对应的discount_rate
   - 非会员返回1.0

4. add_member_points(member_id, amount): 累计积分
   - 根据消费金额和points_rate计算积分
   - 更新member表的total_points
   - 记录member_change_log

5. check_member_upgrade(member_id): 检查会员升级
   - 获取会员当前等级、累计消费、积分
   - 对比升级规则
   - 如果满足升级条件，更新level_code
   - 记录member_change_log（change_type='level_up'）
   - 发送升级通知
```

### 任务8：开发会员消费逻辑

```
请帮我完成 logic/member_consume_logic.py 会员消费逻辑：

1. add_consume(member_id, amount): 累计消费金额
   - 更新member表的total_consume
   - 调用add_member_points累计积分
   - 调用check_member_upgrade检查升级

2. reduce_member_points(member_id, points): 扣减积分（退货时调用）
   - 更新member表的total_points
   - 记录member_change_log

3. reduce_consume(member_id, amount): 扣减消费金额（退货时调用）
   - 更新member表的total_consume
   - 调用check_member_downgrade检查降级

4. check_member_downgrade(member_id): 检查会员降级
   - 获取会员当前等级、累计消费、积分
   - 如果低于当前等级标准，降级
   - 记录member_change_log（change_type='level_down'）
   - 发送降级通知

5. use_points_for_payment(member_id, points): 积分抵扣
   - 检查积分是否足够
   - 扣减积分
   - 返回抵扣金额
```

---

## 组员4提示词 - 退货管理 + 查询统计

### 任务1：开发退货查询界面

```
我是组员4，负责退货管理和查询统计。

请帮我完成 ui/return_query_ui.py 退货查询界面，要求：
1. 顶部：查询条件
   - 小票号/订单号输入框
   - 会员卡号输入框
   - 手机号输入框
   - 查询按钮
2. 中间：原订单信息展示
   - 订单基本信息：订单号、时间、总金额、支付方式
   - 会员信息：卡号、姓名、获得积分
   - 商品列表Treeview（勾选框、商品名、数量、单价、小计、已退数量）
3. 底部：选择退货商品后，点击"发起退货"跳转到退货处理界面

需要检查订单是否在7天退货期限内。
```

### 任务2：开发退货处理界面

```
请帮我完成 ui/return_handle_ui.py 退货处理界面，要求：
1. 顶部：显示原订单信息
2. 中间：退货商品列表
   - 商品名、退货数量（可修改，不超过原购买数量）、退货原因下拉框
   - 退货原因：质量问题、7天无理由、规格不符、损坏、其他
3. 质量问题区（当选择质量问题时显示）：
   - 问题描述文本框
   - 上传照片按钮（可选）
4. 退款信息区：
   - 显示退款金额（自动计算）
   - 显示扣减积分（自动计算）
   - 退款方式（与原支付方式一致）
5. 底部按钮：整单退货、部分退货、取消

退货原因return_reason枚举：quality_issue, no_reason_7day, spec_mismatch, damaged, other
```

### 任务3：开发综合查询界面

```
请帮我完成 ui/query_comprehensive_ui.py 综合查询界面，要求：
1. 顶部Tab切换：销售查询、商品查询、会员查询、挂单/撤单查询
2. 销售查询Tab：
   - 筛选条件：时间范围、订单类型（全部/会员/非会员）、商品分类
   - 结果列表：订单号、时间、商品数、总金额、会员卡号、状态
3. 商品查询Tab：
   - 筛选条件：商品名/条码、分类、状态
   - 结果列表：条码、名称、分类、价格、状态、库存
4. 会员查询Tab：
   - 筛选条件：卡号/姓名/手机、等级
   - 结果列表：卡号、姓名、等级、累计消费、积分
5. 挂单/撤单查询Tab：
   - 筛选条件：时间范围、状态（挂单/已撤销）
   - 结果列表：订单号、时间、金额、状态、收银员
```

### 任务4：开发统计报表界面

```
请帮我完成 ui/statistics_ui.py 统计报表界面，要求：
1. 顶部Tab切换：销售统计、会员统计
2. 销售统计Tab：
   - 筛选条件：时间范围、统计维度（按日/按周/按月）、分类
   - 图表区：折线图/柱状图显示销售额趋势
   - 表格区：显示销售量、销售额、同比、环比
   - 收银员业绩排行
3. 会员统计Tab：
   - 筛选条件：时间范围
   - 图表区：会员增长趋势、消费趋势
   - 表格区：各等级会员数量、消费占比
4. 底部：导出报表按钮、打印按钮

使用matplotlib绑定到tkinter显示图表：
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
import matplotlib.pyplot as plt
```

### 任务5：开发退货查询逻辑

```
请帮我完成 logic/return_query_logic.py 退货查询逻辑：

1. query_order_for_return(ticket_no=None, card_no=None, phone=None): 查询可退货订单
   - 按订单号/会员卡号/手机号查询
   - 只返回status='completed'且在7天内的订单
   - 关联查询订单明细、支付记录、会员信息

2. match_return_goods(order_id, barcode): 匹配退货商品
   - 扫描条码，匹配原订单中的商品
   - 返回商品信息和可退数量（原数量-已退数量）

3. check_return_limit(order_id): 检查退货期限
   - 检查订单完成时间是否在7天内
   - 返回True/False和剩余天数
```

### 任务6：开发整单退货逻辑

```
请帮我完成 logic/return_full_logic.py 整单退货逻辑：

1. process_full_return(order_id, return_reason, reason_detail=None, photo_path=None): 处理整单退货
   - 创建return_record记录，return_type='full'
   - 创建return_detail记录（所有商品）
   - 更新order_info状态为full_returned
   - 创建payment_record退款记录
   - 处理库存恢复（非质量问题转入库存，质量问题转待质检）
   - 如果是会员订单，扣减积分和消费金额，检查降级
   - 如果是质量问题，创建quality_feedback记录
   - 使用事务保证一致性

2. calculate_full_refund(order_id): 计算全额退款
   - 返回原订单的actual_amount

3. calculate_points_deduction(order_id): 计算积分扣减
   - 返回原订单的points_earned
```

### 任务7：开发部分退货逻辑

```
请帮我完成 logic/return_part_logic.py 部分退货逻辑：

1. process_part_return(order_id, return_items): 处理部分退货
   - return_items是列表，每项包含order_detail_id, return_quantity, return_reason
   - 创建return_record记录，return_type='part'
   - 创建return_detail记录（仅退货商品）
   - 原订单状态保持completed（不改变）
   - 更新order_detail的is_returned和returned_quantity
   - 创建payment_record退款记录
   - 处理库存恢复
   - 按比例扣减积分
   - 使用事务

2. calculate_part_refund(order_id, return_items): 计算部分退款
   - 根据退货商品计算退款金额

3. calculate_proportional_points(order_id, refund_amount): 按比例计算积分扣减
   - 积分扣减 = 原积分 × (退款金额 / 原订单金额)
```

### 任务8：开发退货异常处理逻辑

```
请帮我完成 logic/return_exception_logic.py 退货异常处理逻辑：

1. check_return_condition(order_id, goods_id, quantity): 检查退货条件
   - 检查订单是否存在且已完成
   - 检查是否超过退货期限
   - 检查退货数量是否超过可退数量
   - 返回(可退货, 原因)

2. handle_quality_feedback(return_id, goods_id, problem_desc, photo_path): 处理质量问题反馈
   - 创建quality_feedback记录
   - 更新商品状态为pending_inspect
   - 发送通知给商品管理员

3. send_quality_notification(feedback_id): 发送质量问题通知
   - 向sys_notification表插入通知
   - target_role='goods_manager'
   - notification_type='quality_feedback'
```

### 任务9：开发统计分析逻辑

```
请帮我完成 logic/statistics_logic.py 统计分析逻辑：

1. get_sales_statistics(start_date, end_date, group_by='day'): 销售统计
   - 按日/周/月汇总销售额、销售量
   - 返回时间序列数据，用于绑定图表

2. get_category_sales(start_date, end_date): 分类销售统计
   - 按商品分类（课-类-种）汇总销售额

3. get_cashier_performance(start_date, end_date): 收银员业绩
   - 按收银员汇总销售额、订单数

4. calculate_yoy_mom(current_data, period): 计算同比环比
   - 同比：与去年同期对比
   - 环比：与上一期对比

5. get_member_statistics(start_date, end_date): 会员统计
   - 各等级会员数量
   - 会员消费占比
   - 新增会员数

6. association_analysis(): 关联规则分析（可选，使用Apriori算法）
   - 分析经常一起购买的商品
   - 返回关联商品对和支持度
```

---

## 联调测试提示词

```
我需要测试模块间的联调，请帮我编写测试代码：

1. 收银-库存联调：
   - 创建一个测试订单
   - 验证结账后库存是否正确扣减

2. 收银-会员联调：
   - 使用会员卡号结账
   - 验证折扣是否正确应用
   - 验证积分是否正确累计
   - 验证是否触发升级

3. 退货-库存联调：
   - 创建退货记录
   - 验证库存是否正确恢复

4. 退货-会员联调：
   - 会员订单退货
   - 验证积分是否正确扣减
   - 验证是否触发降级

5. 退货-商品联调：
   - 质量问题退货
   - 验证质量反馈是否创建
   - 验证商品状态是否变为待质检
```

---

## 常见问题提示词

```
我遇到了以下问题，请帮我解决：

1. 数据库连接失败
2. CustomTkinter控件布局问题
3. Treeview数据绑定问题
4. 事务回滚不生效
5. 中文显示乱码
6. matplotlib图表无法显示在tkinter中
```
