"""
密码模型
处理密码相关的数据库操作
"""

from datetime import datetime
import uuid


class Password:
    """密码模型类"""

    @staticmethod
    def create(db, user_id, domain, url, encrypted_username, encrypted_password, notes='', password_id=None, created_at=None, updated_at=None):
        """
        创建新密码并返回一个轻量对象，包含 .id 和 .to_dict()

        Args:
            db: 数据库连接
            user_id: 用户ID
            domain: 网站域名
            url: 网站URL
            encrypted_username: 加密的用户名（或明文，视上层而定）
            encrypted_password: 加密的密码（或明文，视上层而定）
            notes: 可选备注
            password_id: 可选的外部ID（如果未提供将自动生成）
            created_at, updated_at: 可选时间

        Returns:
            object: 具有 .id 属性和 .to_dict() 方法的对象
        """
        now = datetime.now()
        created = created_at if created_at else now
        updated = updated_at if updated_at else now

        if isinstance(created, str):
            created = datetime.fromisoformat(created.replace('Z', '+00:00'))

        if isinstance(updated, str):
            updated = datetime.fromisoformat(updated.replace('Z', '+00:00'))

        if not password_id:
            password_id = str(uuid.uuid4())

        cursor = db.cursor()
        cursor.execute(
            """
            INSERT INTO passwords (id, user_id, domain, website_url, encrypted_username, encrypted_password, created_at, updated_at)
            VALUES (%s, %s, %s, %s, %s, %s, %s, %s)
            """,
            (password_id, user_id, domain, url, encrypted_username, encrypted_password, created, updated)
        )
        db.commit()

        class _PwdObj:
            def __init__(self, id_):
                self.id = id_

            def to_dict(self):
                # 使用 find_by_id 保证返回结构一致
                return Password.find_by_id(db, self.id)

        return _PwdObj(password_id)

    @staticmethod
    def find_by_id(db, password_id):
        """
        通过ID查找密码

        Returns:
            dict: 密码信息，如果不存在则返回None
        """
        cursor = db.cursor(dictionary=True)
        cursor.execute("SELECT * FROM passwords WHERE id = %s", (password_id,))
        password = cursor.fetchone()

        # 转换日期为ISO格式字符串
        if password:
            if isinstance(password.get('created_at'), datetime):
                password['created_at'] = password['created_at'].isoformat()
            if isinstance(password.get('updated_at'), datetime):
                password['updated_at'] = password['updated_at'].isoformat()

        return password

    @staticmethod
    def find_by_user_id(db, user_id):
        """
        查找用户的所有密码

        Returns:
            list: 密码列表
        """
        cursor = db.cursor(dictionary=True)
        cursor.execute("SELECT * FROM passwords WHERE user_id = %s", (user_id,))
        passwords = cursor.fetchall()

        # 转换日期为ISO格式字符串
        for password in passwords:
            if isinstance(password.get('created_at'), datetime):
                password['created_at'] = password['created_at'].isoformat()
            if isinstance(password.get('updated_at'), datetime):
                password['updated_at'] = password['updated_at'].isoformat()

        return passwords

    @staticmethod
    def find_by_domain(db, user_id, domain):
        """
        查找用户在特定域名下的密码

        Returns:
            list: 密码列表
        """
        cursor = db.cursor(dictionary=True)
        cursor.execute("SELECT * FROM passwords WHERE user_id = %s AND domain = %s", (user_id, domain))
        passwords = cursor.fetchall()

        # 转换日期为ISO格式字符串
        for password in passwords:
            if isinstance(password.get('created_at'), datetime):
                password['created_at'] = password['created_at'].isoformat()
            if isinstance(password.get('updated_at'), datetime):
                password['updated_at'] = password['updated_at'].isoformat()

        return passwords

    @staticmethod
    def find_by_domain_and_username(db, user_id, domain, username):
        """
        查找指定域名和用户名的单条记录（用于判断是否存在）

        Returns:
            dict|None: 密码记录或None
        """
        cursor = db.cursor(dictionary=True)
        cursor.execute(
            "SELECT * FROM passwords WHERE user_id = %s AND domain = %s AND encrypted_username = %s LIMIT 1",
            (user_id, domain, username)
        )
        row = cursor.fetchone()
        if row:
            if isinstance(row.get('created_at'), datetime):
                row['created_at'] = row['created_at'].isoformat()
            if isinstance(row.get('updated_at'), datetime):
                row['updated_at'] = row['updated_at'].isoformat()
        return row

    @staticmethod
    def update(db, password_id, domain, url, encrypted_username, encrypted_password, notes=''):
        """
        更新密码并返回一个轻量对象（与 create 返回的对象相同形式）

        Returns:
            object|None: 更新成功返回对象，失败返回None
        """
        cursor = db.cursor()
        now = datetime.now()
        cursor.execute(
            """
            UPDATE passwords 
            SET domain = %s, website_url = %s, encrypted_username = %s, encrypted_password = %s, updated_at = %s
            WHERE id = %s
            """,
            (domain, url, encrypted_username, encrypted_password, now, password_id)
        )
        db.commit()

        if cursor.rowcount > 0:
            class _UpdatedObj:
                def __init__(self, id_):
                    self.id = id_

                def to_dict(self):
                    return Password.find_by_id(db, self.id)

            return _UpdatedObj(password_id)

        return None

    @staticmethod
    def update_password_only(db, password_id, encrypted_password):
        """
        仅更新密码字段

        Returns:
            bool: 更新是否成功
        """
        cursor = db.cursor()
        cursor.execute(
            """
            UPDATE passwords 
            SET encrypted_password = %s, updated_at = %s
            WHERE id = %s
            """,
            (encrypted_password, datetime.now(), password_id)
        )
        db.commit()

        return cursor.rowcount > 0

    @staticmethod
    def delete(db, password_id):
        """
        删除密码

        Returns:
            bool: 删除是否成功
        """
        cursor = db.cursor()
        cursor.execute("DELETE FROM passwords WHERE id = %s", (password_id,))
        db.commit()

        return cursor.rowcount > 0

    @staticmethod
    def find_shared_with_user(db, user_id):
        """
        查找与用户共享的密码

        Returns:
            list: 共享密码列表
        """
        cursor = db.cursor(dictionary=True)
        cursor.execute(
            """
            SELECT p.*, b.permissions, u.email as owner_email
            FROM passwords p
            JOIN account_bindings b ON p.user_id = b.account_a_id
            JOIN users u ON p.user_id = u.id
            WHERE b.account_b_id = %s AND b.binding_status = 'active'
            """,
            (user_id,)
        )
        shared_passwords = cursor.fetchall()

        # 转换日期为ISO格式字符串
        for password in shared_passwords:
            if isinstance(password.get('created_at'), datetime):
                password['created_at'] = password['created_at'].isoformat()
            if isinstance(password.get('updated_at'), datetime):
                password['updated_at'] = password['updated_at'].isoformat()

        return shared_passwords
