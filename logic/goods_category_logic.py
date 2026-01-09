# -*- coding: utf-8 -*-
"""商品分类逻辑"""

from db.db_conn import DBConnection


class GoodsCategoryLogic:
    """商品分类业务逻辑"""
    
    def get_all_categories(self):
        """获取所有分类"""
        with DBConnection() as db:
            sql = """
                SELECT c.*, p.category_name as parent_name
                FROM goods_category c
                LEFT JOIN goods_category p ON c.parent_id = p.category_id
                WHERE c.delete_flag = 0 OR c.delete_flag IS NULL
                ORDER BY c.level, c.sort_order, c.category_id
            """
            db.execute(sql)
            return db.fetchall()
    
    def get_categories_by_level(self, level):
        """按级别获取分类"""
        with DBConnection() as db:
            sql = "SELECT * FROM goods_category WHERE level = %s ORDER BY sort_order"
            db.execute(sql, (level,))
            return db.fetchall()
    
    def add_category(self, name, parent_id, level, sort_order=1):
        """新增分类"""
        with DBConnection() as db:
            try:
                # 检查名称是否重复
                db.execute("SELECT category_id FROM goods_category WHERE category_name = %s", (name,))
                if db.fetchone():
                    return False, "分类名称已存在"
                
                # 验证父级分类
                if parent_id:
                    db.execute("SELECT level FROM goods_category WHERE category_id = %s", (parent_id,))
                    parent = db.fetchone()
                    if not parent:
                        return False, "父级分类不存在"
                    if parent['level'] != level - 1:
                        return False, "父级分类级别不正确"
                
                sql = """
                    INSERT INTO goods_category (category_name, parent_id, level, sort_order)
                    VALUES (%s, %s, %s, %s)
                """
                db.execute(sql, (name, parent_id, level, sort_order))
                db.commit()
                return True, "分类添加成功"
            except Exception as e:
                db.rollback()
                return False, f"添加失败: {str(e)}"
    
    def update_category(self, category_id, name, sort_order=None):
        """修改分类"""
        with DBConnection() as db:
            try:
                # 检查名称是否重复
                db.execute("SELECT category_id FROM goods_category WHERE category_name = %s AND category_id != %s", 
                          (name, category_id))
                if db.fetchone():
                    return False, "分类名称已存在"
                
                if sort_order:
                    sql = "UPDATE goods_category SET category_name = %s, sort_order = %s WHERE category_id = %s"
                    db.execute(sql, (name, sort_order, category_id))
                else:
                    sql = "UPDATE goods_category SET category_name = %s WHERE category_id = %s"
                    db.execute(sql, (name, category_id))
                
                db.commit()
                return True, "分类修改成功"
            except Exception as e:
                db.rollback()
                return False, f"修改失败: {str(e)}"
    
    def delete_category(self, category_id):
        """删除分类"""
        with DBConnection() as db:
            try:
                # 检查是否有子分类
                db.execute("SELECT category_id FROM goods_category WHERE parent_id = %s", (category_id,))
                if db.fetchone():
                    return False, "该分类下有子分类，无法删除"
                
                # 检查是否有商品
                db.execute("SELECT goods_id FROM goods WHERE category_id = %s LIMIT 1", (category_id,))
                if db.fetchone():
                    return False, "该分类下有商品，无法删除"
                
                db.execute("DELETE FROM goods_category WHERE category_id = %s", (category_id,))
                db.commit()
                return True, "分类删除成功"
            except Exception as e:
                db.rollback()
                return False, f"删除失败: {str(e)}"
    
    def get_category_tree(self):
        """获取分类树结构"""
        categories = self.get_all_categories()
        
        # 构建树结构
        tree = []
        category_map = {c['category_id']: c for c in categories}
        
        for cat in categories:
            cat['children'] = []
            if cat['parent_id'] is None:
                tree.append(cat)
            else:
                parent = category_map.get(cat['parent_id'])
                if parent:
                    parent['children'].append(cat)
        
        return tree
