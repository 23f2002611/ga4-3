# api/main.py
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
import re
import json
from collections import OrderedDict

app = FastAPI()

# Enable CORS for GET from any origin
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["GET", "OPTIONS"],
    allow_headers=["*"],
)

# Canonical function signatures: order here is authoritative
FUNCTIONS = {
    "get_ticket_status": {
        "params": ["ticket_id"],
        "types": {"ticket_id": int},
    },
    "get_user_details": {
        "params": ["username"],
        "types": {"username": str},
    },
    "get_order_total": {
        "params": ["order_id"],
        "types": {"order_id": int},
    },
    "get_product_price": {
        "params": ["product_name"],
        "types": {"product_name": str},
    },
    # The checker expects emp_id first, then year (exact order)
    "get_employee_bonus": {
        "params": ["emp_id", "year"],
        "types": {"emp_id": int, "year": int},
    },
}

# Patterns: (regex, function_name, {group_index: param_name, ...})
# group_index is 1-based as returned by re.Match.group(n)
QUESTION_PATTERNS = [
    (r"what\s+is\s+the\s+status\s+of\s+ticket\s+(\d+)\??", "get_ticket_status", {1: "ticket_id"}),
    (r"show\s+details\s+for\s+user\s+(\w+)\??", "get_user_details", {1: "username"}),
    (r"what\s+is\s+the\s+total\s+for\s+order\s+(\d+)\??", "get_order_total", {1: "order_id"}),
    (r"what\s+is\s+the\s+price\s+of\s+product\s+(\w+)\??", "get_product_price", {1: "product_name"}),
    (r"what\s+bonus\s+for\s+emp\s+(\d+)\s+in\s+(\d{4})\??", "get_employee_bonus", {1: "emp_id", 2: "year"}),
]

@app.get("/execute")
async def execute(q: str):
    query = q.strip()

    for pattern, func_name, group_map in QUESTION_PATTERNS:
        match = re.search(pattern, query, flags=re.IGNORECASE)
        if not match:
            continue

        # Validate function meta exists
        meta = FUNCTIONS.get(func_name)
        if not meta:
            raise HTTPException(status_code=500, detail=f"Server misconfiguration: unknown function '{func_name}'")

        # invert group_map: param_name -> group_index
        param_to_group = {param_name: idx for idx, param_name in group_map.items()}

        # Build ordered args according to the canonical param order
        ordered_args = OrderedDict()
        for param in meta["params"]:
            if param not in param_to_group:
                raise HTTPException(
                    status_code=500,
                    detail=f"Server misconfiguration: parameter '{param}' not provided by pattern for '{func_name}'"
                )
            group_index = param_to_group[param]
            try:
                raw_value = match.group(group_index)
            except IndexError:
                raise HTTPException(status_code=400, detail="Pattern matched but group missing")

            # cast to expected type if possible
            cast_fn = meta.get("types", {}).get(param, str)
            try:
                value = cast_fn(raw_value)
            except Exception:
                # fallback: keep string if cast fails
                value = raw_value

            ordered_args[param] = value

        # Convert ordered args to JSON string preserving order
        arguments_json_str = json.dumps(ordered_args)

        return JSONResponse({"name": func_name, "arguments": arguments_json_str})

    # No pattern matched
    raise HTTPException(status_code=400, detail="Unrecognized question pattern")
