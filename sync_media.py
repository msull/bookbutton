#!python
import json
import os
from datetime import datetime
from pathlib import Path
import boto3


PREFIX = "bookbutton/"


def list_file_pairs(directory: Path):
    file_pairs = {}
    for file in directory.glob("*.m4a"):
        base_name = file.stem
        png_file = directory / f"{base_name}.png"
        file_pairs[base_name] = {
            "m4a": str(file.name),
            "png": str(png_file.name) if png_file.exists() else None,
        }
    return file_pairs


def get_s3_objects(bucket_name, s3_client):
    response = s3_client.list_objects_v2(
        Bucket=bucket_name, Prefix=PREFIX, Delimiter="/"
    )
    data = [
        x
        for x in (
            item["Key"].removeprefix(PREFIX).strip()
            for item in response.get("Contents", [])
        )
        if x
    ]
    return data


def upload_files_to_s3(bucket_name, directory, file_pairs, existing_files, s3_client):
    for base_name, files in file_pairs.items():
        for file_type in files:
            if files[file_type] and files[file_type] not in existing_files:
                file_path = directory / files[file_type]
                print(f"Uploading {file_path}")
                s3_client.upload_file(
                    str(file_path), bucket_name, PREFIX + files[file_type]
                )
                print("Done")


def main():
    directory = Path(os.environ["MEDIA_PATH"])
    bucket_name = os.environ["S3_BUCKET"]

    if not directory.exists() or not directory.is_dir():
        raise ValueError(
            f"The directory {directory} does not exist or is not a directory."
        )

    s3_client = boto3.client("s3")
    existing_files = get_s3_objects(bucket_name, s3_client)

    file_pairs = list_file_pairs(directory)
    upload_files_to_s3(bucket_name, directory, file_pairs, existing_files, s3_client)

    # Generate and upload JSON file
    json_file_name = directory / "data.json"
    with open(json_file_name, "w") as json_file:
        json.dump(file_pairs, json_file, indent=2, sort_keys=True)

    print(f"Uploading {json_file_name}")
    s3_client.upload_file(
        str(json_file_name), bucket_name, PREFIX + json_file_name.name
    )

    cloudfront_client = boto3.client("cloudfront")

    response = cloudfront_client.create_invalidation(
        DistributionId="E19YBRNT140O6B",
        InvalidationBatch={
            "Paths": {
                "Quantity": 1,
                "Items": [f"/{PREFIX}*"],  # Invalidate all objects in the distribution
            },
            "CallerReference": datetime.now().isoformat(),
        },
    )

    print(response)


if __name__ == "__main__":
    main()
