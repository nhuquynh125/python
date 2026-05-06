"""
╔══════════════════════════════════════════════════════════════╗
║          LUNAR HERITAGE AI BACKEND  –  v1.0                 ║
║          Python 3.11+ · FastAPI · Claude claude-sonnet-4-20250514           ║
║                                                              ║
║  Endpoints:                                                  ║
║   POST /api/chat          – Thầy Đồ Neon chatbot            ║
║   POST /api/analyze-image – Nhận diện ảnh di sản            ║
║   POST /api/itinerary     – Gợi ý lịch trình du lịch        ║
║   GET  /api/heritage      – Danh sách di sản                 ║
║   GET  /api/health        – Health check                     ║
╚══════════════════════════════════════════════════════════════╝
"""

import os
import base64
import httpx
import json
from datetime import datetime
from typing import Optional, List

from fastapi import FastAPI, HTTPException, UploadFile, File, Form
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import StreamingResponse
from pydantic import BaseModel

# ──────────────────────────────────────────────
#  CONFIG
# ──────────────────────────────────────────────
ANTHROPIC_API_KEY = os.getenv("ANTHROPIC_API_KEY", "")
CLAUDE_MODEL      = "claude-sonnet-4-20250514"
ANTHROPIC_API_URL = "https://api.anthropic.com/v1/messages"
MAX_IMAGE_SIZE_MB = 5

app = FastAPI(
    title="LUNAR HERITAGE AI",
    description="AI backend cho website di sản Việt Nam LUNAR HERITAGE",
    version="1.0.0",
)

# Cho phép frontend gọi API (CORS)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],          # Đổi thành domain thật khi deploy
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# ──────────────────────────────────────────────
#  DỮ LIỆU DI SẢN (knowledge base)
# ──────────────────────────────────────────────
HERITAGE_DB = [
    {"id": 1,  "name": "Vịnh Hạ Long",           "province": "Quảng Ninh",        "lat": 20.9101, "lng": 107.1839, "unesco": 1994, "type": "thiên nhiên"},
    {"id": 2,  "name": "Cố đô Huế",              "province": "Thừa Thiên Huế",    "lat": 16.4637, "lng": 107.5909, "unesco": 1993, "type": "văn hóa"},
    {"id": 3,  "name": "Phố cổ Hội An",          "province": "Quảng Nam",         "lat": 15.8801, "lng": 108.3380, "unesco": 1999, "type": "văn hóa"},
    {"id": 4,  "name": "Ruộng bậc thang Sapa",   "province": "Lào Cai",           "lat": 22.3364, "lng": 103.8438, "unesco": None, "type": "thiên nhiên"},
    {"id": 5,  "name": "Phong Nha – Kẻ Bàng",   "province": "Quảng Bình",        "lat": 17.5500, "lng": 106.1333, "unesco": 2003, "type": "thiên nhiên"},
    {"id": 6,  "name": "Tràng An",               "province": "Ninh Bình",         "lat": 20.2521, "lng": 105.9020, "unesco": 2014, "type": "hỗn hợp"},
    {"id": 7,  "name": "Thánh địa Mỹ Sơn",      "province": "Quảng Nam",         "lat": 15.7636, "lng": 108.1230, "unesco": 1999, "type": "văn hóa"},
    {"id": 8,  "name": "Cao nguyên đá Đồng Văn", "province": "Hà Giang",          "lat": 23.2741, "lng": 105.3700, "unesco": 2010, "type": "địa chất"},
    {"id": 9,  "name": "Phố cổ Hà Nội 36 phố",  "province": "Hà Nội",           "lat": 21.0340, "lng": 105.8520, "unesco": None, "type": "văn hóa"},
    {"id": 10, "name": "Phở Việt Nam",           "province": "Toàn quốc",         "lat": 21.0285, "lng": 105.8542, "unesco": 2024, "type": "phi vật thể"},
    {"id": 11, "name": "Vịnh Nha Trang",         "province": "Khánh Hòa",         "lat": 12.2388, "lng": 109.1967, "unesco": None, "type": "thiên nhiên"},
    {"id": 12, "name": "Làng gốm Bát Tràng",    "province": "Hà Nội",            "lat": 20.9735, "lng": 105.9080, "unesco": None, "type": "làng nghề"},
]

