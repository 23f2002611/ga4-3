from fastapi import FastAPI, Request, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
import re
import json

app = FastAPI()

# Enable CORS (allow all origins for GET requests)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["GET"],
    allow_headers=["*"],
)

# Predefined question patterns mapped to function names
QUESTION_PATTERNS = [
    # Ticket status query
    (r"what is the status of ticket (\d+)\??", "get_ticket_status", ["ticket_id"]),
    # User details query
    (r"show details for user (\w+)\??", "get_user_details", ["username"]),
    # Order info query
    (r"what is the total for order (\d+)\??", "get_order_total", ["order_id"]),
    # Product price query
    (r"what is the price of product (\w+)\??", "get_product_price", ["product_name"]),
]

@app.get("/execute")
async def execute_query(q: str):
    query = q.strip().lower()

    for pattern, func_name, params in QUESTION_PATTERNS:
        match = re.match(pattern, query)
        if match:
            values = match.groups()
            args = {params[i]: values[i] for i in range(len(params))}

            # Convert numbers to int when applicable
            for key, value in args.items():
                if value.isdigit():
                    args[key] = int(value)

            return JSONResponse(
                {
                    "name": func_name,
                    "arguments": json.dumps(args)
                }
            )

    raise HTTPException(status_code=400, detail="Unrecognized question pattern")


# Example local URL for testing:
# http://127.0.0.1:8000/execute?q=What%20is%20the%20status%20of%20ticket%2083742%3F
