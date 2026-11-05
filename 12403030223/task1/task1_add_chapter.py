from pymongo import MongoClient
from pymongo.errors import PyMongoError
from pprint import pprint

MONGO_URI = "mongodb://127.0.0.1:27017/?replicaSet=rs0"
DB_NAME = "exam_12403030223"

COURSE_ID = "COURSE-12403030223-01"

NEW_CHAPTER = {
    "chapterId": "CH03",
    "title": "Redis高级操作",
    "hours": 4
}


def add_chapter(courses):
    """
    仅当CH03不存在时才添加。
    利用update_one的筛选条件实现防重复。
    """
    result = courses.update_one(
        {
            "_id": COURSE_ID,
            "chapters.chapterId": {"$ne": "CH03"}
        },
        {
            "$push": {
                "chapters": NEW_CHAPTER
            }
        }
    )

    return result


def main():
    client = MongoClient(
        MONGO_URI,
        serverSelectionTimeoutMS=10000
    )

    try:
        client.admin.command("ping")
        courses = client[DB_NAME]["courses"]

        print("========== 第一次执行新增 ==========")

        result1 = add_chapter(courses)

        print("匹配文档数量：", result1.matched_count)
        print("实际修改数量：", result1.modified_count)

        print("\n========== 第二次执行新增 ==========")

        result2 = add_chapter(courses)

        print("匹配文档数量：", result2.matched_count)
        print("实际修改数量：", result2.modified_count)

        print("\n========== 最终课程文档 ==========")

        final_course = courses.find_one(
            {"_id": COURSE_ID}
        )

        pprint(final_course, sort_dicts=False)

    except PyMongoError as e:
        print("新增章节失败：", e)

    finally:
        client.close()


if __name__ == "__main__":
    main()