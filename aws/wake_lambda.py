"""
Trip Buddy wake-up link (AWS Lambda, Python 3.13, function URL).

The server turns itself off after 30 idle minutes. Opening this link:
  - server running and app ready  -> redirect to the app
  - server off                    -> start it, show a "waking up" page that refreshes
  - monthly credit limit reached  -> do NOT start it, say so
"""

import os
import urllib.request

import boto3

INSTANCE_ID = os.environ["INSTANCE_ID"]
ACCOUNT_ID = os.environ["ACCOUNT_ID"]
BUDGET_NAME = os.environ["BUDGET_NAME"]

ec2 = boto3.client("ec2")
budgets = boto3.client("budgets", region_name="us-east-1")


def page(title: str, message: str, refresh: int | None = 15) -> dict:
    meta = f'<meta http-equiv="refresh" content="{refresh}">' if refresh else ""
    html = f"""<!doctype html><html><head><meta charset="utf-8">
<meta name="viewport" content="width=device-width,initial-scale=1">{meta}
<title>Trip Buddy</title>
<style>body{{font-family:system-ui,sans-serif;background:#f4f6f8;color:#1d2733;display:grid;place-items:center;min-height:100vh;margin:0;padding:16px}}
.card{{background:#fff;border-radius:12px;padding:32px;max-width:420px;text-align:center;box-shadow:0 2px 12px #0001}}
h1{{font-size:1.4rem;margin:0 0 8px}}p{{color:#4a5563;line-height:1.5}}</style></head>
<body><div class="card"><h1>🧳 {title}</h1><p>{message}</p></div></body></html>"""
    return {"statusCode": 200, "headers": {"Content-Type": "text/html; charset=utf-8"}, "body": html}


def over_budget() -> bool:
    b = budgets.describe_budget(AccountId=ACCOUNT_ID, BudgetName=BUDGET_NAME)["Budget"]
    spent = float(b.get("CalculatedSpend", {}).get("ActualSpend", {}).get("Amount", 0))
    return spent >= float(b["BudgetLimit"]["Amount"])


def app_ready(host: str) -> bool:
    try:
        with urllib.request.urlopen(f"https://{host}/", timeout=4) as r:
            return r.status == 200
    except Exception:
        return False


def handler(event, context):
    inst = ec2.describe_instances(InstanceIds=[INSTANCE_ID])["Reservations"][0]["Instances"][0]
    state = inst["State"]["Name"]

    if state == "running":
        ip = inst.get("PublicIpAddress")
        host = f"{ip.replace('.', '-')}.sslip.io" if ip else None
        if host and app_ready(host):
            return {"statusCode": 302, "headers": {"Location": f"https://{host}/"}}
        return page("Almost ready…", "The server is on and Trip Buddy is starting. This page refreshes by itself.", 10)

    if state in ("stopped",):
        if over_budget():
            return page("Paused for this month",
                        "Trip Buddy reached its monthly credit limit, so it stays off until next month.", None)
        ec2.start_instances(InstanceIds=[INSTANCE_ID])
        return page("Waking up Trip Buddy…",
                    "It was asleep to save credits. This takes about a minute; the page refreshes by itself.")

    # pending, stopping, shutting-down: wait and try again
    return page("Please wait…", f"The server is {state}. This page refreshes by itself.")
