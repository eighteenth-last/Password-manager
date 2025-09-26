"""
账号绑定模型
处理账号绑定相关的数据库操作
"""

from datetime import datetime
import uuid

class Binding:
    """账号绑定模型类"""
    
    @staticmethod
    def create(db, account_a_id, account_b_id, binding_status, permissions):
        """
        创建新的账号绑定关系
        
        Args:
            db: 数据库连接
            account_a_id: 账号A的ID（发起绑定的账号）
            account_b_id: 账号B的ID（被绑定的账号）
            binding_status: 绑定状态（pending, active）
            permissions: 权限（read, write）
            
        Returns:
            str: 绑定关系ID
        """
        # 生成唯一ID
        binding_id = str(uuid.uuid4())
        
        # 当前时间
        now = datetime.now()
        
        # 插入绑定记录
        cursor = db.cursor()
        cursor.execute(
            """
            INSERT INTO account_bindings (id, account_a_id, account_b_id, binding_status, permissions, created_at, updated_at)
            VALUES (%s, %s, %s, %s, %s, %s, %s)
            """,
            (binding_id, account_a_id, account_b_id, binding_status, permissions, now, now)
        )
        db.commit()
        
        return binding_id
    
    @staticmethod
    def find_by_id(db, binding_id):
        """
        通过ID查找绑定关系
        
        Args:
            db: 数据库连接
            binding_id: 绑定关系ID
            
        Returns:
            dict: 绑定关系信息，如果不存在则返回None
        """
        cursor = db.cursor(dictionary=True)
        cursor.execute("SELECT * FROM account_bindings WHERE id = %s", (binding_id,))
        binding = cursor.fetchone()
        
        # 转换日期为ISO格式字符串
        if binding:
            binding['created_at'] = binding['created_at'].isoformat()
            binding['updated_at'] = binding['updated_at'].isoformat()
        
        return binding
    
    @staticmethod
    def find_by_account_ids(db, account_a_id, account_b_id):
        """
        通过账号ID查找绑定关系
        
        Args:
            db: 数据库连接
            account_a_id: 账号A的ID
            account_b_id: 账号B的ID
            
        Returns:
            dict: 绑定关系信息，如果不存在则返回None
        """
        cursor = db.cursor(dictionary=True)
        cursor.execute(
            "SELECT * FROM account_bindings WHERE account_a_id = %s AND account_b_id = %s",
            (account_a_id, account_b_id)
        )
        binding = cursor.fetchone()
        
        # 转换日期为ISO格式字符串
        if binding:
            binding['created_at'] = binding['created_at'].isoformat()
            binding['updated_at'] = binding['updated_at'].isoformat()
        
        return binding
    
    @staticmethod
    def find_by_user_id(db, user_id):
        """
        查找用户的所有绑定关系
        
        Args:
            db: 数据库连接
            user_id: 用户ID
            
        Returns:
            list: 绑定关系列表
        """
        cursor = db.cursor(dictionary=True)
        cursor.execute(
            """
            SELECT b.*, u.email as bound_account_email
            FROM account_bindings b
            JOIN users u ON b.account_b_id = u.id
            WHERE b.account_a_id = %s AND b.binding_status = 'active'
            """,
            (user_id,)
        )
        bindings = cursor.fetchall()
        
        # 转换日期为ISO格式字符串
        for binding in bindings:
            binding['created_at'] = binding['created_at'].isoformat()
            binding['updated_at'] = binding['updated_at'].isoformat()
        
        return bindings
    
    @staticmethod
    def find_pending_requests(db, user_id):
        """
        查找发送给用户的待处理绑定请求
        
        Args:
            db: 数据库连接
            user_id: 用户ID
            
        Returns:
            list: 待处理绑定请求列表
        """
        cursor = db.cursor(dictionary=True)
        cursor.execute(
            """
            SELECT b.*, u.email as requester_email
            FROM account_bindings b
            JOIN users u ON b.account_a_id = u.id
            WHERE b.account_b_id = %s AND b.binding_status = 'pending'
            """,
            (user_id,)
        )
        requests = cursor.fetchall()
        
        # 转换日期为ISO格式字符串
        for request in requests:
            request['created_at'] = request['created_at'].isoformat()
            request['updated_at'] = request['updated_at'].isoformat()
        
        return requests
    
    @staticmethod
    def update_status(db, binding_id, status):
        """
        更新绑定状态
        
        Args:
            db: 数据库连接
            binding_id: 绑定关系ID
            status: 新状态
            
        Returns:
            bool: 更新是否成功
        """
        cursor = db.cursor()
        cursor.execute(
            "UPDATE account_bindings SET binding_status = %s, updated_at = %s WHERE id = %s",
            (status, datetime.now(), binding_id)
        )
        db.commit()
        
        return cursor.rowcount > 0
    
    @staticmethod
    def update_permissions(db, binding_id, permissions):
        """
        更新绑定权限
        
        Args:
            db: 数据库连接
            binding_id: 绑定关系ID
            permissions: 新权限
            
        Returns:
            bool: 更新是否成功
        """
        cursor = db.cursor()
        cursor.execute(
            "UPDATE account_bindings SET permissions = %s, updated_at = %s WHERE id = %s",
            (permissions, datetime.now(), binding_id)
        )
        db.commit()
        
        return cursor.rowcount > 0
    
    @staticmethod
    def delete(db, binding_id):
        """
        删除绑定关系
        
        Args:
            db: 数据库连接
            binding_id: 绑定关系ID
            
        Returns:
            bool: 删除是否成功
        """
        cursor = db.cursor()
        cursor.execute("DELETE FROM account_bindings WHERE id = %s", (binding_id,))
        db.commit()
        
        return cursor.rowcount > 0