# ──────────────────────────────────────────────
#  SYSTEM PROMPTS
# ──────────────────────────────────────────────
THAYDО_SYSTEM = """Bạn là **Thầy Đồ Neon** – trợ lý AI thông thái và duyên dáng của website LUNAR HERITAGE, \
chuyên về di sản văn hóa, lịch sử, địa lý và ẩm thực Việt Nam.

## Phong cách trả lời
- Ngắn gọn, súc tích (3–5 câu cho câu hỏi thường, tối đa 10 câu cho câu phức tạp)
- Dùng emoji liên quan một cách tự nhiên
- Giọng điệu thân thiện, đôi khi pha chút cổ kính: "Theo sử sách...", "Ta biết rằng..."
- Trả lời hoàn toàn bằng **tiếng Việt**
- Kết thúc bằng 1 câu gợi mở hoặc đề xuất khám phá thêm

## Kiến thức cốt lõi
- Di sản UNESCO Việt Nam (vật thể & phi vật thể)
- Lịch sử 4.000 năm Việt Nam
- Địa danh, phong tục, lễ hội
- Ẩm thực truyền thống các vùng miền
- Làng nghề và nghệ thuật dân gian
- Gợi ý lịch trình du lịch

## Giới hạn
- Không trả lời câu hỏi ngoài chủ đề di sản/văn hóa/lịch sử/du lịch Việt Nam
- Nếu bị hỏi ngoài chủ đề, lịch sự chuyển hướng về di sản Việt Nam"""

ANALYZE_SYSTEM = """Bạn là chuyên gia nhận diện di sản văn hóa và địa danh Việt Nam.
Khi nhận được ảnh, hãy:
1. Xác định đây là địa danh/di sản gì (nếu nhận ra)
2. Mô tả những gì thấy trong ảnh (kiến trúc, cảnh quan, đặc điểm nổi bật)
3. Cung cấp thông tin lịch sử & văn hóa ngắn gọn
4. Gợi ý thời điểm tốt nhất để thăm (nếu là địa danh du lịch)
5. Gợi ý các địa danh tương tự ở Việt Nam

Trả lời bằng tiếng Việt, sinh động và hấp dẫn, dùng emoji phù hợp."""

ITINERARY_SYSTEM = """Bạn là chuyên gia lập kế hoạch du lịch di sản Việt Nam cao cấp.
Hãy tạo lịch trình chi tiết, thực tế và hấp dẫn dựa trên thông tin người dùng cung cấp.

Format lịch trình theo cấu trúc JSON:
{
  "title": "Tên lịch trình",
  "summary": "Tóm tắt ngắn",
  "days": [
    {
      "day": 1,
      "title": "Tiêu đề ngày",
      "locations": [
        {
          "time": "08:00",
          "name": "Tên địa điểm",
          "duration": "2 tiếng",
          "description": "Mô tả ngắn",
          "tip": "Mẹo hay"
        }
      ],
      "food": "Gợi ý ẩm thực trong ngày",
      "transport": "Phương tiện di chuyển",
      "cost_estimate": "Ước tính chi phí (VND)"
    }
  ],
  "total_budget": "Tổng chi phí ước tính",
  "best_season": "Thời điểm lý tưởng",
  "tips": ["Mẹo du lịch 1", "Mẹo du lịch 2"]
}

Chỉ trả về JSON thuần túy, không thêm markdown hay giải thích."""

# ──────────────────────────────────────────────
#  PYDANTIC MODELS
# ──────────────────────────────────────────────
class Message(BaseModel):
    role: str       # "user" hoặc "assistant"
    content: str

class ChatRequest(BaseModel):
    messages: List[Message]
    stream: bool = False

class ItineraryRequest(BaseModel):
    destination: str           # Điểm đến chính
    days: int                  # Số ngày
    budget: str                # "tiết kiệm" / "trung bình" / "cao cấp"
    interests: List[str]       # ["lịch sử", "ẩm thực", "thiên nhiên", ...]
    travelers: str             # "solo" / "cặp đôi" / "gia đình" / "nhóm bạn"
    start_from: Optional[str]  # Điểm xuất phát (tùy chọn)

# ──────────────────────────────────────────────
#  HELPER: gọi Claude API
# ──────────────────────────────────────────────
async def call_claude(
    messages: list,
    system: str,
    max_tokens: int = 1000,
    stream: bool = False,
):
    if not ANTHROPIC_API_KEY:
        raise HTTPException(status_code=500, detail="ANTHROPIC_API_KEY chưa được cấu hình")

    headers = {
        "x-api-key": ANTHROPIC_API_KEY,
        "anthropic-version": "2023-06-01",
        "content-type": "application/json",
    }
    payload = {
        "model": CLAUDE_MODEL,
        "max_tokens": max_tokens,
        "system": system,
        "messages": messages,
    }
    if stream:
        payload["stream"] = True

    async with httpx.AsyncClient(timeout=60.0) as client:
        if stream:
            async def event_generator():
                async with client.stream("POST", ANTHROPIC_API_URL, headers=headers, json=payload) as resp:
                    async for line in resp.aiter_lines():
                        if line.startswith("data:"):
                            data = line[5:].strip()
                            if data and data != "[DONE]":
                                try:
                                    chunk = json.loads(data)
                                    if chunk.get("type") == "content_block_delta":
                                        text = chunk.get("delta", {}).get("text", "")
                                        if text:
                                            yield f"data: {json.dumps({'text': text})}\n\n"
                                except json.JSONDecodeError:
                                    pass
                yield "data: [DONE]\n\n"
            return event_generator()
        else:
            resp = await client.post(ANTHROPIC_API_URL, headers=headers, json=payload)
            resp.raise_for_status()
            data = resp.json()
            return data["content"][0]["text"]

