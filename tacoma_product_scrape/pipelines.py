# Define your item pipelines here
#
# Don't forget to add your pipeline to the ITEM_PIPELINES setting
# See: https://docs.scrapy.org/en/latest/topics/item-pipeline.html


# useful for handling different item types with a single interface
from itemadapter import ItemAdapter
import mysql.connector
from mysql.connector import Error






class TacomaProductScrapePipeline:

    def __init__(self):
        # Database configuration
        self.host = "localhost"
        self.user = "root"
        self.password = "actowiz"  # replace with your MySQL password
        self.port = "3306"
        self.database = "tacoma_scrapy_db"

    def open_spider(self, spider):
        """Runs when spider starts"""
        try:
            # Connect to MySQL server
            self.conn = mysql.connector.connect(
                host=self.host,
                user=self.user,
                password=self.password,
                port=self.port
            )
            self.cursor = self.conn.cursor()

            # Create database if not exists
            self.cursor.execute(f"CREATE DATABASE IF NOT EXISTS {self.database}")
            self.conn.database = self.database


            # ================================
            #  1. Create all_category table
            # ================================
            self.cursor.execute("""
            CREATE TABLE IF NOT EXISTS all_category (
                id INT AUTO_INCREMENT PRIMARY KEY,
                category_name VARCHAR(255),
                url TEXT,
                status VARCHAR(50) DEFAULT 'pending'
                
            )
            """)

            # ==================================
            # 2. Create product_api table
            # ==================================
            self.cursor.execute("""
            CREATE TABLE IF NOT EXISTS product_api (
                id INT AUTO_INCREMENT PRIMARY KEY,
                category_name VARCHAR(255),
                sub_category_id VARCHAR(255),
                sub_category_name VARCHAR(255),
                api_url TEXT,
                status VARCHAR(50) DEFAULT 'pending'
            )
            """)


            # ====================================
            #  3. Create product_detail table
            # ====================================
            self.cursor.execute("""
            CREATE TABLE IF NOT EXISTS product_detail (
                id INT AUTO_INCREMENT PRIMARY KEY,
                category_name VARCHAR(255),
                sub_category_id VARCHAR(255),
                sub_category_name VARCHAR(255),
                product_id VARCHAR(100),
                product_name TEXT,
                product_url TEXT,
                status VARCHAR(50) DEFAULT 'pending'
            )
            """)

            self.cursor.execute("""
            CREATE TABLE IF NOT EXISTS product_info (
                id INT AUTO_INCREMENT PRIMARY KEY,
                product_id VARCHAR(255),
                product_name VARCHAR(255),
                url TEXT,
                img_url TEXT,
                price VARCHAR(255),
                description TEXT,
                shipping_weight VARCHAR(255),
                in_stock VARCHAR(255),
                specification TEXT
            )
            """)

            # # Create table if not exists with UNIQUE on city_link
            # self.cursor.execute("""
            # CREATE TABLE IF NOT EXISTS tacoma_stores (
            #     id INT AUTO_INCREMENT PRIMARY KEY,
            #     category_name VARCHAR(255),
            #     sub_category_name VARCHAR(255),
            #     product_id VARCHAR(255),
            #     product_name VARCHAR(255) ,
            #     product_url TEXT
            # )
            # """)

            self.conn.commit()
        except Error as e:
            spider.logger.error(f"Error connecting to MySQL: {e}")


    def process_item(self, item, spider):


        # -------------------------------
        # Insert into all_category
        # -------------------------------
        if item.get("type") == "category":
            query = """
            INSERT INTO all_category (category_name, url, status)
            VALUES (%s, %s, %s)
            
            """

            values = (
                item.get("category_name"),
                item.get("url"),
                item.get("status", "pending")
            )

            self.cursor.execute(query, values)
            self.conn.commit()

        # -------------------------------
        #  Insert into product_api
        # -------------------------------
        elif item.get("type") == "product_api":
            query = """
            INSERT INTO product_api (category_name, sub_category_id, sub_category_name, api_url, status)
            VALUES (%s, %s, %s, %s, %s)
            
            """

            values = (
                item.get("category_name"),
                item.get("sub_category_id"),
                item.get("sub_category_name"),
                item.get("api_url"),
                item.get("status", "pending")
            )

            self.cursor.execute(query, values)
            self.conn.commit()

        # -------------------------------
        #  Insert into product_detail
        # -------------------------------
        elif item.get("type") == "product_detail":
            query = """
            INSERT INTO product_detail (
                category_name,
                sub_category_id,
                sub_category_name,
                product_id,
                product_name,
                product_url,
                status
            )
            VALUES (%s, %s, %s, %s, %s, %s, %s)
            
            """

            values = (
                item.get("category_name"),
                item.get("sub_category_id"),
                item.get("sub_category_name"),
                item.get("product_id"),
                item.get("product_name"),
                item.get("product_url"),
                item.get("status", "pending")
            )

            self.cursor.execute(query, values)
            self.conn.commit()


        elif item.get("type") == "product_info":
            query = """
            INSERT INTO product_info (product_id, product_name, url, img_url, price, description, shipping_weight, in_stock, specification)
            VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s )
            
            """

            values = (
                item.get("product_id"),
                item.get("product_name"),
                item.get("url"),
                item.get("img_url"),
                item.get("price"),
                item.get("description"),
                item.get("shipping_weight"),
                item.get("in_stock"),
                item.get("specification")
            )

            self.cursor.execute(query, values)
            self.conn.commit()
        

        return item





    # ====================================
    #  Close Connection
    # ====================================
    def close_spider(self, spider):
        self.cursor.close()
        self.conn.close()


        # # return item


        # """Insert each item into MySQL"""
        # try:
        #     sql = """
        #     INSERT INTO tacoma_stores
        #     (category_name, sub_category_name, product_id, product_name, product_url)
        #     VALUES (%s, %s, %s, %s, %s)
        #     """
        #     # print("process_items : ", item)
        #     values = (
        #         item.get('category_name'),
        #         item.get('sub_category_name'),
        #         item.get('product_id'),
        #         item.get('product_name'),
        #         item.get('product_url')
        #     )
        #     self.cursor.execute(sql, values)
        #     self.conn.commit()
        # except Error as e:
        #     spider.logger.error(f"Error inserting item: {e}")
        # return item


    # -------------------------------
    # Fetch all categories from DB
    # -------------------------------
    # def fetch_all_categories(self):
    #     conn = mysql.connector.connect(
    #         host="localhost",
    #         user="root",
    #         password="actowiz",
    #         database="tacoma_scrapy_db",
    #         port="3306"
    #     )
    #     cursor = conn.cursor(dictionary=True)
    #     cursor.execute("SELECT * FROM all_category WHERE status='pending'")
    #     rows = cursor.fetchall()
    #     cursor.close()
    #     conn.close()
    #     return rows








