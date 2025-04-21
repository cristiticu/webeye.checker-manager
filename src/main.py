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
        u_guid: str = check_request["u_guid"]
        url: str = check_request["url"]
        configuration = check_request["configuration"]

        zones: list[str] = configuration["zones"]

        if not application_context.monitored_webpages.has_monitored_webpage(u_guid, url):
            print("User does not have requested webpage")
            return None

        payload = {
            "u_guid": u_guid,
            "url": url,
            "check_string": configuration["check_string"] if "check_string" in configuration else None,
            "fail_on_status": configuration["fail_on_status"] if "fail_on_status" in configuration else [],
            "timeout": configuration["timeout"] if "timeout" in configuration else None,
            "screenshot": configuration["save_screenshot"] if "save_screenshot" in configuration else False,
        }

        for zone in zones:
            print(f"Checking from {zone}")

            for region in settings.AVAILABLE_REGIONS[zone]:
                print(f"Checking from {region}")

                lambda_client = boto3.client("lambda", region_name=region)

                lambda_client.invoke(
                    FunctionName=f"{settings.LAMBDA_PREFIX}_{settings.SPEED_CHECKER_LAMBDA_NAME}-{region}",
                    InvocationType="Event",
                    Payload=json.dumps(payload)
                )

    except Exception as e:
        print(f"Exception when processing request {check_request}: {e}")
        return None


def lambda_handler(event: SQSEvent, context: Context):
    records = event.get("Records")

    with ThreadPoolExecutor() as executor:
        executor.map(process_record, [json.loads(record.get(
            "body", "")) for record in records], timeout=20)
