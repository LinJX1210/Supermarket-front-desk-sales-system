# -*- coding: utf-8 -*-
"""
小票打印工具 - 组员1负责
"""

import os
from datetime import datetime


# 小票配置
RECEIPT_CONFIG = {
    "store_name": "智慧超市",
    "store_address": "XX市XX区XX路XX号",
    "store_phone": "400-XXX-XXXX",
    "width": 48,  # 小票宽度（字符数）
    "receipts_dir": "receipts"  # 小票保存目录
}


def _center_text(text, width=None):
    """居中文本"""
    width = width or RECEIPT_CONFIG["width"]
    return text.center(width)


def _left_right_text(left, right, width=None):
    """左右对齐文本"""
    width = width or RECEIPT_CONFIG["width"]
    space = width - len(left) - len(right)
    if space < 1:
        space = 1
    return left + " " * space + right


def _separator(char="-", width=None):
    """分隔线"""
    width = width or RECEIPT_CONFIG["width"]
    return char * width


def generate_receipt(order_info, order_details, member_info=None, cashier_name=""):
    """
    生成小票内容
    :param order_info: 订单信息 {order_no, total_amount, discount_amount, actual_amount, points_earned, create_time}
    :param order_details: 商品明细 [{goods_name, quantity, unit_price, subtotal}, ...]
    :param member_info: 会员信息 {card_no, name, total_points} (可选)
    :param cashier_name: 收银员姓名
    :return: 格式化的小票文本
    """
    lines = []
    w = RECEIPT_CONFIG["width"]
    
    # 店铺信息
    lines.append(_center_text(RECEIPT_CONFIG["store_name"]))
    lines.append(_center_text(RECEIPT_CONFIG["store_address"]))
    lines.append(_center_text(f"电话: {RECEIPT_CONFIG['store_phone']}"))
    lines.append(_separator("="))
    
    # 订单信息
    lines.append(f"订单号: {order_info.get('order_no', '')}")
    
    # 处理时间格式
    create_time = order_info.get("create_time", "")
    if isinstance(create_time, datetime):
        create_time = create_time.strftime("%Y-%m-%d %H:%M:%S")
    lines.append(f"时  间: {create_time}")
    
    if cashier_name:
        lines.append(f"收银员: {cashier_name}")
    lines.append(_separator("-"))
    
    # 商品列表表头
    lines.append("商品名称")
    lines.append(_left_right_text("  数量 x 单价", "小计"))
    lines.append(_separator("-"))
    
    # 商品明细
    for item in order_details:
        name = item.get("goods_name", "")
        # 商品名称过长时截断
        if len(name) > w - 2:
            name = name[:w-4] + ".."
        lines.append(name)
        
        qty = item.get("quantity", 0)
        price = item.get("unit_price", 0)
        subtotal = item.get("subtotal", 0)
        
        # 格式化数量（整数或小数）
        if qty == int(qty):
            qty_str = str(int(qty))
        else:
            qty_str = f"{qty:.2f}"
        
        detail_left = f"  {qty_str} x ¥{price:.2f}"
        detail_right = f"¥{subtotal:.2f}"
        lines.append(_left_right_text(detail_left, detail_right))
    
    lines.append(_separator("-"))
    
    # 金额汇总
    total = order_info.get("total_amount", 0)
    discount = order_info.get("discount_amount", 0)
    actual = order_info.get("actual_amount", 0)
    
    lines.append(_left_right_text("商品总额:", f"¥{total:.2f}"))
    
    if discount > 0:
        lines.append(_left_right_text("优惠金额:", f"-¥{discount:.2f}"))
    
    lines.append(_separator("-"))
    lines.append(_left_right_text("实付金额:", f"¥{actual:.2f}"))
    lines.append(_separator("="))
    
    # 会员信息
    if member_info:
        lines.append("【会员信息】")
        lines.append(f"卡  号: {member_info.get('card_no', '')}")
        if member_info.get("name"):
            lines.append(f"姓  名: {member_info.get('name', '')}")
        
        points_earned = order_info.get("points_earned", 0)
        total_points = member_info.get("total_points", 0)
        
        lines.append(f"本次积分: +{points_earned}")
        lines.append(f"累计积分: {total_points + points_earned}")
        lines.append(_separator("-"))
    
    # 退货提示
    lines.append("")
    lines.append(_center_text("*** 温馨提示 ***"))
    lines.append("商品如有质量问题，请于7日内")
    lines.append("凭此小票办理退换货。")
    lines.append("")
    lines.append(_center_text("谢谢惠顾，欢迎再次光临！"))
    lines.append("")
    lines.append(_center_text(datetime.now().strftime("%Y-%m-%d %H:%M:%S")))
    
    return "\n".join(lines)


