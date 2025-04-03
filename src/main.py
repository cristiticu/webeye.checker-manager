from concurrent.futures import ThreadPoolExecutor
import json
from aws_lambda_typing.context import Context
from aws_lambda_typing.events import SQSEvent
import boto3

from context import ApplicationContext
import settings

application_context = ApplicationContext()


def process_record(check_request):
    print(f"Processing record {check_request}")

    try:
        user_guid = check_request["user_guid"]
        url = check_request["url"]
        check_type = check_request["check_type"]
        region = "us-east-1"

        if not application_context.monitored_webpages.has_monitored_webpage(user_guid, url):
            print("User does not have requested webpage")
            return None

        current_status = application_context.downtimes.get_current_status(
            user_guid, url, check_type)

        if current_status:
            last_checked_region_index = settings.AVAILABLE_REGIONS.index(
                current_status.last_checked_from)
            next_index = (last_checked_region_index +
                          3) % len(settings.AVAILABLE_REGIONS)

            region = settings.AVAILABLE_REGIONS[next_index]

        print(f"Checking from {region}")

        lambda_client = boto3.client("lambda", region_name=region)
        lambda_client.invoke(
            FunctionName=f"webeye.lambda.{region}.downtime-checker",
            InvocationType="Event",
            Payload=json.dumps(check_request)
        )

    except Exception:
        print(f"Exception when processing request {check_request}")
        return None


def lambda_handler(event: SQSEvent, context: Context):
    records = event.get("Records")

    with ThreadPoolExecutor() as executor:
        executor.map(process_record, [json.loads(record.get(
            "body", "")) for record in records], timeout=10)
