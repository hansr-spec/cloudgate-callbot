from fastapi import FastAPI, HTTPException, Query
from fastapi.middleware.cors import CORSMiddleware

app = FastAPI(title="회원정보 조회 데모 API", version="1.0.0")

# CORS 허용 (콜봇/외부 플랫폼에서 호출할 수 있도록)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

# -------------------------------------------------------------------
# 목업(mock) 회원 데이터입니다. 실제 개인정보가 아닌 데모용 가상 데이터입니다.
# 실제 서비스에서는 이 부분을 DB 조회로 교체하세요.
# -------------------------------------------------------------------
MEMBERS = {
    "01046910781": {
        "member_id": "M0001",
        "name": "한세라",
        "phone": "01046910781",
        "grade": "36허4567",
        "points": 15200,
        "join_date": "2021-03-15",
        "status": "정상",
    },
    "01071040924": {
        "member_id": "M0002",
        "name": "조성배",
        "phone": "01071040924",
        "grade": "36허4555",
        "points": 3200,
        "join_date": "2023-07-01",
        "status": "정상",
    },
    "01055556666": {
        "member_id": "M0003",
        "name": "홍성태",
        "phone": "01055556666",
        "grade": "42허4567",
        "points": 8900,
        "join_date": "2019-11-20",
        "status": "휴면",
    },
}


def normalize_phone(raw: str) -> str:
    """
    실제 통화에서는 발신번호가 다양한 형태로 넘어올 수 있어 표준 형태로 맞춰줍니다.
    예: '+82 10-4691-0781', '821046910781', '010 4691 0781' -> '01046910781'
    """
    if not raw:
        return ""
    # 공백, 하이픈, 괄호 제거
    p = str(raw).strip()
    for ch in [" ", "-", "(", ")"]:
        p = p.replace(ch, "")

    # 국가번호 +82 / 82 처리 -> 0으로 교체
    if p.startswith("+82"):
        p = "0" + p[3:]
    elif p.startswith("82") and len(p) >= 11:
        p = "0" + p[2:]

    return p


@app.get("/")
def root():
    return {"message": "회원정보 조회 데모 API가 정상 동작 중입니다.", "docs": "/docs"}


@app.get("/members/lookup")
def lookup_member(
    phone: str = Query(..., description="회원 전화번호 (하이픈 없이, 예: 01012345678)")
):
    """전화번호로 회원정보를 조회합니다. 일반 REST 호출용."""
    normalized = normalize_phone(phone)
    member = MEMBERS.get(normalized)
    if not member:
        raise HTTPException(status_code=404, detail="회원 정보를 찾을 수 없습니다.")
    return member


@app.post("/lookup-member")
async def lookup_member_simple(payload: dict):
    """
    콜봇/LLM 도구 호출용 단순 엔드포인트.
    요청 body 예시: {"phone": "01012345678"}
    응답은 사람이 바로 읽을 수 있는 answer 텍스트로 내려줍니다.
    """
    raw_phone = payload.get("phone", "")
    phone = normalize_phone(raw_phone)
    member = MEMBERS.get(phone)

    if not member:
        return {
            "found": False,
            "name": "",
            "answer": "해당 전화번호로 등록된 회원 정보를 찾을 수 없습니다.",
            "received_phone": raw_phone,      # 디버깅용: 실제 넘어온 원본 값
            "normalized_phone": phone,        # 디버깅용: 정규화 후 값
        }

    answer = (
        f"{member['name']} 고객님, {member['grade']} 등급이시며 "
        f"현재 포인트는 {member['points']}점입니다. "
        f"회원 상태는 {member['status']}입니다."
    )

    return {
        "found": True,
        "name": member["name"],
        "grade": member["grade"],
        "points": member["points"],
        "status": member["status"],
        "answer": answer,
    }


@app.post("/dialogflow-webhook")
async def dialogflow_webhook(payload: dict):
    """
    다이얼로그플로우(Dialogflow) Fulfillment 웹훅 형식.
    인텐트 파라미터에 phone_number 라는 이름으로 전화번호가 담겨 온다고 가정합니다.
    파라미터 이름은 실제 Dialogflow 인텐트 설정에 맞게 조정하세요.
    """
    try:
        params = payload.get("queryResult", {}).get("parameters", {})
        phone = normalize_phone(params.get("phone_number", ""))
    except AttributeError:
        phone = ""

    member = MEMBERS.get(phone)

    if not member:
        fulfillment_text = "죄송합니다. 해당 전화번호로 등록된 회원 정보를 찾을 수 없습니다."
    else:
        fulfillment_text = (
            f"{member['name']} 고객님, {member['grade']} 등급이시며 "
            f"현재 포인트는 {member['points']}점입니다. "
            f"회원 상태는 {member['status']}입니다."
        )

    return {"fulfillmentText": fulfillment_text}
