# main.py
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
import re
import json

app = FastAPI()

# Enable CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["GET", "OPTIONS"],
    allow_headers=["*"],
)

# Pattern matching with explicit parameter extraction
@app.get("/execute")
async def execute(q: str):
    query = q.strip()
    query_lower = query.lower()
    
    # 1. Ticket Status
    match = re.search(r'ticket\s+(\d+)', query_lower)
    if match:
        return {
            "name": "get_ticket_status",
            "arguments": json.dumps({"ticket_id": int(match.group(1))})
        }
    
    # 2. Schedule Meeting
    match = re.search(r'schedule\s+a\s+meeting\s+on\s+([\d-]+)\s+at\s+([\d:]+)\s+in\s+room\s+(\w+)', query_lower)
    if match:
        return {
            "name": "schedule_meeting",
            "arguments": json.dumps({
                "date": match.group(1),
                "time": match.group(2),
                "meeting_room": f"Room {match.group(3).upper()}"
            })
        }
    
    # 3. Expense Balance
    match = re.search(r'expense\s+balance\s+for\s+employee\s+(\d+)', query_lower)
    if match:
        return {
            "name": "get_expense_balance",
            "arguments": json.dumps({"employee_id": int(match.group(1))})
        }
    
    # 4. Performance Bonus - Multiple phrasings
    match = re.search(r'(?:calculate\s+)?performance\s+bonus\s+for\s+employee\s+(\d+)\s+for\s+(\d{4})', query_lower)
    if not match:
        match = re.search(r'bonus\s+for\s+emp(?:loyee)?\s+(\d+)\s+in\s+(\d{4})', query_lower)
    if not match:
        # "Emp 27756 bonus 2025" format
        match = re.search(r'emp(?:loyee)?\s+(\d+)\s+bonus\s+(\d{4})', query_lower)
    if not match:
        # "bonus emp 27756 2025" format
        match = re.search(r'bonus\s+emp(?:loyee)?\s+(\d+)\s+(\d{4})', query_lower)
    if match:
        return {
            "name": "calculate_performance_bonus",
            "arguments": json.dumps({
                "employee_id": int(match.group(1)),
                "current_year": int(match.group(2))
            })
        }
    
    # 5. Report Office Issue
    match = re.search(r'report\s+office\s+issue\s+(\d+)\s+for\s+(?:the\s+)?(\w+)', query_lower)
    if match:
        dept = match.group(2).capitalize()
        return {
            "name": "report_office_issue",
            "arguments": json.dumps({
                "issue_code": int(match.group(1)),
                "department": dept
            })
        }
    
    raise HTTPException(status_code=400, detail="Unrecognized question format")
