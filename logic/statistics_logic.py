# -*- coding: utf-8 -*-
"""统计分析逻辑"""

from db.db_conn import DBConnection


class StatisticsLogic:
    """统计分析业务逻辑"""
    
    def get_summary(self, start_date, end_date):
        """获取汇总数据"""
        with DBConnection() as db:
            # 销售总额和订单数
            sql = """
                SELECT COUNT(*) as order_count, 
                       COALESCE(SUM(actual_amount), 0) as total_sales,
                       COALESCE(SUM(CASE WHEN member_id IS NOT NULL THEN actual_amount ELSE 0 END), 0) as member_sales
                FROM order_info 
                WHERE order_status = 'completed'
                AND DATE(create_time) >= %s AND DATE(create_time) <= %s
            """
            db.execute(sql, (start_date, end_date))
            sales = db.fetchone()
            
            # 退货金额
            sql = """
                SELECT COALESCE(SUM(refund_amount), 0) as total_return
                FROM return_record
                WHERE DATE(create_time) >= %s AND DATE(create_time) <= %s
            """
            db.execute(sql, (start_date, end_date))
            returns = db.fetchone()
            
            total_sales = float(sales['total_sales'] or 0)
            member_sales = float(sales['member_sales'] or 0)
            member_ratio = (member_sales / total_sales * 100) if total_sales > 0 else 0
            
            return {
                'total_sales': total_sales,
                'total_orders': sales['order_count'] or 0,
                'total_return': float(returns['total_return'] or 0),
                'member_ratio': member_ratio
            }
    
    def get_daily_sales(self, start_date, end_date):
        """获取每日销售数据"""
        with DBConnection() as db:
            sql = """
                SELECT 
                    DATE(o.create_time) as date,
                    COUNT(DISTINCT o.order_id) as order_count,
                    COALESCE(SUM(o.actual_amount), 0) as sales,
                    COALESCE(SUM(o.actual_amount) - SUM(d.quantity * g.cost_price), 0) as profit
                FROM order_info o
                LEFT JOIN order_detail d ON o.order_id = d.order_id
                LEFT JOIN goods g ON d.goods_id = g.goods_id
                WHERE o.order_status = 'completed'
                AND DATE(o.create_time) >= %s AND DATE(o.create_time) <= %s
                GROUP BY DATE(o.create_time)
                ORDER BY date DESC
            """
            db.execute(sql, (start_date, end_date))
            results = db.fetchall()
            
            return [{
                'date': str(r['date']),
                'order_count': r['order_count'],
                'sales': float(r['sales'] or 0),
                'profit': float(r['profit'] or 0)
            } for r in results]
    
    def get_goods_ranking(self, start_date, end_date, limit=20):
        """获取商品销量排行"""
        with DBConnection() as db:
            sql = """
                SELECT 
                    g.goods_name,
                    COALESCE(SUM(d.quantity - d.returned_quantity), 0) as total_qty,
                    COALESCE(SUM(d.subtotal), 0) as total_amount
                FROM order_detail d
                JOIN goods g ON d.goods_id = g.goods_id
                JOIN order_info o ON d.order_id = o.order_id
                WHERE o.order_status = 'completed'
                AND DATE(o.create_time) >= %s AND DATE(o.create_time) <= %s
                GROUP BY g.goods_id, g.goods_name
                HAVING total_qty > 0
                ORDER BY total_qty DESC
                LIMIT %s
            """
            db.execute(sql, (start_date, end_date, limit))
            results = db.fetchall()
            
            return [{
                'goods_name': r['goods_name'],
                'total_qty': int(r['total_qty']),
                'total_amount': float(r['total_amount'] or 0)
            } for r in results]
    
    def get_member_ranking(self, start_date, end_date, limit=20):
        """获取会员消费排行"""
        with DBConnection() as db:
            sql = """
                SELECT 
                    m.name, m.card_no,
                    COUNT(o.order_id) as order_count,
                    COALESCE(SUM(o.actual_amount), 0) as total_amount
                FROM member m
                JOIN order_info o ON m.member_id = o.member_id
                WHERE o.order_status = 'completed'
                AND DATE(o.create_time) >= %s AND DATE(o.create_time) <= %s
                GROUP BY m.member_id, m.name, m.card_no
                ORDER BY total_amount DESC
                LIMIT %s
            """
            db.execute(sql, (start_date, end_date, limit))
            results = db.fetchall()
            
            return [{
                'name': r['name'],
                'card_no': r['card_no'],
                'order_count': r['order_count'],
                'total_amount': float(r['total_amount'] or 0)
            } for r in results]
    
    def get_order_list(self, start_date, end_date, limit=100):
        """获取订单列表"""
        with DBConnection() as db:
            sql = """
                SELECT 
                    o.order_id, o.order_no, o.actual_amount, 
                    o.order_status, o.create_time,
                    m.name as member_name, m.card_no
                FROM order_info o
                LEFT JOIN member m ON o.member_id = m.member_id
                WHERE DATE(o.create_time) >= %s AND DATE(o.create_time) <= %s
                ORDER BY o.create_time DESC
                LIMIT %s
            """
            db.execute(sql, (start_date, end_date, limit))
            results = db.fetchall()
            
            return results