# class TacomaProductScrapePipeline:

#     def __init__(self):
#         # Database configuration
#         self.host = "localhost"
#         self.user = "root"
#         self.password = "actowiz"  # replace with your MySQL password
#         self.port = "3306"
#         self.database = "tacoma_scrapy_db"

#     def open_spider(self, spider):
#         """Runs when spider starts"""
#         try:
#             # Connect to MySQL server
#             self.conn = mysql.connector.connect(
#                 host=self.host,
#                 user=self.user,
#                 password=self.password,
#                 port=self.port
#             )
#             self.cursor = self.conn.cursor()

#             # Create database if not exists
#             self.cursor.execute(f"CREATE DATABASE IF NOT EXISTS {self.database}")
#             self.conn.database = self.database

#             # Create table if not exists with UNIQUE on city_link
#             self.cursor.execute("""
#             CREATE TABLE IF NOT EXISTS tacoma_stores (
#                 id INT AUTO_INCREMENT PRIMARY KEY,
#                 category_name VARCHAR(255),
#                 sub_category_name VARCHAR(255),
#                 product_id VARCHAR(255),
#                 product_name VARCHAR(255) ,
#                 product_url TEXT
#             )
#             """)
#             self.conn.commit()
#         except Error as e:
#             spider.logger.error(f"Error connecting to MySQL: {e}")

#     def process_item(self, item, spider):
#         # return item


#         """Insert each item into MySQL"""
#         try:
#             sql = """
#             INSERT INTO tacoma_stores
#             (category_name, sub_category_name, product_id, product_name, product_url)
#             VALUES (%s, %s, %s, %s, %s)
#             """
#             # print("process_items : ", item)
#             values = (
#                 item.get('category_name'),
#                 item.get('sub_category_name'),
#                 item.get('product_id'),
#                 item.get('product_name'),
#                 item.get('product_url')
#             )
#             self.cursor.execute(sql, values)
#             self.conn.commit()
#         except Error as e:
#             spider.logger.error(f"Error inserting item: {e}")
#         return item

