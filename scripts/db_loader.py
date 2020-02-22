"""Script to populate a DynamoDB table with Launch data"""
import json
import os
import uuid
import logging
import argparse

import boto3
from botocore.exceptions import ClientError

log_level = logging.INFO
logging.basicConfig(level=log_level)
logger = logging.getLogger()
logger.setLevel(log_level)

AWS_REGION = os.getenv("AWS_REGION", "us-east-1")
SESSION = boto3.session.Session(region_name=AWS_REGION)
DDB = SESSION.resource("dynamodb")


def put_ddb_item(table, item):
    """Insert a DynamoDB record"""
    response = None
    try:
        response = table.put_item(Item=item)
    except ClientError as err:
        logger.error(err)

    return response


def parse_links(links):
    """Inspect links object and return target data"""
    reddit = any(
        (
            links.get("reddit_campaign"),
            links.get("reddit_launch"),
            links.get("reddit_recovery"),
            links.get("reddit_media"),
        )
    )

    return reddit, links.get("article_link"), links.get("mission_patch_small")


def parse_cores(cores):
    """Inspect cores array and return total landed & reused bool"""
    landed, reused = [], []
    for core in cores:
        reused.append(core["reused"])
        landed.append(core["land_success"])

    return all(landed), all(reused)


def get_args():
    """Return parsed CLI args"""
    parser = argparse.ArgumentParser(description="DDB loader")
    parser.add_argument(
        "--src", default="seed-data.json", help="Path to source data (seed-data.json)"
    )
    parser.add_argument(
        "--table", default="prod-launch-prod-sputnik-api", help="Target DynamoDB table name"
    )

    return parser.parse_args()


def main():
    """Script entry point"""
    args = get_args()
    table = DDB.Table(args.table)

    with open(args.src) as json_file:
        data = json.load(json_file)
        for obj in data:
            rocket = obj.get("rocket")
            flight_number = obj.get("flight_number")
            landed, reused = parse_cores(rocket["first_stage"]["cores"])
            reddit, article, patch = parse_links(obj.get("links"))

            item = dict(
                id=str(uuid.uuid4()),
                flightNumber=flight_number,
                missionName=obj.get("mission_name"),
                details=obj.get("details"),
                launchDate=obj.get("launch_date_utc"),
                rocketName=rocket.get("rocket_name"),
                rocketType=rocket.get("rocket_type"),
                landSuccess=landed,
                reused=reused,
                withReddit=reddit,
                articleUrl=article,
                missionPatchUrl=patch,
            )

            # Remove keys with None values
            item = {k: v for k, v in item.items() if v is not None}
            
            logger.info(f"Inserting flight {flight_number}")
            _ = put_ddb_item(table, item)


if __name__ == "__main__":
    main()
