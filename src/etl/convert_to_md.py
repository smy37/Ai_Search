import json
import os
from datetime import datetime


def read_raw_json(json_path):
    with open(json_path, "r") as f:
        data = json.load(f)
    return data

def parsing_json(json_conv):
    try:
        title = json_conv["title"]
    except Exception as e:
        print(json_conv)
        import sys
        sys.exit()


    chat_tree = json_conv["mapping"]
    text_list = []

    current_node = {}
    for id in chat_tree:
        current_node = chat_tree[id]
        break
    while current_node.get("parent"):
        current_node = chat_tree[current_node.get("parent")]
    root = current_node
    id_stack = [root["id"]]

    def dfs(id_s):
        cur = id_s[:]
        cur_id = id_s[-1]

        for child in chat_tree[cur_id]["children"]:
            next_l = dfs(id_s+[child])
            if len(cur) < len(next_l):
                cur = next_l[:]

        return cur

    id_list = dfs(id_stack)

    for conv_id in id_list:
        cur_conv = chat_tree[conv_id]
        message = cur_conv.get("message")
        if message:
            if message.get("author", {}).get("role", ""):
                role = message.get("author", {}).get("role", "")
                content_list = message.get("content", {}).get("parts", [])
                parts = [p for p in content_list if isinstance(p, str)]
                content = "\n".join(parts).strip()
                if role == "user" and len(text_list)%2 == 0:
                    text_list.append({"role": "user", "text": content})
                elif role == "assistant" and len(text_list)%2 == 1:
                    text_list.append({"role": "assistant", "text": content})

    parsing_data = {
        "title": title,
        "content": text_list
    }
    return parsing_data

def convert_to_md(dict_data: dict):
    md_text = ""
    md_text += f"# 대화 제목: {dict_data["title"]}\n\n\n"
    for chat in dict_data["content"]:
        md_text += f"## {chat["role"]}:\n{chat["text"]}\n\n"
    return md_text


def ts_to_filename(ts: float) -> str:
    dt = datetime.fromtimestamp(ts)
    return dt.strftime("%Y-%m-%d_%H-%M-%S")

def find_json_file(json_dir_path, output_path):
    file_list = os.listdir(json_dir_path)
    cnt = 0
    for file in file_list:
        extension = os.path.splitext(file)[-1]
        if extension == ".json":
            json_data = read_raw_json(os.path.join(json_dir_path, file))

            for conv in json_data:
                if conv:
                    create_time = conv.get("create_time", "")
                    print(create_time)
                    if not create_time:
                        continue
                    parsing_data = parsing_json(conv)
                    md_data = convert_to_md(parsing_data)
                    time_title = ts_to_filename(create_time)
                    with open(os.path.join(output_path, f"{time_title}.md"), "w", encoding="utf-8") as wr:
                        wr.write(md_data)
                    cnt += 1


if __name__ == "__main__":
    json_path = "data/chat_json"
    output_path = "data/chat_markdown"
    find_json_file(json_path, output_path)
