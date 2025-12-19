# -*- coding: utf-8 -*-
"""
退货查询逻辑 - 组员4负责
"""


class ReturnQueryLogic:
    """退货查询业务逻辑"""
    
    def query_order_for_return(self, ticket_no=None, card_no=None, phone=None):
        """查询可退货订单"""
        # TODO: 实现
        pass
    
    def match_return_goods(self, order_id, barcode):
        """匹配退货商品"""
        # TODO: 实现
        pass
    
    def check_return_limit(self, order_id):
        """检查退货期限"""
        # TODO: 实现
        pass
