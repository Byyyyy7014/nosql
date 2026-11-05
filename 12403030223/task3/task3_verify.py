
import time

from redis.cluster import RedisCluster, ClusterNode
from redis.exceptions import RedisError


# ==================== Redis Cluster连接配置 ====================

STARTUP_NODES = [
    ClusterNode("127.0.0.1", 30223),
    ClusterNode("127.0.0.1", 30224),
    ClusterNode("127.0.0.1", 30225)
]

SID = "12403030223"
KEY_PREFIX = f"exam:{SID}:"

# 四种数据结构对应的键
STUDENT_KEY = KEY_PREFIX + "student"
CHAPTER_KEY = KEY_PREFIX + "chapters"
RANKING_KEY = KEY_PREFIX + "ranking"
SESSION_KEY = KEY_PREFIX + "session"


def main():

    redis_client = None

    try:
        # 连接Redis Cluster
        redis_client = RedisCluster(
            startup_nodes=STARTUP_NODES,
            decode_responses=True
        )

        print("========== 第三题最终核验：四种数据结构 ==========")

        # 1. 检查Hash类型
        print("\n========== 1. Hash学生信息 ==========")

        student_type = redis_client.type(STUDENT_KEY)
        student_info = redis_client.hgetall(STUDENT_KEY)

        print("Redis键名：", STUDENT_KEY)
        print("数据类型：", student_type)
        print("学生信息：", student_info)

        # 2. 检查Set类型
        print("\n========== 2. Set章节记录 ==========")

        chapter_type = redis_client.type(CHAPTER_KEY)
        chapter_members = redis_client.smembers(CHAPTER_KEY)

        print("Redis键名：", CHAPTER_KEY)
        print("数据类型：", chapter_type)
        print("章节成员：", sorted(chapter_members))

        # 3. 检查Sorted Set类型
        print("\n========== 3. Sorted Set成绩排行榜 ==========")

        ranking_type = redis_client.type(RANKING_KEY)
        ranking_count = redis_client.zcard(RANKING_KEY)
        my_score = redis_client.zscore(
            RANKING_KEY,
            f"Student:{SID}"
        )

        print("Redis键名：", RANKING_KEY)
        print("数据类型：", ranking_type)
        print("排行榜成员数量：", ranking_count)
        print("本人成绩：", int(my_score) if my_score is not None else None)

        # 4. 重新创建会话键，检查过期前的String类型
        print("\n========== 4. String会话键 ==========")

        redis_client.set(
            SESSION_KEY,
            f"session-{SID}",
            ex=5
        )

        session_type = redis_client.type(SESSION_KEY)
        session_ttl = redis_client.ttl(SESSION_KEY)

        print("Redis键名：", SESSION_KEY)
        print("数据类型：", session_type)
        print("过期前TTL：", session_ttl)

        # 5. 等待会话键过期
        print("\n等待6秒，验证String会话键自动过期...")
        time.sleep(6)

        session_exists = redis_client.exists(SESSION_KEY)
        session_ttl_after = redis_client.ttl(SESSION_KEY)

        print("过期后是否存在：", bool(session_exists))
        print("过期后TTL：", session_ttl_after)

        # 6. 汇总核验
        print("\n========== 5. 四种数据结构最终核验 ==========")

        checks = {
            "Hash类型正确": student_type == "hash",
            "Set类型正确": chapter_type == "set",
            "Sorted Set类型正确": ranking_type == "zset",
            "String类型正确": session_type == "string",
            "String会话自动过期": session_exists == 0 and session_ttl_after == -2,
            "Hash学生信息完整": len(student_info) == 5,
            "Set章节数量正确": len(chapter_members) == 3,
            "Sorted Set成员数量正确": ranking_count == 5,
            "本人成绩正确": my_score == 93
        }

        for name, result in checks.items():
            print(f"{name}：{'通过' if result else '未通过'}")

        if all(checks.values()):
            print("\n第三题四种数据结构最终核验：全部通过")
        else:
            print("\n第三题四种数据结构最终核验：未通过")

    except RedisError as e:
        print("Redis操作失败：", e)

    finally:
        if redis_client is not None:
            redis_client.close()


if __name__ == "__main__":
    main()
