
from pymongo import MongoClient
from pymongo.errors import PyMongoError
from pprint import pprint
from uuid import uuid4


# ==================== 基本配置 ====================

MONGO_URI = "mongodb://127.0.0.1:27017/?replicaSet=rs0"
DB_NAME = "exam_12403030223"

BOOK_ID = "BOOK-12403030223"
STUDENT_ID = "12403030223"

# 个人参数
A = 2
C = 3

STOCK = 5 + C
BUY = 1 + A

# T4连续订购次数
T4_ATTEMPTS = STOCK // BUY + 1


# ==================== 业务异常 ====================

class BusinessError(Exception):
    pass


# ==================== 事务订购函数 ====================

def order_book(client, request_id, force_error=False):
    """
    在同一个事务中完成库存扣减和订单插入。

    force_error=True：
    库存扣减成功后、订单插入前主动抛出异常。
    """

    db = client[DB_NAME]
    inventory = db["inventory"]
    orders = db["orders"]

    try:
        with client.start_session() as session:
            with session.start_transaction():

                # 1. 原子扣减库存
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

                # 2. 模拟异常
                if force_error:
                    raise RuntimeError(
                        "主动模拟异常：订单插入前发生错误"
                    )

                # 3. 插入订单
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


# ==================== 场景初始化 ====================

def reset_scenario(db, initial_stock):
    """
    每个测试场景开始前独立初始化库存和订单。
    """

    db["inventory"].replace_one(
        {"_id": BOOK_ID},
        {
            "_id": BOOK_ID,
            "title": "NoSQL数据库教材",
            "stock": initial_stock
        },
        upsert=True
    )

    db["orders"].delete_many({})


# ==================== 场景测试 ====================

def run_scenario(client, scenario_name, initial_stock,
                 attempts, force_error=False):

    db = client[DB_NAME]

    print("\n" + "=" * 65)
    print(f"开始测试场景：{scenario_name}")
    print("=" * 65)

    # 重置本场景数据
    reset_scenario(db, initial_stock)

    success_count = 0
    failure_count = 0

    # 连续执行订购
    for i in range(attempts):

        request_id = (
            f"{scenario_name}-{i + 1}-{uuid4().hex}"
        )

        result = order_book(
            client,
            request_id,
            force_error=force_error
        )

        print(f"\n第{i + 1}次订购结果：")
        print(result["message"])

        if result["success"]:
            success_count += 1
        else:
            failure_count += 1

    # 查询最终库存
    final_book = db["inventory"].find_one(
        {"_id": BOOK_ID}
    )

    final_stock = (
        final_book["stock"] if final_book else None
    )

    # 查询订单数量
    order_count = db["orders"].count_documents({})

    # 计算预期值
    expected_success = (
        0 if force_error
        else min(attempts, initial_stock // BUY)
    )

    expected_failure = attempts - expected_success

    expected_stock = (
        initial_stock - expected_success * BUY
    )

    expected_orders = expected_success

    # 判断实际结果是否符合预期
    passed = (
        success_count == expected_success
        and failure_count == expected_failure
        and final_stock == expected_stock
        and order_count == expected_orders
    )

    # 输出场景统计
    print("\n---------- 场景统计 ----------")
    print("场景编号：", scenario_name)
    print("初始库存：", initial_stock)
    print("购买数量：", BUY)
    print("订购尝试次数：", attempts)
    print("成功次数：", success_count)
    print("失败次数：", failure_count)
    print("最终库存：", final_stock)
    print("订单数量：", order_count)

    print("预期成功次数：", expected_success)
    print("预期失败次数：", expected_failure)
    print("预期最终库存：", expected_stock)
    print("预期订单数量：", expected_orders)

    print("场景核验结果：", "通过" if passed else "未通过")

    return passed


# ==================== 主程序 ====================

def main():

    client = MongoClient(
        MONGO_URI,
        serverSelectionTimeoutMS=10000
    )

    try:
        client.admin.command("ping")

        print("MongoDB连接成功！")
        print("数据库名称：", DB_NAME)
        print("个人学号：", STUDENT_ID)
        print("初始库存参数：", STOCK)
        print("单次购买数量：", BUY)
        print("T4订购次数：", T4_ATTEMPTS)

        results = []

        # T1：库存充足，正常订购一次
        results.append(
            run_scenario(
                client,
                "T1",
                initial_stock=STOCK,
                attempts=1
            )
        )

        # T2：库存不足
        results.append(
            run_scenario(
                client,
                "T2",
                initial_stock=BUY - 1,
                attempts=1
            )
        )

        # T3：库存扣减后主动制造异常
        results.append(
            run_scenario(
                client,
                "T3",
                initial_stock=STOCK,
                attempts=1,
                force_error=True
            )
        )

        # T4：连续订购，直到出现库存不足
        results.append(
            run_scenario(
                client,
                "T4",
                initial_stock=STOCK,
                attempts=T4_ATTEMPTS
            )
        )

        # 汇总结果
        print("\n" + "=" * 65)
        print("第二题四种场景最终汇总")
        print("=" * 65)

        scenario_names = ["T1", "T2", "T3", "T4"]

        for name, passed in zip(scenario_names, results):
            print(
                f"{name}：{'通过' if passed else '未通过'}"
            )

        print(
            "\n总体验证结果：",
            "全部通过" if all(results) else "存在未通过场景"
        )

        print("\n第二题测试完成。")

    except PyMongoError as e:
        print("数据库连接或执行异常：", e)

    finally:
        client.close()


if __name__ == "__main__":
    main()
