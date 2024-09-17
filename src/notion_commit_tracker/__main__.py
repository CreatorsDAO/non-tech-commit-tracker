from collections import defaultdict

from .analyzer import analyze_contributions, get_all_databases, get_all_pages


# 主函数
def main():
    all_databases = get_all_databases()
    all_contributions = defaultdict(lambda: {"score": 0, "edits": 0})

    for database in all_databases:
        print(f"正在分析数据库: {database['title'][0]['plain_text']}")
        pages = get_all_pages(database["id"])
        contributions = analyze_contributions(pages)

        # 合并贡献数据
        for user, data in contributions.items():
            all_contributions[user]["score"] += data["score"]
            all_contributions[user]["edits"] += data["edits"]

    print("\n总贡献度分析结果：")
    for user, data in sorted(
        all_contributions.items(), key=lambda x: x[1]["score"], reverse=True
    ):
        print(f"{user}: 分数 {data['score']:.2f}, 编辑次数 {data['edits']}")


if __name__ == "__main__":
    main()
