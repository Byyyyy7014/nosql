
from redis.cluster import RedisCluster, ClusterNode
from redis.exceptions import RedisError


# ==================== Redis Cluster连接配置 ====================

STARTUP_NODES = [
    ClusterNode("127.0.0.1", 30223),
    ClusterNode("127.0.0.1", 30224),
    ClusterNode("127.0.0.1", 30225)
]

# 个人信息参数
SID = "12403030223"
COURSE_ID = "COURSE-12403030223-01"
KEY_PREFIX = f"exam:{SID}:"

# Hash学生信息键
STUDENT_KEY = KEY_PREFIX + "student"


def main():

    redis_client = None

    try:
        # 连接Redis Cluster
        redis_client = RedisCluster(
            startup_nodes=STARTUP_NODES,
            decode_responses=True
        )

        print("========== 第三题第一问：Hash学生信息管理 ==========")

        # 1. 创建学生Hash信息
        student_info = {
            "studentId": SID,
            "name": "张三",
            "className": "大数据管理与应用2班",
            "courseId": COURSE_ID,
            "status": "learning"
        }

        redis_client.hset(STUDENT_KEY, mapping=student_info)

        print("\n========== 1. 创建学生信息 ==========")
        print("Redis键名：", STUDENT_KEY)
        print("初始Hash信息：")

        for field, value in redis_client.hgetall(STUDENT_KEY).items():
            print(f"{field}: {value}")

        # 2. 修改学习状态
        redis_client.hset(STUDENT_KEY, "status", "completed")

        print("\n========== 2. 修改学习状态 ==========")
        print("status修改为：", redis_client.hget(STUDENT_KEY, "status"))

        # 3. 单独读取指定字段
        print("\n========== 3. 单独读取字段 ==========")
        student_name = redis_client.hget(STUDENT_KEY, "name")
        student_status = redis_client.hget(STUDENT_KEY, "status")

        print("学生姓名：", student_name)
        print("当前学习状态：", student_status)

        # 4. 输出完整Hash信息
        print("\n========== 4. 输出完整Hash信息 ==========")
        final_info = redis_client.hgetall(STUDENT_KEY)

        for field, value in final_info.items():
            print(f"{field}: {value}")

        # 5. 结果核验
        print("\n========== 5. 结果核验 ==========")

        if (
            final_info.get("studentId") == SID
            and final_info.get("name") == "张三"
            and final_info.get("className") == "大数据管理与应用2班"
            and final_info.get("courseId") == COURSE_ID
            and final_info.get("status") == "completed"
        ):
            print("Hash学生信息核验：全部通过")
        else:
            print("Hash学生信息核验：未通过")

    except RedisError as e:
        print("Redis操作失败：", e)

    finally:
        if redis_client is not None:
            redis_client.close()


if __name__ == "__main__":
    main()
