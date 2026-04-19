import os
import boto3

def upload_markdown_files(local_dir, bucket_name, s3_prefix):
    s3 = boto3.client("s3")

    for file in os.listdir(local_dir):
        if not file.endswith(".md"):
            continue

        local_path = os.path.join(local_dir, file)
        s3_key = f"{s3_prefix}/{file}"

        s3.upload_file(
            local_path,
            bucket_name,
            s3_key,
            ExtraArgs={"ContentType": "text/markdown"}
        )

        print(f"Uploaded: {local_path} -> s3://{bucket_name}/{s3_key}")



if __name__ == "__main__":
    bucket_name = "smy-dev-gpt-data"
    local_path = "data/chat_markdown"
    s3_prefix = "chat_markdown"

    upload_markdown_files(local_path, bucket_name, s3_prefix)