# 超市前台销售系统

## 项目简介

基于 Python + CustomTkinter + MySQL 的超市前台销售管理系统，包含收银管理、商品管理、会员管理、退货管理和统计分析等功能模块。

## 项目结构

```
Supermarket-front-desk-sales-system/
├── main.py                 # 程序入口
├── config.py               # 系统配置
├── requirements.txt        # 依赖包
│
├── db/                     # 数据库模块
│   ├── __init__.py
│   ├── db_conn.py          # 数据库连接
│   └── schema.sql          # 建表脚本
│
├── ui/                     # 界面模块
│   ├── __init__.py
│   ├── main_ui.py          # 主界面 (组员1)
│   ├── cashier_ui.py       # 收银界面 (组员1)
│   ├── goods_category_ui.py    # 商品分类界面 (组员2)
│   ├── goods_manage_ui.py      # 商品管理界面 (组员2)
│   ├── inventory_monitor_ui.py # 库存监控界面 (组员2)
│   ├── user_manage_ui.py       # 用户管理界面 (组员3)
│   ├── member_manage_ui.py     # 会员管理界面 (组员3)
│   ├── member_rule_ui.py       # 会员规则界面 (组员3)
│   ├── return_query_ui.py      # 退货查询界面 (组员4)
│   ├── return_handle_ui.py     # 退货处理界面 (组员4)
│   ├── query_comprehensive_ui.py # 综合查询界面 (组员4)
│   └── statistics_ui.py        # 统计报表界面 (组员4)
│
├── logic/                  # 业务逻辑模块
│   ├── __init__.py
│   ├── cashier_logic.py        # 收银结算逻辑 (组员1)
│   ├── cashier_hang_cancel.py  # 挂单/调单/撤单 (组员1)
│   ├── goods_category_logic.py # 商品分类逻辑 (组员2)
│   ├── goods_manage_logic.py   # 商品管理逻辑 (组员2)
│   ├── goods_quality_logic.py  # 质量问题处理 (组员2)
│   ├── inventory_logic.py      # 库存管理逻辑 (组员2)
│   ├── inventory_warning.py    # 库存警戒逻辑 (组员2)
│   ├── user_auth_logic.py      # 用户认证逻辑 (组员3)
│   ├── user_manage_logic.py    # 用户管理逻辑 (组员3)
│   ├── member_manage_logic.py  # 会员管理逻辑 (组员3)
│   ├── member_rule_logic.py    # 会员规则逻辑 (组员3)
│   ├── member_consume_logic.py # 会员消费逻辑 (组员3)
│   ├── return_query_logic.py   # 退货查询逻辑 (组员4)
│   ├── return_full_logic.py    # 整单退货逻辑 (组员4)
│   ├── return_part_logic.py    # 部分退货逻辑 (组员4)
│   ├── return_exception_logic.py # 退货异常处理 (组员4)
│   ├── query_base_logic.py     # 基础查询逻辑 (组员4)
│   └── statistics_logic.py     # 统计分析逻辑 (组员4)
│
├── utils/                  # 工具模块
│   ├── __init__.py
│   └── print_utils.py      # 打印工具 (组员1)
│
└── docs/                   # 文档
    └── 数据库设计文档.md
```

## 分工说明

| 组员 | 负责模块 | 主要文件 |
|------|----------|----------|
| 组员1(组长) | 收银管理 + 系统框架 | main_ui, cashier_ui, cashier_logic, print_utils |
| 组员2 | 商品管理 + 库存管理 | goods_*_ui, goods_*_logic, inventory_* |
| 组员3 | 会员管理 + 用户权限 | user_*_ui, member_*_ui, user_*_logic, member_*_logic |
| 组员4 | 退货管理 + 查询统计 | return_*_ui, query_*_ui, statistics_ui, return_*_logic, statistics_logic |

## 环境要求

- Python 3.8+
- MySQL 5.7+ / 8.0+

## 安装步骤

1. 安装依赖
```bash
pip install -r requirements.txt
```

2. 创建数据库
```bash
mysql -u root -p < db/schema.sql
```

3. 修改数据库配置
编辑 `config.py` 文件，修改数据库连接信息

4. 运行程序
```bash
python main.py
```

## 默认账号

- 用户名：admin
- 密码：admin123

## 技术栈

- 界面：CustomTkinter
- 数据库：MySQL + PyMySQL
- 数据分析：Pandas + Matplotlib
- 关联规则：mlxtend (Apriori算法)
