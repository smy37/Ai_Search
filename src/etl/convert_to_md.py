import json
import os
from datetime import datetime


def read_raw_json(json_path):
    with open(json_path, "r") as f:
        data = json.load(f)
    return data

def parse_parts(parts):
    result = []
    for p in parts:
        if isinstance(p, str):
            result.append(p)
        elif isinstance(p, dict):
            if p.get("type", "") == "code":
                code = p.get("text", "")
                result.append(f"```{p.get("language", "unknown_language")}\n{code}\n```")
            elif p.get("type", "") == "image":
                result.append(f"[image: {p.get("image_url", "")}]")

    return "\n".join(result)

def parsing_json(json_conv):
    try:
        title = json_conv["title"]
    except Exception as e:
        print(json_conv)
        import sys
        sys.exit()

    chat_tree = json_conv["mapping"]
    text_list = []

    root = None
    for node in chat_tree.values():
        if node.get("parent") is None:
            root = node
            break

    if root is None:
        return {"title": title, "content": ""}

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
        if not message:
            continue
        role = message.get("author", {}).get("role", "")
        part_list = message.get("content", {}).get("parts", [])
        content = parse_parts(part_list)

        if role == "user":
            text_list.append({"role": "user", "text": content})
        elif role == "assistant":
            text_list.append({"role": "assistant", "text": content})
        elif role == "tool":
            text_list.append({"role": "tool", "text": content})

    parsing_data = {
        "title": title,
        "content": text_list
    }
    return parsing_data

def convert_to_md(dict_data: dict):
    md_text = ""
    md_text += f"# 대화 제목: {dict_data['title']}\n\n\n"
    for chat in dict_data["content"]:
        md_text += f"## {chat['role']}:\n{chat['text']}\n\n"
    return md_text


def ts_to_filename(ts: float) -> str:
    dt = datetime.fromtimestamp(ts)
    return dt.strftime("%Y-%m-%d_%H-%M-%S")

def find_json_file(json_dir_path, output_path):
    file_list = os.listdir(json_dir_path)
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



if __name__ == "__main__":
    json_path = "data/chat_json"
    output_path = "data/chat_markdown"
    find_json_file(json_path, output_path)
