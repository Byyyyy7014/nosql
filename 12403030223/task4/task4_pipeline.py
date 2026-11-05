
import time
from redis.cluster import RedisCluster, ClusterNode
from redis.exceptions import RedisError


# ==================== 个人参数 ====================

SID = "12403030223"

# N = 1000 + 100C + S = 1323
S = 23
C = 3
N = 1000 + 100 * C + S

# Pipeline每批最多执行100条命令
Q = 100

KEY_PREFIX = f"exam:{SID}:"

# Redis Cluster连接配置
STARTUP_NODES = [
    ClusterNode("127.0.0.1", 30223),
    ClusterNode("127.0.0.1", 30224),
    ClusterNode("127.0.0.1", 30225)
]


def create_client():
    """创建Redis Cluster连接。"""
    return RedisCluster(
        startup_nodes=STARTUP_NODES,
        decode_responses=True
    )


def sequential_write(client):
    """方案甲：逐条同步执行SET命令。"""

    print("\n========== 方案甲：逐条同步写入 ==========")

    start_time = time.perf_counter()

    for i in range(1, N + 1):
        key = f"{KEY_PREFIX}seq:{i}"
        value = f"value-{SID}-{i}"

        client.set(key, value)

    elapsed = time.perf_counter() - start_time

    print("写入命令总数：", N)
    print("写入方式：逐条执行SET")
    print(f"执行耗时：{elapsed:.6f}秒")

    return elapsed


def pipeline_write(client):
    """方案乙：使用普通Pipeline分批写入。"""

    print("\n========== 方案乙：Pipeline批量写入 ==========")

    start_time = time.perf_counter()

    batch_count = 0

    for batch_start in range(1, N + 1, Q):

        batch_end = min(batch_start + Q - 1, N)

        # 显式关闭事务，使用普通Pipeline
        pipe = client.pipeline(transaction=False)

        for i in range(batch_start, batch_end + 1):
            key = f"{KEY_PREFIX}pipe:{i}"
            value = f"value-{SID}-{i}"

            pipe.set(key, value)

        # 执行当前批次并接收全部回复
        results = pipe.execute()

        batch_count += 1

        # 检查当前批次执行结果
        if len(results) != batch_end - batch_start + 1:
            raise RuntimeError(
                f"第{batch_count}批回复数量异常"
            )

        if not all(result is True for result in results):
            raise RuntimeError(
                f"第{batch_count}批存在写入失败"
            )

        print(
            f"第{batch_count:02d}批："
            f"写入{batch_end - batch_start + 1}条，"
            f"范围{i if False else batch_start}-{batch_end}"
        )

    elapsed = time.perf_counter() - start_time

    print("写入命令总数：", N)
    print("每批最大命令数：", Q)
    print("实际批次数：", batch_count)
    print("最后一批命令数：", N % Q if N % Q != 0 else Q)
    print("写入方式：普通Pipeline，transaction=False")
    print(f"执行耗时：{elapsed:.6f}秒")

    return elapsed, batch_count


def verify_data(client, key_type):
    """验证写入的数据数量和值是否正确。"""

    print(f"\n========== {key_type}数据完整性验证 ==========")

    success_count = 0
    error_count = 0

    for i in range(1, N + 1):

        key = f"{KEY_PREFIX}{key_type}:{i}"
        expected_value = f"value-{SID}-{i}"

        actual_value = client.get(key)

        if actual_value == expected_value:
            success_count += 1
        else:
            error_count += 1
            if error_count <= 5:
                print(
                    f"数据异常：{key}，"
                    f"预期={expected_value}，"
                    f"实际={actual_value}"
                )

    print("预期数据数量：", N)
    print("正确数据数量：", success_count)
    print("错误数据数量：", error_count)

    passed = success_count == N and error_count == 0

    print("完整性核验：", "通过" if passed else "未通过")

    return passed


def main():

    client = None

    try:
        print("========== 第四题：Redis Pipeline性能比较 ==========")
        print("个人学号：", SID)
        print("S：", S)
        print("C：", C)
        print("N：", N)
        print("Q：", Q)
        print("预计Pipeline批次数：", (N + Q - 1) // Q)

        client = create_client()

        # 先执行方案甲
        sequential_time = sequential_write(client)

        # 再执行方案乙
        pipeline_time, batch_count = pipeline_write(client)

        # 两种写入方式分别进行完整性验证
        sequential_passed = verify_data(client, "seq")
        pipeline_passed = verify_data(client, "pipe")

        # 性能比较
        print("\n========== 性能比较结果 ==========")

        print(f"方案甲逐条写入耗时：{sequential_time:.6f}秒")
        print(f"方案乙Pipeline耗时：{pipeline_time:.6f}秒")

        if pipeline_time < sequential_time:
            print("性能比较：Pipeline写入速度更快。")
            print(
                f"耗时约为逐条写入的"
                f"{pipeline_time / sequential_time:.2%}"
            )
        elif pipeline_time > sequential_time:
            print("性能比较：本次测试中逐条写入速度更快。")
            print(
                f"Pipeline耗时约为逐条写入的"
                f"{pipeline_time / sequential_time:.2%}"
            )
        else:
            print("性能比较：两种方式耗时相同。")

        print("\n========== 最终核验 ==========")

        checks = {
            "方案甲写入数量正确": N == 1323,
            "Pipeline批次数正确": batch_count == 14,
            "最后一批数量正确": N - (batch_count - 1) * Q == 23,
            "方案甲数据完整": sequential_passed,
            "方案乙数据完整": pipeline_passed
        }

        for name, result in checks.items():
            print(f"{name}：{'通过' if result else '未通过'}")

        if all(checks.values()):
            print("\n第四题Pipeline实验：全部核验通过")
        else:
            print("\n第四题Pipeline实验：存在未通过项目")

    except (RedisError, RuntimeError) as e:
        print("\n实验执行失败：", e)

    finally:
        if client is not None:
            client.close()


if __name__ == "__main__":
    main()
