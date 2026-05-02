import os
from fastapi import FastAPI, Depends  # type: ignore
from fastapi.responses import StreamingResponse  # type: ignore
from pydantic import BaseModel  # type: ignore
from fastapi_clerk_auth import ClerkConfig, ClerkHTTPBearer, HTTPAuthorizationCredentials  # type: ignore
from openai import OpenAI  # type: ignore

app = FastAPI()
clerk_config = ClerkConfig(jwks_url=os.getenv("CLERK_JWKS_URL"))
clerk_guard = ClerkHTTPBearer(clerk_config)


class Visit(BaseModel):
    patient_name: str
    date_of_visit: str
    notes: str


system_prompt = """
Bạn được cung cấp ghi chú do bác sĩ viết về buổi khám của một bệnh nhân.
Nhiệm vụ của bạn là tóm tắt buổi khám cho bác sĩ và soạn một email gửi bệnh nhân.
Hãy trả lời hoàn toàn bằng tiếng Việt với chính xác ba mục có tiêu đề:
### Tóm tắt buổi khám cho hồ sơ của bác sĩ
### Các bước tiếp theo cho bác sĩ
### Bản nháp email gửi bệnh nhân bằng ngôn ngữ thân thiện
"""


def user_prompt_for(visit: Visit) -> str:
    return f"""Hãy tạo bản tóm tắt, các bước tiếp theo và bản nháp email cho:
Tên bệnh nhân: {visit.patient_name}
Ngày khám: {visit.date_of_visit}
Ghi chú:
{visit.notes}"""


@app.post("/api")
def consultation_summary(
    visit: Visit,
    creds: HTTPAuthorizationCredentials = Depends(clerk_guard),
):
    user_id = creds.decoded["sub"]  # Available for tracking/auditing
    client = OpenAI()

    user_prompt = user_prompt_for(visit)

    prompt = [
        {"role": "system", "content": system_prompt},
        {"role": "user", "content": user_prompt},
    ]

    stream = client.chat.completions.create(
        model="gpt-4.1-mini",
        messages=prompt,
        stream=True,
    )

    def event_stream():
        for chunk in stream:
            text = chunk.choices[0].delta.content
            if text:
                lines = text.split("\n")
                for line in lines[:-1]:
                    yield f"data: {line}\n\n"
                    yield "data:  \n"
                yield f"data: {lines[-1]}\n\n"

    return StreamingResponse(event_stream(), media_type="text/event-stream")