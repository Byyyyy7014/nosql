from pymongo import MongoClient
from pymongo.errors import PyMongoError

MONGO_URI = "mongodb://127.0.0.1:27017/?replicaSet=rs0"
DB_NAME = "exam_12403030223"

COURSE_ID = "COURSE-12403030223-01"


def main():
    client = MongoClient(
        MONGO_URI,
        serverSelectionTimeoutMS=10000
    )

    try:
        client.admin.command("ping")

        courses = client[DB_NAME]["courses"]

        course = courses.find_one(
            {"_id": COURSE_ID}
        )

        if course is None:
            print("核验失败：未找到指定课程！")
            return

        # 统计章节数量
        chapters = course["chapters"]
        total_count = len(chapters)

        # 统计CH03出现次数
        ch03_count = sum(
            1 for chapter in chapters
            if chapter["chapterId"] == "CH03"
        )

        # 查找CH02和CH03
        ch02 = next(
            (chapter for chapter in chapters
             if chapter["chapterId"] == "CH02"),
            None
        )

        ch03 = next(
            (chapter for chapter in chapters
             if chapter["chapterId"] == "CH03"),
            None
        )

        # 检查各项要求
        checks = {
            "CH02标题正确": (
                ch02 is not None
                and ch02["title"] == "Redis基础与应用-23"
            ),
            "CH03存在且数量唯一": (
                ch03 is not None and ch03_count == 1
            ),
            "最终章节总数为3": total_count == 3,
            "teacher字段保持不变": (
                course["teacher"] == "张老师"
            ),
            "status字段保持不变": (
                course["status"] == "OPEN"
            ),
            "课程名称保持不变": (
                course["courseName"] == "NoSQL数据库"
            )
        }

        print("========== 第一题最终核验 ==========")
        print("课程编号：", course["_id"])
        print("课程名称：", course["courseName"])
        print("教师：", course["teacher"])
        print("课程状态：", course["status"])
        print("章节总数：", total_count)
        print("CH03出现次数：", ch03_count)

        print("\n========== 逐项核验结果 ==========")

        for name, passed in checks.items():
            print(f"{name}：{'通过' if passed else '未通过'}")

        all_passed = all(checks.values())

        print("\n========== 最终结论 ==========")
        print("第一题核验结果：", "全部通过" if all_passed else "存在未通过项目")

        print("\n========== 局部更新的优点 ==========")
        print("1. 只修改目标字段，不影响文档中的其他字段。")
        print("2. 减少客户端读取和传输的数据量。")
        print("3. 降低整个文档被覆盖或误修改的风险。")
        print("4. MongoDB单文档更新具有原子性。")

    except PyMongoError as e:
        print("核验失败：", e)

    finally:
        client.close()


if __name__ == "__main__":
    main()