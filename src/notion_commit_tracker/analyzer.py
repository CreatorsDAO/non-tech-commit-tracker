import os
from collections import defaultdict

from dotenv import load_dotenv
from notion_client import Client

load_dotenv(dotenv_path=os.path.join(os.getcwd(), ".env"))


notion_token = os.environ.get("NOTION_KEY")
print(notion_token)

# 初始化Notion客户端
notion = Client(auth=notion_token)

# 获取所有数据库


def get_all_databases():
    databases = []
    has_more = True
    start_cursor = None
    while has_more:
        response = notion.search(
            filter={"property": "object", "value": "database"},
            start_cursor=start_cursor,
        )
        databases.extend(response["results"])
        has_more = response["has_more"]
        start_cursor = response["next_cursor"]
    return databases


# 获取数据库中的所有页面


def get_all_pages(database_id):
    pages = []
    has_more = True
    start_cursor = None
    while has_more:
        response = notion.databases.query(
            database_id=database_id, start_cursor=start_cursor
        )
        pages.extend(response["results"])
        has_more = response["has_more"]
        start_cursor = response["next_cursor"]
    return pages


# 计算页面复杂度
def calculate_page_complexity(page):
    complexity = 0

    # 考虑页面属性数量
    complexity += len(page["properties"]) * 0.5

    # 获取页面内容
    page_content = notion.blocks.children.list(block_id=page["id"])

    # 考虑页面内容长度和块数量
    total_length = 0
    for block in page_content["results"]:
        if "paragraph" in block:
            total_length += len(block["paragraph"]["rich_text"])
        elif "heading_1" in block or "heading_2" in block or "heading_3" in block:
            total_length += len(block[block["type"]]["rich_text"]) * 2  # 标题权重更高

    complexity += total_length * 0.01  # 每100个字符增加1点复杂度
    complexity += len(page_content["results"]) * 0.1  # 每个块增加0.1点复杂度

    return complexity


user_cache = {}


def get_user(user_id):
    if user_id not in user_cache:
        try:
            user = notion.users.retrieve(user_id=user_id)
            user_cache[user_id] = user["name"]
        except Exception as e:
            print(f"获取用户信息失败: {e}")
            user_cache[user_id] = "Unknown User: " + user_id
    return user_cache[user_id]


# 分析贡献度


def analyze_contributions(pages):
    contributions = defaultdict(lambda: {"score": 0, "edits": 0})
    for page in pages:
        creator = get_user(page["created_by"]["id"])
        last_editor = get_user(page["last_edited_by"]["id"])
        complexity = calculate_page_complexity(page)
        contributions[creator]["score"] += complexity
        contributions[creator]["edits"] += 1
        if creator != last_editor:
            contributions[last_editor]["score"] += complexity * 0.5
            contributions[last_editor]["edits"] += 1
    return contributions