def print_receipt(receipt_text, order_no):
    """
    打印/保存小票
    :param receipt_text: 小票文本内容
    :param order_no: 订单号（用于文件名）
    :return: {"success": bool, "file_path": str, "message": str}
    """
    try:
        # 确保目录存在
        receipts_dir = RECEIPT_CONFIG["receipts_dir"]
        if not os.path.exists(receipts_dir):
            os.makedirs(receipts_dir)
        
        # 生成文件名
        filename = f"receipt_{order_no}.txt"
        file_path = os.path.join(receipts_dir, filename)
        
        # 保存文件
        with open(file_path, "w", encoding="utf-8") as f:
            f.write(receipt_text)
        
        return {
            "success": True,
            "file_path": file_path,
            "message": f"小票已保存: {file_path}"
        }
        
    except Exception as e:
        return {
            "success": False,
            "file_path": None,
            "message": f"保存小票失败: {str(e)}"
        }


def generate_return_receipt(return_info, return_details, member_info=None, operator_name=""):
    """
    生成退货凭证
    :param return_info: 退货信息 {return_no, order_no, refund_amount, points_deducted, return_reason, create_time}
    :param return_details: 退货明细 [{goods_name, quantity, refund_amount}, ...]
    :param member_info: 会员信息 (可选)
    :param operator_name: 操作员姓名
    :return: 格式化的退货凭证文本
    """
    lines = []
    w = RECEIPT_CONFIG["width"]
    
    # 店铺信息
    lines.append(_center_text(RECEIPT_CONFIG["store_name"]))
    lines.append(_center_text("【退货凭证】"))
    lines.append(_separator("="))
    
    # 退货信息
    lines.append(f"退货单号: {return_info.get('return_no', '')}")
    lines.append(f"原订单号: {return_info.get('order_no', '')}")
    
    create_time = return_info.get("create_time", "")
    if isinstance(create_time, datetime):
        create_time = create_time.strftime("%Y-%m-%d %H:%M:%S")
    lines.append(f"退货时间: {create_time}")
    
    if operator_name:
        lines.append(f"操 作 员: {operator_name}")
    
    # 退货原因
    reason_map = {
        "quality_issue": "质量问题",
        "no_reason_7day": "7天无理由",
        "spec_mismatch": "规格不符",
        "damaged": "商品损坏",
        "other": "其他原因"
    }
    reason = return_info.get("return_reason", "")
    reason_text = reason_map.get(reason, reason)
    lines.append(f"退货原因: {reason_text}")
    lines.append(_separator("-"))
    
    # 退货商品
    lines.append("退货商品:")
    for item in return_details:
        name = item.get("goods_name", "")
        qty = item.get("quantity", 0)
        amount = item.get("refund_amount", 0)
        
        if len(name) > w - 2:
            name = name[:w-4] + ".."
        lines.append(f"  {name}")
        lines.append(_left_right_text(f"    数量: {qty}", f"¥{amount:.2f}"))
    
    lines.append(_separator("-"))
    
    # 退款金额
    refund = return_info.get("refund_amount", 0)
    lines.append(_left_right_text("退款金额:", f"¥{refund:.2f}"))
    
    # 积分扣减
    points_deducted = return_info.get("points_deducted", 0)
    if points_deducted > 0:
        lines.append(_left_right_text("扣减积分:", f"-{points_deducted}"))
    
    lines.append(_separator("="))
    
    # 会员信息
    if member_info:
        lines.append(f"会员卡号: {member_info.get('card_no', '')}")
    
    lines.append("")
    lines.append(_center_text("此凭证请妥善保管"))
    lines.append("")
    
    return "\n".join(lines)


def print_return_receipt(receipt_text, return_no):
    """
    打印/保存退货凭证
    :param receipt_text: 凭证文本内容
    :param return_no: 退货单号
    :return: {"success": bool, "file_path": str, "message": str}
    """
    try:
        receipts_dir = RECEIPT_CONFIG["receipts_dir"]
        if not os.path.exists(receipts_dir):
            os.makedirs(receipts_dir)
        
        filename = f"return_{return_no}.txt"
        file_path = os.path.join(receipts_dir, filename)
        
        with open(file_path, "w", encoding="utf-8") as f:
            f.write(receipt_text)
        
        return {
            "success": True,
            "file_path": file_path,
            "message": f"退货凭证已保存: {file_path}"
        }
        
    except Exception as e:
        return {
            "success": False,
            "file_path": None,
            "message": f"保存退货凭证失败: {str(e)}"
        }
