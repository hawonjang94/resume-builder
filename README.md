# 📋 AI Resume & Portfolio Builder

> Google Gemini AI를 활용하여 맞춤형 이력서와 포트폴리오 초안을 자동으로 생성하는 Flask 기반 웹 애플리케이션입니다.

---

## 🚀 주요 기능

- 📝 **간편한 정보 입력**: 이름, 지원 직무, 경력, 프로젝트, 문체(Tone) 입력 폼
- 🤖 **AI 이력서 생성**: Google Gemini API를 호출하여 맞춤형 이력서 & 포트폴리오 초안 자동 생성
- ✏️ **Prompt A / B 선택**: 일반 모드(친절한 코치) vs 전문가 모드(STAR 기법 기반) 선택 가능
- 📋 **결과 복사**: 생성된 텍스트를 클립보드로 즉시 복사
- 💾 **Markdown 다운로드**: 생성 결과를 `.md` 파일로 바로 다운로드
- ✅ **이중 입력 검증**: Frontend(JavaScript) + Backend(Flask) 양쪽에서 입력값 검증
- 🔒 **API Key 보안 관리**: `.env` 파일로 API 키 안전하게 분리 보관
- 📡 **백엔드 로깅**: 요청, 응답, 오류 내역을 터미널 콘솔에 실시간 출력

---

## 🗂️ 파일 구조

```
resume-builder/
├── app.py              # Flask 백엔드 서버 (Gemini API 연동, 라우팅, 로깅)
├── requirements.txt    # 필요한 Python 패키지 목록
├── .env                # 실제 API Key 보관 (Git 제외 - 절대 공유 금지!)
├── .env.example        # API Key 입력 형식 안내 견본 파일
├── .gitignore          # Git 추적 제외 파일 목록
├── README.md           # 프로젝트 설명서 (현재 파일)
├── templates/
│   └── index.html      # 메인 웹 화면 (입력 폼 + 결과 표시)
└── static/
    ├── css/
    │   └── style.css   # 스타일시트 (노란색 배경 + 하늘색 입력창 디자인)
    └── js/
        └── app.js      # 프론트엔드 로직 (폼 제출, 결과 렌더링, 복사, 다운로드)
```

---

## ⚙️ 시작하는 방법

### 1. 프로젝트 폴더로 이동
```powershell
Set-Location "C:\AI-study\resume-builder"
```

### 2. 가상환경 활성화
```powershell
.\venv\Scripts\Activate.ps1
```

### 3. `.env` 파일 생성 및 API Key 입력
```powershell
Copy-Item .env.example .env
notepad .env
```
메모장에서 `your_gemini_api_key_here` 부분을 본인의 실제 Gemini API Key로 교체하고 저장합니다.

> 💡 API Key는 [Google AI Studio](https://aistudio.google.com/app/apikey)에서 무료로 발급받을 수 있습니다.

### 4. 패키지 설치 (최초 1회만)
```powershell
py -m pip install -r requirements.txt
```

### 5. 서버 실행
```powershell
py app.py
```

### 6. 브라우저에서 접속
```
http://127.0.0.1:5000
```

---

## 🛠️ 사용 기술 스택

| 구분 | 기술 |
|---|---|
| **Backend** | Python, Flask |
| **AI 모델** | Google Gemini API (`gemini-3.5-flash-lite`) |
| **Frontend** | HTML5, CSS3, JavaScript (Vanilla) |
| **Markdown 렌더링** | marked.js (CDN) |
| **환경변수 관리** | python-dotenv |
| **버전 관리** | Git |

---

## 🔐 보안 주의사항

- `.env` 파일에는 실제 API Key가 들어있으므로 **절대 GitHub에 올리거나 타인과 공유하지 마세요.**
- `.gitignore`에 `.env`가 등록되어 있어 `git add .`를 실행해도 자동으로 제외됩니다.
- API Key가 유출되었다고 의심된다면 즉시 [Google AI Studio](https://aistudio.google.com/app/apikey)에서 해당 Key를 삭제하고 새로 발급받으세요.

---

## 📌 개발 정보

- **개발 환경**: Windows 11, PowerShell
- **Python 버전**: 3.10 이상
- **개발 방식**: Flask Development Server (학습/테스트용)

---

## 🙌 만든 사람

AI Resume & Portfolio Builder는 Antigravity AI 코딩 강의를 통해 처음부터 직접 만든 첫 번째 풀스택 웹 프로젝트입니다.
