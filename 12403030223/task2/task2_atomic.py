from pymongo import MongoClient
from pymongo.errors import PyMongoError

MONGO_URI = "mongodb://127.0.0.1:27017/?replicaSet=rs0"
DB_NAME = "exam_12403030223"

BOOK_ID = "BOOK-12403030223"
BUY = 3


def deduct_stock(inventory, book_id, quantity):
    """
    原子扣减库存：
    只有教材存在且库存足够时，才执行扣减。
    """

    if quantity <= 0:
        return {
            "success": False,
            "message": "购买数量必须大于0"
        }

    try:
        result = inventory.update_one(
            {
                "_id": book_id,
                "stock": {"$gte": quantity}
            },
            {
                "$inc": {"stock": -quantity}
            }
        )

        if result.modified_count == 1:
            return {
                "success": True,
                "message": "库存扣减成功"
            }

        # 更新没有匹配到文档，仅用于区分不存在和库存不足
        book = inventory.find_one(
            {"_id": book_id},
            {"stock": 1}
        )

        if book is None:
            return {
                "success": False,
                "message": "教材不存在"
            }

        return {
            "success": False,
            "message": "库存不足"
        }

    except PyMongoError as e:
        return {
            "success": False,
            "message": f"数据库异常：{e}"
        }


def main():
    client = MongoClient(
        MONGO_URI,
        serverSelectionTimeoutMS=10000
    )

    try:
        client.admin.command("ping")

        inventory = client[DB_NAME]["inventory"]

        print("========== 原子扣减测试 ==========")

        result = deduct_stock(
            inventory,
            BOOK_ID,
            BUY
        )

        print("扣减结果：", result["message"])
        print("是否成功：", result["success"])

        print("\n========== 当前库存 ==========")

        book = inventory.find_one(
            {"_id": BOOK_ID}
        )

        print(book)

    except PyMongoError as e:
        print("数据库连接失败：", e)

    finally:
        client.close()


if __name__ == "__main__":
    main()