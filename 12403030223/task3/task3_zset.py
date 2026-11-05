
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
C = 3
KEY_PREFIX = f"exam:{SID}:"

# Sorted Set排行榜键
RANKING_KEY = KEY_PREFIX + "ranking"

# 本人成绩：70 + C
MY_SCORE = 70 + C

# 本人排行榜成员名称
MY_MEMBER = f"Student:{SID}"


def main():

    redis_client = None

    try:
        # 连接Redis Cluster
        redis_client = RedisCluster(
            startup_nodes=STARTUP_NODES,
            decode_responses=True
        )

        print("========== 第三题第三问：Sorted Set成绩排行榜 ==========")

        # 1. 初始化排行榜
        # 清理本题专用排行榜键，保证每次运行结果一致
        redis_client.delete(RANKING_KEY)

        scores = {
            MY_MEMBER: MY_SCORE,
            "demo:01": 85,
            "demo:02": 90,
            "demo:03": 60,
            "demo:04": 80
        }

        redis_client.zadd(RANKING_KEY, scores)

        print("\n========== 1. 初始化成绩 ==========")
        print("排行榜成员数量：", redis_client.zcard(RANKING_KEY))

        for member, score in scores.items():
            print(f"{member}: {score}")

        # 2. 查询初始成绩降序前三名
        print("\n========== 2. 初始排行榜前三名 ==========")

        initial_top3 = redis_client.zrevrange(
            RANKING_KEY, 0, 2, withscores=True
        )

        for rank, (member, score) in enumerate(initial_top3, start=1):
            print(f"第{rank}名：{member}，成绩：{int(score)}")

        # 3. 给本人增加20分
        print("\n========== 3. 本人成绩增加20分 ==========")

        new_score = redis_client.zincrby(
            RANKING_KEY, 20, MY_MEMBER
        )

        print("本人原始成绩：", MY_SCORE)
        print("本次增加分数：20")
        print("本人更新后成绩：", int(new_score))

        # 4. 查询更新后的排行榜前三名
        print("\n========== 4. 更新后的排行榜前三名 ==========")

        updated_top3 = redis_client.zrevrange(
            RANKING_KEY, 0, 2, withscores=True
        )

        for rank, (member, score) in enumerate(updated_top3, start=1):
            print(f"第{rank}名：{member}，成绩：{int(score)}")

        # 5. 查询本人最新成绩和名次
        print("\n========== 5. 查询本人最新成绩和名次 ==========")

        final_score = redis_client.zscore(RANKING_KEY, MY_MEMBER)

        # ZREVRANK返回从0开始的排名，因此加1转换为正常名次
        rank_index = redis_client.zrevrank(RANKING_KEY, MY_MEMBER)
        final_rank = rank_index + 1 if rank_index is not None else None

        print("本人排行榜成员：", MY_MEMBER)
        print("本人最终成绩：", int(final_score))
        print("本人最终名次：", final_rank)

        # 6. 最终核验
        print("\n========== 6. 结果核验 ==========")

        expected_initial = 73
        expected_final = 93

        checks = {
            "初始成员数量正确": redis_client.zcard(RANKING_KEY) == 5,
            "本人初始成绩正确": MY_SCORE == expected_initial,
            "本人加分后成绩正确": final_score == expected_final,
            "本人名次查询成功": final_rank is not None,
            "排行榜前三名数量正确": len(updated_top3) == 3
        }

        for name, result in checks.items():
            print(f"{name}：{'通过' if result else '未通过'}")

        if all(checks.values()):
            print("\nSorted Set排行榜核验：全部通过")
        else:
            print("\nSorted Set排行榜核验：未通过")

    except RedisError as e:
        print("Redis操作失败：", e)

    finally:
        if redis_client is not None:
            redis_client.close()


if __name__ == "__main__":
    main()
