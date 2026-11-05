
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

# Set章节记录键
CHAPTER_KEY = KEY_PREFIX + "chapters"


def main():

    redis_client = None

    try:
        # 连接Redis Cluster
        redis_client = RedisCluster(
            startup_nodes=STARTUP_NODES,
            decode_responses=True
        )

        print("========== 第三题第二问：Set章节记录管理 ==========")

        # 清理本题专用Set键，保证每次运行结果一致
        redis_client.delete(CHAPTER_KEY)

        # 按题目要求依次提交章节
        chapters = ["CH01", "CH02", "CH02", "CH03"]

        print("\n========== 1. 依次提交章节 ==========")

        counts = []

        for chapter in chapters:
            redis_client.sadd(CHAPTER_KEY, chapter)

            count = redis_client.scard(CHAPTER_KEY)
            counts.append(count)

            print(f"提交章节：{chapter}，当前成员数量：{count}")

        # 2. 输出最终所有成员
        members = redis_client.smembers(CHAPTER_KEY)

        print("\n========== 2. 最终Set成员 ==========")
        print("最终成员：", sorted(members))
        print("最终成员数量：", len(members))

        # 3. 判断指定章节是否存在
        has_ch02 = redis_client.sismember(CHAPTER_KEY, "CH02")
        has_ch04 = redis_client.sismember(CHAPTER_KEY, "CH04")

        print("\n========== 3. 章节存在性判断 ==========")
        print("是否包含CH02：", bool(has_ch02))
        print("是否包含CH04：", bool(has_ch04))

        # 4. 验证重复提交不增加成员数量
        duplicate_verified = (
            counts[1] == counts[2]
            and counts == [1, 2, 2, 3]
        )

        print("\n========== 4. 重复提交验证 ==========")
        print("第二次提交CH02前成员数量：", counts[1])
        print("第二次提交CH02后成员数量：", counts[2])
        print("重复提交是否增加成员数量：", counts[2] > counts[1])

        # 5. 最终核验
        expected_members = {"CH01", "CH02", "CH03"}

        print("\n========== 5. 结果核验 ==========")

        if (
            set(members) == expected_members
            and counts == [1, 2, 2, 3]
            and has_ch02 == 1
            and has_ch04 == 0
            and duplicate_verified
        ):
            print("Set章节记录核验：全部通过")
        else:
            print("Set章节记录核验：未通过")

    except RedisError as e:
        print("Redis操作失败：", e)

    finally:
        if redis_client is not None:
            redis_client.close()


if __name__ == "__main__":
    main()
