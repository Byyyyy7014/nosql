
from pymongo import MongoClient
from pymongo.errors import PyMongoError


# 数据库连接配置 =

MONGO_URI = "mongodb://127.0.0.1:27017/?replicaSet=rs0"
DB_NAME = "exam_12403030223"


def main():
    client = MongoClient(
        MONGO_URI,
        serverSelectionTimeoutMS=10000
    )

    try:
        # 检查数据库连接
        client.admin.command("ping")
        print("MongoDB连接成功！")

        # 选择个人数据库和课程集合
        db = client[DB_NAME]
        courses = db["courses"]

        # 防止重复初始化覆盖已有数据
        existing_count = courses.count_documents({})

        if existing_count > 0:
            print("检测到courses集合中已有数据。")
            print("当前课程数量：", existing_count)
            print("为避免覆盖已有数据，本次不重复初始化。")
            return

        # 初始化课程数据

        course_data = [
            {
                "_id": "COURSE-12403030223-01",
                "courseName": "NoSQL数据库",
                "teacher": "张老师",
                "status": "OPEN",
                "chapters": [
                    {
                        "chapterId": "CH01",
                        "title": "MongoDB基础",
                        "hours": 2
                    },
                    {
                        "chapterId": "CH02",
                        "title": "Redis基础",
                        "hours": 2
                    }
                ]
            },
            {
                "_id": "COURSE-12403030223-02",
                "courseName": "数据库原理",
                "teacher": "张老师",
                "status": "CLOSED",
                "chapters": [
                    {
                        "chapterId": "CH01",
                        "title": "关系模型",
                        "hours": 2
                    }
                ]
            },
            {
                "_id": "COURSE-12403030223-03",
                "courseName": "机器学习",
                "teacher": "李老师",
                "status": "OPEN",
                "chapters": [
                    {
                        "chapterId": "CH01",
                        "title": "分类",
                        "hours": 2
                    },
                    {
                        "chapterId": "CH02",
                        "title": "聚类",
                        "hours": 2
                    }
                ]
            }
        ]

        # 插入初始化数据
        result = courses.insert_many(course_data)

        print("\n========== 课程初始化完成 ==========")
        print("数据库名称：", DB_NAME)
        print("集合名称：courses")
        print("成功插入课程数量：", len(result.inserted_ids))

        # 输出初始化后的课程数据
        print("\n========== 初始化数据 ==========")

        for course in courses.find().sort("_id", 1):
            print(course)

    except PyMongoError as e:
        print("初始化失败：", e)

    finally:
        client.close()


if __name__ == "__main__":
    main()
