from pymongo import MongoClient
from pymongo.errors import PyMongoError
from pprint import pprint

MONGO_URI = "mongodb://127.0.0.1:27017/?replicaSet=rs0"
DB_NAME = "exam_12403030223"

COURSE_ID = "COURSE-12403030223-01"
NEW_TITLE = "Redis基础与应用-23"


def main():
    client = MongoClient(
        MONGO_URI,
        serverSelectionTimeoutMS=10000
    )

    try:
        client.admin.command("ping")

        courses = client[DB_NAME]["courses"]

        # 仅更新指定课程中chapterId为CH02的章节标题
        result = courses.update_one(
            {
                "_id": COURSE_ID,
                "chapters.chapterId": "CH02"
            },
            {
                "$set": {
                    "chapters.$.title": NEW_TITLE
                }
            }
        )

        print("========== 局部更新执行结果 ==========")
        print("匹配文档数量：", result.matched_count)
        print("实际修改数量：", result.modified_count)

        # 查询并输出更新后的完整课程文档
        updated_course = courses.find_one(
            {"_id": COURSE_ID}
        )

        print("\n========== 更新后的完整课程文档 ==========")
        pprint(updated_course, sort_dicts=False)

    except PyMongoError as e:
        print("更新失败：", e)

    finally:
        client.close()


if __name__ == "__main__":
    main()