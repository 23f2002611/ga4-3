from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
import re, json
from collections import OrderedDict

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["GET", "OPTIONS"],
    allow_headers=["*"],
)

FUNCTIONS = {
    "get_ticket_status": ["ticket_id"],
    "schedule_meeting": ["date", "time", "meeting_room"],
    "get_expense_balance": ["employee_id"],
    "calculate_performance_bonus": ["employee_id", "current_year"],
    "report_office_issue": ["issue_code", "department"],
}

QUESTION_PATTERNS = [
    (r"what\s+is\s+the\s+status\s+of\s+ticket\s+(\d+)\??", "get_ticket_status", {1: "ticket_id"}),
    (r"schedule\s+a\s+meeting\s+on\s+(\d{4}-\d{2}-\d{2})\s+at\s+(\d{2}:\d{2})\s+in\s+room\s+(\w+)\.?", "schedule_meeting", {1: "date", 2: "time", 3: "meeting_room"}),
    (r"show\s+my\s+expense\s+balance\s+for\s+employee\s+(\d+)\.?", "get_expense_balance", {1: "employee_id"}),
    (r"calculate\s+performance\s+bonus\s+for\s+employee\s+(\d+)\s+for\s+(\d{4})\.?", "calculate_performance_bonus", {1: "employee_id", 2: "current_year"}),
    (r"what\s+bonus\s+for\s+emp\s+(\d+)\s+in\s+(\d{4})\??", "calculate_performance_bonus", {1: "employee_id", 2: "current_year"}),
    (r"report\s+office\s+issue\s+(\d+)\s+for\s+the\s+(\w+)\s+department\.?", "report_office_issue", {1: "issue_code", 2: "department"}),
]

@app.get("/execute")
async def execute(q: str):
    query = q.strip().lower()
    for pattern, func_name, group_map in QUESTION_PATTERNS:
        match = re.search(pattern, query)
        if not match:
            continue
        ordered_args = OrderedDict()
        for param in FUNCTIONS[func_name]:
            for idx, pname in group_map.items():
                if pname == param:
                    val = match.group(idx)
                    try:
                        val = int(val)
                    except ValueError:
                        pass
                    ordered_args[param] = val
                    break
        return JSONResponse({
            "name": func_name,
            "arguments": json.dumps(ordered_args),
        })
    raise HTTPException(status_code=400, detail="Unrecognized question format")
