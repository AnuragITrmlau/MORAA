import os
import sys
import asyncio
from pathlib import Path
from dotenv import load_dotenv

backend_dir = Path(__file__).resolve().parent.parent
if str(backend_dir) not in sys.path:
    sys.path.insert(0, str(backend_dir))

load_dotenv(backend_dir / ".env")
load_dotenv(backend_dir.parent / ".env")

import httpx
from app.services.erpnext_service import ERPNextService

async def main():
    service = ERPNextService()
    # Test customer already exists, fetch or use 'Test User'
    customer_id = "Test User"
    
    # Direct test request with full error response print
    url = f"{service.base_url}/api/resource/Sales Invoice"
    payload = {
        "company": service.company or "moraa",
        "customer": customer_id,
        "items": [
            {
                "item_code": "GEMVISION-WALLET-RECHARGE",
                "qty": 1,
                "rate": 10.0
            }
        ]
    }
    
    async with httpx.AsyncClient() as client:
        res = await client.post(url, headers=service.headers, json=payload)
        print("\n--- ERPNext Full Response ---")
        print(f"Status Code: {res.status_code}")
        print(res.text)
        print("-----------------------------\n")

if __name__ == "__main__":
    asyncio.run(main())