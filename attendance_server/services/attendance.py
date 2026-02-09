import httpx
import cv2
from config import ATTENDANCE_URL
from utils.logger import setup_logger

logger = setup_logger("attendance_service")


async def mark_attendance(worker_id: int, frame, token: str):
    try:
        # Encode frame to JPG
        success, img_encoded = cv2.imencode(".jpg", frame)
        if not success:
            logger.error("Failed to encode frame")
            return

        image_bytes = img_encoded.tobytes()

        headers = {
            "Authorization": f"Bearer {token}"
        }

        files = {
            "file": ("frame.jpg", image_bytes, "image/jpeg")
        }

        async with httpx.AsyncClient(timeout=10.0) as client:
            resp = await client.post(
                f"{ATTENDANCE_URL}{worker_id}",
                headers=headers,
                files=files
            )

        if resp.status_code == 200:
            logger.info(f"Attendance marked for worker {worker_id}")
        else:
            logger.warning(f"Attendance failed [{resp.status_code}]: {resp.text}")

    except Exception as e:
        logger.error(f"Error marking attendance: {e}")
