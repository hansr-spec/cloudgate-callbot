# 회원정보 조회 데모 API

콜봇(다이얼로그플로우 등) 시연용으로 만든 회원정보 조회 API입니다.
실제 개인정보가 아닌 **가짜(목업) 데이터** 3건이 들어 있습니다.

## 1. 로컬에서 실행하기

```bash
pip install -r requirements.txt
uvicorn main:app --host 0.0.0.0 --port 8000
```

실행 후 브라우저에서 `http://localhost:8000/docs` 로 들어가면
자동 생성된 API 문서(Swagger UI)에서 바로 테스트해볼 수 있습니다.

## 2. 제공하는 엔드포인트

### GET /members/lookup?phone=01012345678
일반 REST 방식 조회. 응답 예시:
```json
{
  "member_id": "M0001",
  "name": "홍길동",
  "phone": "01012345678",
  "grade": "VIP",
  "points": 15200,
  "join_date": "2021-03-15",
  "status": "정상"
}
```

테스트용 전화번호: `01012345678`, `01098765432`, `01055556666`

### POST /dialogflow-webhook
다이얼로그플로우 Fulfillment 웹훅 형식 그대로 응답합니다.
인텐트의 파라미터 이름을 `phone_number`로 맞춰서 설정하면 바로 연동됩니다.
(파라미터 이름이 다르면 main.py의 `params.get("phone_number", ...)` 부분을 수정하세요.)

## 3. 콜봇에서 호출할 공개 URL 만들기

로컬 서버는 외부(콜봇 플랫폼)에서 접속할 수 없으므로, 아래 중 하나로 공개 URL을 만들어야 합니다.

### 방법 A. ngrok (가장 빠름, 임시 데모용 추천)
1. https://ngrok.com 가입 후 설치
2. 로컬에서 API 실행: `uvicorn main:app --port 8000`
3. 새 터미널에서: `ngrok http 8000`
4. 터미널에 나오는 `https://xxxx.ngrok-free.app` 주소가 공개 URL입니다.
   - 예: `https://xxxx.ngrok-free.app/dialogflow-webhook`
   - 컴퓨터를 끄거나 ngrok을 종료하면 URL이 사라지니, 시연 직전에 켜두세요.

### 방법 B. Render.com (무료, 계속 켜두고 싶을 때)
1. 이 폴더를 GitHub 저장소에 올립니다.
2. https://render.com 에서 "New Web Service" → 해당 저장소 연결
3. Start Command: `uvicorn main:app --host 0.0.0.0 --port $PORT`
4. 배포가 끝나면 `https://프로젝트명.onrender.com` 같은 고정 URL이 생깁니다.
   (무료 플랜은 몇 분간 요청이 없으면 슬립 상태가 되어 첫 호출이 느릴 수 있습니다.)

## 4. 주의사항
- 목업 데이터이며, 실제 서비스 전환 시 `MEMBERS` 딕셔너리 부분을 실제 DB 조회 로직으로 교체해야 합니다.
- 실제 회원 개인정보를 이 코드에 넣지 마세요 (데모/테스트 목적으로만 사용).
- CORS는 전체 허용(`*`)으로 되어 있어 데모용으로만 적합합니다. 운영 환경에서는 제한이 필요합니다.
