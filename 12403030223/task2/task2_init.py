from pymongo import MongoClient
from pymongo.errors import PyMongoError

MONGO_URI = "mongodb://127.0.0.1:27017/?replicaSet=rs0"
DB_NAME = "exam_12403030223"

BOOK_ID = "BOOK-12403030223"

# 本人参数
STOCK = 8
BUY = 3


def main():
    client = MongoClient(
        MONGO_URI,
        serverSelectionTimeoutMS=10000
    )

    try:
        client.admin.command("ping")

        db = client[DB_NAME]

        inventory = db["inventory"]
        orders = db["orders"]

        # 初始化库存文档
        inventory_doc = {
            "_id": BOOK_ID,
            "title": "NoSQL数据库教材",
            "stock": STOCK
        }

        # 清理本题旧测试数据，建立初始状态
        inventory.replace_one(
            {"_id": BOOK_ID},
            inventory_doc,
            upsert=True
        )

        orders.delete_many({})

        print("========== 第二题初始化完成 ==========")
        print("数据库名称：", DB_NAME)
        print("库存集合：inventory")
        print("订单集合：orders")
        print("教材编号：", BOOK_ID)
        print("教材名称：NoSQL数据库教材")
        print("初始库存：", STOCK)
        print("购买数量：", BUY)

        print("\n========== 当前库存数据 ==========")
        print(inventory.find_one({"_id": BOOK_ID}))

        print("\n当前订单数量：", orders.count_documents({}))

    except PyMongoError as e:
        print("初始化失败：", e)

    finally:
        client.close()


if __name__ == "__main__":
    main()