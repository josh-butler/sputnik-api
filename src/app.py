"""SAM app entry point"""
import json
import os
import decimal

import boto3  # pylint: disable=import-error
from botocore.exceptions import ClientError  # pylint: disable=import-error
from boto3.dynamodb.conditions import Attr  # pylint: disable=unused-import

from logger import log_info, log_error

SESSION = boto3.session.Session()
DDB = SESSION.resource("dynamodb")
DDB_TABLE = DDB.Table(os.getenv("TABLE_NAME"))  # pylint: disable=import-error,no-member


class DecimalEncoder(json.JSONEncoder):
    """Helper to convert a DynamoDB item to JSON"""

    def default(self, o):  # pylint: disable=method-hidden
        if isinstance(o, decimal.Decimal):
            return str(o)
        return super(DecimalEncoder, self).default(o)


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
    return dict(
        statusCode=200,
        headers=cors_headers(),
        body=json.dumps(body, cls=DecimalEncoder),
    )


def get_ddb_all(table, filters=None):
    """Retrieves all items in a table"""
    items = None
    try:
        if filters:
            fe = eval(  # pylint: disable=eval-used
                " & ".join([f"Attr('{k}').eq({v})" for k, v in filters.items()])
            )
            response = table.scan(FilterExpression=fe)
        else:
            response = table.scan()
    except ClientError as error:
        log_error(error)
    else:
        items = response.get("Items")
    return items


def get_filters(params):
    """Prepare query params for DDB query"""
    query_fields = ["reused", "landSuccess", "withReddit"]
    filters = dict()
    for k in params:
        if k in query_fields and params[k] == "1":
            filters[k] = True

    return filters if filters else None


def lambda_handler(event, _):
    """Users Lambda handler"""
    response = None
    http_method = event.get("httpMethod")
    params = event.get("queryStringParameters")
    filters = get_filters(params) if params else None

    if http_method == "GET":
        log_info(f"GET launches: {filters}")
        items = get_ddb_all(DDB_TABLE, filters)
        if items:
            response = ok_response(items)
        else:
            response = error_404()

    return response if response else error_400()
