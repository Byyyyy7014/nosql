
from pymongo import MongoClient
from pymongo.errors import PyMongoError
from pprint import pprint
from uuid import uuid4


MONGO_URI = "mongodb://127.0.0.1:27017/?replicaSet=rs0"
DB_NAME = "exam_12403030223"

BOOK_ID = "BOOK-12403030223"
STUDENT_ID = "12403030223"
BUY = 3


class BusinessError(Exception):
    """订购业务异常"""
    pass


def order_book(client, request_id, force_error=False):
    """
    在同一个MongoDB事务中完成：
    1. 原子扣减库存
    2. 插入订单

    force_error=True时，在库存扣减后、
    订单插入前主动抛出异常，验证事务回滚。
    """

    db = client[DB_NAME]
    inventory = db["inventory"]
    orders = db["orders"]

    try:
        with client.start_session() as session:
            with session.start_transaction():

                # 第一步：原子扣减库存
                result = inventory.update_one(
                    {
                        "_id": BOOK_ID,
                        "stock": {"$gte": BUY}
                    },
                    {
                        "$inc": {"stock": -BUY}
                    },
                    session=session
                )

                if result.modified_count != 1:

                    # 区分教材不存在和库存不足
                    book = inventory.find_one(
                        {"_id": BOOK_ID},
                        {"stock": 1},
                        session=session
                    )

                    if book is None:
                        raise BusinessError("教材不存在")

                    raise BusinessError("库存不足")

                print("库存扣减成功，当前事务尚未提交。")

                # 第二步：模拟异常
                if force_error:
                    raise RuntimeError(
                        "主动模拟异常：订单插入前发生错误"
                    )

                # 第三步：插入订单
                order = {
                    "_id": request_id,
                    "bookId": BOOK_ID,
                    "studentId": STUDENT_ID,
                    "quantity": BUY
                }

                orders.insert_one(
                    order,
                    session=session
                )

        # 正常离开事务上下文后自动提交
        return {
            "success": True,
            "message": "订购成功",
            "requestId": request_id
        }

    except BusinessError as e:
        return {
            "success": False,
            "message": str(e),
            "requestId": request_id
        }

    except RuntimeError as e:
        return {
            "success": False,
            "message": str(e),
            "requestId": request_id
        }

    except PyMongoError as e:
        return {
            "success": False,
            "message": f"数据库异常：{e}",
            "requestId": request_id
        }


def main():
    client = MongoClient(
        MONGO_URI,
        serverSelectionTimeoutMS=10000
    )

    try:
        client.admin.command("ping")

        print("========== 异常回滚测试 ==========")

        # 强制模拟订单插入前发生异常
        error_result = order_book(
            client,
            "TEST-ERROR-" + uuid4().hex,
            force_error=True
        )

        print(error_result)

        db = client[DB_NAME]

        # 输出回滚后的库存
        print("\n========== 回滚后的库存 ==========")

        book = db["inventory"].find_one(
            {"_id": BOOK_ID}
        )
        pprint(book, sort_dicts=False)

        # 输出当前全部订单
        print("\n========== 当前订单 ==========")

        order_list = list(db["orders"].find())

        for order in order_list:
            pprint(order, sort_dicts=False)

        print("\n当前订单数量：", len(order_list))

    except PyMongoError as e:
        print("数据库连接失败：", e)

    finally:
        client.close()


if __name__ == "__main__":
    main()
