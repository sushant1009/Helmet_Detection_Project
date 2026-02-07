import httpx
from config import ATTENDANCE_URL

async def mark_attendance(worker_id: int, token: str):
    """Mark attendance for a worker"""
    try:
        async with httpx.AsyncClient() as client:
            headers = {"Authorization": f"Bearer {token}"}
            resp = await client.post(f"{ATTENDANCE_URL}{worker_id}", headers=headers)
            print(f"Attendance marked: {resp.status_code}, {resp.text}")
    except Exception as e:
        print(f"Error marking attendance: {e}")