
import time

from redis.cluster import RedisCluster, ClusterNode
from redis.exceptions import RedisError


# ==================== Redis Cluster连接配置 ====================

STARTUP_NODES = [
    ClusterNode("127.0.0.1", 30223),
    ClusterNode("127.0.0.1", 30224),
    ClusterNode("127.0.0.1", 30225)
]

# 个人参数
SID = "12403030223"
KEY_PREFIX = f"exam:{SID}:"

# String会话键
SESSION_KEY = KEY_PREFIX + "session"

# 自定义会话值
SESSION_VALUE = f"session-{SID}"

# 过期时间：5秒
EXPIRE_SECONDS = 5


def main():

    redis_client = None

    try:
        # 连接Redis Cluster
        redis_client = RedisCluster(
            startup_nodes=STARTUP_NODES,
            decode_responses=True
        )

        print("========== 第三题第四问：String会话过期管理 ==========")

        # 1. 创建会话键并设置5秒过期时间
        redis_client.set(
            SESSION_KEY,
            SESSION_VALUE,
            ex=EXPIRE_SECONDS
        )

        print("\n========== 1. 创建会话键 ==========")
        print("Redis键名：", SESSION_KEY)
        print("会话值：", redis_client.get(SESSION_KEY))

        # 2. 查询会话键TTL
        initial_ttl = redis_client.ttl(SESSION_KEY)

        print("\n========== 2. 查询初始TTL ==========")
        print("设置的过期时间：", EXPIRE_SECONDS, "秒")
        print("当前剩余TTL：", initial_ttl, "秒")

        # 3. 过期前检查数据类型
        initial_type = redis_client.type(SESSION_KEY)

        print("\n========== 3. 过期前检查数据类型 ==========")
        print("会话键数据类型：", initial_type)

        # 4. 等待6秒，超过设置的5秒过期时间
        print("\n========== 4. 等待会话自动过期 ==========")
        print("开始等待6秒...")

        time.sleep(6)

        print("等待结束。")

        # 5. 再次检查会话键
        exists_after = redis_client.exists(SESSION_KEY)
        ttl_after = redis_client.ttl(SESSION_KEY)
        value_after = redis_client.get(SESSION_KEY)

        print("\n========== 5. 过期后检查 ==========")
        print("会话键是否存在：", bool(exists_after))
        print("过期后TTL：", ttl_after)
        print("过期后会话值：", value_after)

        # 6. 结果核验
        print("\n========== 6. 结果核验 ==========")

        checks = {
            "会话键创建成功": initial_ttl > 0,
            "会话值正确": SESSION_VALUE == f"session-{SID}",
            "过期前数据类型为String": initial_type == "string",
            "过期后键不存在": exists_after == 0,
            "过期后TTL为-2": ttl_after == -2,
            "过期后无法读取会话值": value_after is None
        }

        for name, result in checks.items():
            print(f"{name}：{'通过' if result else '未通过'}")

        if all(checks.values()):
            print("\nString会话过期核验：全部通过")
        else:
            print("\nString会话过期核验：未通过")

    except RedisError as e:
        print("Redis操作失败：", e)

    finally:
        if redis_client is not None:
            redis_client.close()


if __name__ == "__main__":
    main()
