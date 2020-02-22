"""SAM app entry point"""
import json
import os

import boto3  # pylint: disable=import-error
from botocore.exceptions import ClientError  # pylint: disable=import-error

from logger import log_info, log_error

SESSION = boto3.session.Session()
DDB = SESSION.resource("dynamodb")
DDB_TABLE = DDB.Table(os.getenv("TABLE_NAME"))  # pylint: disable=import-error,no-member


def cors_headers(origin="*"):
    """Returns CORS enabled headers"""
    headers = {
        "Content-Type": "application/json",
        "Access-Control-Allow-Origin": origin,
    }
    return headers


def error_400():
    """Builds an HTTP 400 response"""
    return dict(
        statusCode=400,
        headers=cors_headers(),
        body=json.dumps({"message": "Bad Request"}),
    )


def error_404():
    """Builds an HTTP 404 response"""
    return dict(
        statusCode=404,
        headers=cors_headers(),
        body=json.dumps({"message": "Not Found"}),
    )


def ok_response(body=""):
    """Builds an HTTP 200 response"""
    return dict(statusCode=200, headers=cors_headers(), body=json.dumps(body))


def get_ddb_item(table, item_id):
    """Retrieves a single item from a DDB table"""
    item = None
    try:
        response = table.get_item(Key={"id": item_id})
    except ClientError as error:
        log_error(error)
    else:
        item = response.get("Item")
    return item


def get_ddb_all(table):
    """Retrieves all items in a table"""
    items = None
    try:
        response = table.scan(AttributesToGet=['id'])
    except ClientError as error:
        log_error(error)
    else:
        items = response.get("Items")
    return items


def lambda_handler(event, _):
    """Users Lambda handler"""
    response = None
    http_method = event.get("httpMethod")
    # params = event.get("queryStringParameters")

    # filters = params.keys() if params else []

    # params = event.get("pathParameters")
    # uid = params.get("id") if params else None
    # queryStringParameters
    # 'queryStringParameters': {'reddit': '1', 'reused': '1'}
    # print(event)
    uid = None

    if http_method == "GET":
        if uid:
            log_info(f"GET user {uid}")
            item = get_ddb_item(DDB_TABLE, uid)
            if item:
                print(item)
                response = ok_response(item)
            else:
                response = error_404()
        else:
            log_info("GET all users.")
            items = get_ddb_all(DDB_TABLE)
            if items:
                print(items)
                response = ok_response(items)
            else:
                response = error_404()

    return response if response else error_400()
