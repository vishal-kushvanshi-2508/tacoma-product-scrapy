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

            # Create table if not exists with UNIQUE on city_link
            self.cursor.execute("""
            CREATE TABLE IF NOT EXISTS tacoma_stores (
                id INT AUTO_INCREMENT PRIMARY KEY,
                category_name VARCHAR(255),
                sub_category_name VARCHAR(255),
                product_id VARCHAR(255),
                product_name VARCHAR(255) ,
                product_url TEXT
            )
            """)
            self.conn.commit()
        except Error as e:
            spider.logger.error(f"Error connecting to MySQL: {e}")

    def process_item(self, item, spider):
        # return item


        """Insert each item into MySQL"""
        try:
            sql = """
            INSERT INTO tacoma_stores
            (category_name, sub_category_name, product_id, product_name, product_url)
            VALUES (%s, %s, %s, %s, %s)
            """
            # print("process_items : ", item)
            values = (
                item.get('category_name'),
                item.get('sub_category_name'),
                item.get('product_id'),
                item.get('product_name'),
                item.get('product_url')
            )
            self.cursor.execute(sql, values)
            self.conn.commit()
        except Error as e:
            spider.logger.error(f"Error inserting item: {e}")
        return item
