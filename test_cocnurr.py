import asyncio
import time
import httpx

password = "TEST1234"
ACCESS_TOKEN = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiJjNzhiMWU0Yy04NGMxLTRkODMtYWQ1Yy03NTJlYWVkNGUxZjEiLCJpYXQiOjE3OTAwOTU0MjgsImV4cCI6MTc5MDA5NjMyOH0.WQUzVAIiTW63lSQvYA1bIfOc_zYB1gzsMPQeP6S8kVk"

URL = "http://127.0.0.1:8000/chat"

USER_ID = "c78b1e4c-84c1-4d83-ad5c-752eaed4e1f1"

# Use different real session IDs belonging to your test user(s)
SESSION_ID_1 = "1df0bf7a-d44f-4da2-8c87-bdc84fe3707b"
SESSION_ID_2 = "d67ae275-108f-4dc2-ae59-b19de3473f80"
SESSION_ID_3 = "7cf5c8cb-003a-4b45-9ed8-d669008a8d7c"
SESSION_ID_4 = "9b6adce0-c4d4-4659-bb3f-aa386e999e93"
SESSION_ID_5 = "430061a7-4db3-4ad6-a849-a7a303310dbf"
REQUESTS = [
    {
        "session_id": SESSION_ID_1,
        "message": "What is 27 * 86 + 78?"
    },
    {
        "session_id": SESSION_ID_2,
        "message": "Who is ceo of open ai ?"
    },
    {
        "session_id": SESSION_ID_3,
        "message": "What is weather in indore ?"
    },
    {
        "session_id": SESSION_ID_4,
        "message": "What is love?"
    },
    {
        "session_id": SESSION_ID_5,
        "message": "hello "
    },
]


async def send_request(
    client: httpx.AsyncClient,
    request_number: int,
    session_id: str,
    message: str,
):
    start = time.perf_counter()

    response = await client.post(
        URL,
        json={
            "session_id": session_id,
            "message": message,
        },
        # Add your auth header here
        headers={

            "Authorization": f"Bearer {ACCESS_TOKEN}"

        }
    )

    elapsed = time.perf_counter() - start

    print(
        f"Request {request_number}: "
        f"status={response.status_code} "
        f"time={elapsed:.2f}s"
    )

    return response


async def main():
    print("Starting concurrent requests...\n")

    start = time.perf_counter()

    async with httpx.AsyncClient(timeout=180) as client:

        tasks = [
            send_request(
                client,
                i + 1,
                request["session_id"],
                request["message"],
            )
            for i, request in enumerate(REQUESTS)
        ]

        await asyncio.gather(*tasks)

    total = time.perf_counter() - start

    print(f"\nTotal test time: {total:.2f}s")


if __name__ == "__main__":
    asyncio.run(main())