# ──────────────────────────────────────────────
#  ROUTES
# ──────────────────────────────────────────────

@app.get("/api/health")
async def health():
    return {
        "status": "online",
        "model": CLAUDE_MODEL,
        "api_key_set": bool(ANTHROPIC_API_KEY),
        "timestamp": datetime.now().isoformat(),
        "version": "1.0.0",
    }


@app.get("/api/heritage")
async def get_heritage():
    """Trả về toàn bộ danh sách di sản"""
    return {"data": HERITAGE_DB, "total": len(HERITAGE_DB)}


@app.post("/api/chat")
async def chat(req: ChatRequest):
    """
    Thầy Đồ Neon – chatbot hỏi đáp di sản.
    Hỗ trợ streaming (stream=true) và non-streaming.
    """
    messages = [{"role": m.role, "content": m.content} for m in req.messages]

    if req.stream:
        gen = await call_claude(messages, THAYDО_SYSTEM, max_tokens=800, stream=True)
        return StreamingResponse(gen, media_type="text/event-stream")
    else:
        reply = await call_claude(messages, THAYDО_SYSTEM, max_tokens=800)
        return {"reply": reply, "model": CLAUDE_MODEL}


@app.post("/api/analyze-image")
async def analyze_image(file: UploadFile = File(...)):
    """
    Nhận diện ảnh di sản: upload ảnh → AI mô tả & định danh.
    """
    # Kiểm tra loại file
    if not file.content_type.startswith("image/"):
        raise HTTPException(status_code=400, detail="Chỉ chấp nhận file ảnh (jpg, png, webp)")

    # Đọc & kiểm tra kích thước
    content = await file.read()
    size_mb = len(content) / (1024 * 1024)
    if size_mb > MAX_IMAGE_SIZE_MB:
        raise HTTPException(status_code=400, detail=f"Ảnh quá lớn (tối đa {MAX_IMAGE_SIZE_MB}MB)")

    # Encode base64
    img_b64  = base64.standard_b64encode(content).decode()
    media_type = file.content_type

    messages = [{
        "role": "user",
        "content": [
            {
                "type": "image",
                "source": {
                    "type": "base64",
                    "media_type": media_type,
                    "data": img_b64,
                },
            },
            {
                "type": "text",
                "text": "Đây là ảnh chụp địa danh hoặc di sản gì của Việt Nam? Hãy phân tích chi tiết.",
            },
        ],
    }]

    reply = await call_claude(messages, ANALYZE_SYSTEM, max_tokens=1000)
    return {"analysis": reply, "filename": file.filename}


@app.post("/api/itinerary")
async def create_itinerary(req: ItineraryRequest):
    """
    Tạo lịch trình du lịch di sản cá nhân hóa.
    """
    user_msg = f"""Tạo lịch trình du lịch di sản với thông tin sau:
- Điểm đến chính: {req.destination}
- Số ngày: {req.days} ngày
- Ngân sách: {req.budget}
- Sở thích: {', '.join(req.interests)}
- Loại du khách: {req.travelers}
{f'- Xuất phát từ: {req.start_from}' if req.start_from else ''}

Hãy tạo lịch trình chi tiết, bao gồm các di sản UNESCO nếu phù hợp."""

    messages = [{"role": "user", "content": user_msg}]
    raw = await call_claude(messages, ITINERARY_SYSTEM, max_tokens=2000)

    # Parse JSON trả về
    try:
        # Xóa markdown code fences nếu có
        clean = raw.strip()
        if clean.startswith("```"):
            clean = clean.split("```")[1]
            if clean.startswith("json"):
                clean = clean[4:]
        itinerary = json.loads(clean.strip())
    except json.JSONDecodeError:
        # Nếu không parse được, trả raw text
        itinerary = {"raw": raw}

    return {"itinerary": itinerary}


@app.post("/api/nearby")
async def find_nearby(lat: float, lng: float, radius_km: float = 500):
    """
    Tìm di sản gần vị trí người dùng nhất.
    """
    import math

    def haversine(la1, lo1, la2, lo2):
        R = 6371
        dlat = math.radians(la2 - la1)
        dlng = math.radians(lo2 - lo1)
        a = math.sin(dlat/2)**2 + math.cos(math.radians(la1)) * math.cos(math.radians(la2)) * math.sin(dlng/2)**2
        return R * 2 * math.atan2(math.sqrt(a), math.sqrt(1-a))

    results = []
    for h in HERITAGE_DB:
        dist = haversine(lat, lng, h["lat"], h["lng"])
        if dist <= radius_km:
            results.append({**h, "distance_km": round(dist, 1)})

    results.sort(key=lambda x: x["distance_km"])
    return {"nearby": results, "user_location": {"lat": lat, "lng": lng}}
