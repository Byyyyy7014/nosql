from pymongo import MongoClient
from pymongo.errors import PyMongoError

MONGO_URI = "mongodb://127.0.0.1:27017/?replicaSet=rs0"
DB_NAME = "exam_12403030223"


def main():
    client = MongoClient(
        MONGO_URI,
        serverSelectionTimeoutMS=10000
    )

    try:
        client.admin.command("ping")

        db = client[DB_NAME]
        courses = db["courses"]

        # 查询张老师授课且状态为OPEN的课程
        query = {
            "teacher": "张老师",
            "status": "OPEN"
        }

        # 保留课程编号、课程名称和章节数组
        projection = {
            "_id": 1,
            "courseName": 1,
            "chapters": 1
        }

        results = courses.find(
            query,
            projection
        ).sort("_id", 1)

        print("========== 张老师正在开放的课程 ==========")

        count = 0

        for course in results:
            count += 1

            # 根据chapters数组实际计算章节数量
            chapter_count = len(course["chapters"])

            print("课程编号：", course["_id"])
            print("课程名称：", course["courseName"])
            print("章节数量：", chapter_count)
            print("-" * 45)

        print("符合条件的课程总数：", count)

    except PyMongoError as e:
        print("查询失败：", e)

    finally:
        client.close()


if __name__ == "__main__":
    main()