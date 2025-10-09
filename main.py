from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
import re
import json

app = FastAPI()

# Enable CORS for all origins
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["GET"],
    allow_headers=["*"],
)

# Predefined question patterns
QUESTION_PATTERNS = [
    (r"what is the status of ticket (\d+)\??", "get_ticket_status", ["ticket_id"]),
    (r"show details for user (\w+)\??", "get_user_details", ["username"]),
    (r"what is the total for order (\d+)\??", "get_order_total", ["order_id"]),
    (r"what is the price of product (\w+)\??", "get_product_price", ["product_name"]),
    # 👇 Correct pattern and argument order for bonus question
    (r"what bonus for emp (\d+) in (\d{4})\??", "get_employee_bonus", ["emp_id", "year"]),
]



@app.get("/execute")
async def execute_query(q: str):
    query = q.strip().lower()

    for pattern, func_name, params in QUESTION_PATTERNS:
        match = re.match(pattern, query)
        if match:
            values = match.groups()
            args = {params[i]: values[i] for i in range(len(params))}

            # convert numeric strings to integers
            for key, value in args.items():
                if str(value).isdigit():
                    args[key] = int(value)

            return JSONResponse({
                "name": func_name,
                "arguments": json.dumps(args)
            })

    raise HTTPException(status_code=400, detail="Unrecognized question pattern")

