import os
import logging
from flask import Flask, render_template, request, jsonify
from dotenv import load_dotenv
import google.generativeai as genai

# 1. 환경변수 로드 (.env 파일에서 API 키 읽기)
load_dotenv()
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")

# 2. 백엔드 로깅 설정 (요청, 응답, 오류를 콘솔에 출력)
logging.basicConfig(
    level=logging.INFO,
    format="[%(asctime)s] %(levelname)s: %(message)s",
    datefmt="%Y-%m-%d %H:%M:%S"
)
logger = logging.getLogger(__name__)

# 3. Gemini API 초기화
if GEMINI_API_KEY and GEMINI_API_KEY.strip() != "your_gemini_api_key_here":
    genai.configure(api_key=GEMINI_API_KEY)
    logger.info("Gemini API가 성공적으로 설정되었습니다.")
else:
    logger.warning(".env 파일에 올바른 GEMINI_API_KEY가 설정되지 않았습니다.")

# 4. Flask 웹 애플리케이션 생성 (로컬 및 Vercel 서버리스 환경 경로 호환)
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
app = Flask(
    __name__,
    template_folder=os.path.join(BASE_DIR, "templates"),
    static_folder=os.path.join(BASE_DIR, "static")
)


@app.route("/manifest.json")
def manifest():
    """PWA 매니페스트 서빙"""
    return app.send_static_file("manifest.json")


@app.route("/sw.js")
def service_worker():
    """PWA 서비스 워커 서빙 (루트 스코프 적용)"""
    response = app.send_static_file("sw.js")
    response.headers["Content-Type"] = "application/javascript"
    return response


@app.route("/")
@app.route("/api")
@app.route("/api/index")
@app.route("/api/index.py")
def index():
    """메인 화면 렌더링"""
    logger.info("메인 페이지(/) 요청 접수")
    return render_template("index.html")


@app.errorhandler(404)
def handle_404(e):
    """미등록 경로 접근 시 메인 화면으로 안전하게 폴백"""
    logger.warning(f"미등록 경로 요청({request.path}) -> 메인 화면으로 안내")
    if request.path.endswith("/generate") and request.method == "POST":
        return generate()
    return render_template("index.html")


@app.route("/generate", methods=["POST"])
@app.route("/api/generate", methods=["POST"])
@app.route("/api/index.py/generate", methods=["POST"])
def generate():
    """이력서 및 포트폴리오 생성 API 엔드포인트"""
    try:
        # 클라이언트가 전송한 JSON 데이터 수신
        data = request.get_json()
        if not data:
            logger.warning("요청 본문(JSON) 데이터가 없습니다.")
            return jsonify({"error": "입력 데이터가 전송되지 않았습니다."}), 400

        name = data.get("name", "").strip()
        target_role = data.get("target_role", "").strip()
        experience = data.get("experience", "").strip()
        projects = data.get("projects", "").strip()
        tone = data.get("tone", "전문적인").strip()
        prompt_type = data.get("prompt_type", "A").strip()

        # Backend 입력값 검증 (필수 필드 누락 여부 확인)
        if not name:
            logger.warning("입력 검증 실패: 이름 누락")
            return jsonify({"error": "이름을 입력해 주세요."}), 400
        if not target_role:
            logger.warning("입력 검증 실패: 지원 직무 누락")
            return jsonify({"error": "지원 직무를 입력해 주세요."}), 400
        if not experience:
            logger.warning("입력 검증 실패: 경력 사항 누락")
            return jsonify({"error": "경력 사항을 입력해 주세요."}), 400
        if not projects:
            logger.warning("입력 검증 실패: 프로젝트 경험 누락")
            return jsonify({"error": "프로젝트 경험을 입력해 주세요."}), 400

        # API Key 등록 여부 검증
        if not GEMINI_API_KEY or GEMINI_API_KEY.strip() == "your_gemini_api_key_here":
            logger.error("유효한 GEMINI_API_KEY가 존재하지 않습니다.")
            return jsonify({
                "error": ".env 파일에 유효한 Gemini API 키가 설정되지 않았습니다. .env 파일을 확인해 주세요."
            }), 500

        logger.info(
            f"생성 요청 시작 -> 이름: {name}, 직무: {target_role}, "
            f"톤: {tone}, 프롬프트 타입: {prompt_type}"
        )

        # 프롬프트 엔지니어링: Prompt A(일반) vs Prompt B(전문가)
        if prompt_type == "B":
            # Prompt B: 전문가 모드 (STAR 기법, 성과 지표 수치화, 전문 역량 극대화)
            system_instruction = (
                "당신은 글로벌 테크 기업의 최고 채용 심사관이자 커리어 컨설턴트입니다. "
                "사용자가 제공한 정보를 바탕으로 인사담당자의 시선을 사로잡을 수 있는 "
                "고도로 전문적이고 매력적인 이력서(Resume)와 포트폴리오(Portfolio) 초안을 작성하세요.\n\n"
                "[작성 가이드라인]\n"
                "1. 메인 제목은 '#', 각 소제목은 '##'으로 작성하여 구조를 명확히 구분하세요.\n"
                "2. 각 섹션, 소제목, 주요 항목마다 내용과 잘 어울리는 다양하고 센스 있는 이모지(💼, 🚀, 🛠️, 📈, 💡, 🎯, ✨ 등)를 적극 활용하세요.\n"
                "3. STAR(Situation, Task, Action, Result) 기법을 엄격히 적용하여 경험을 재구성하세요.\n"
                "4. 단순한 업무 나열을 배제하고, 기여도와 임팩트를 구체적인 수치와 지표로 나타내세요.\n"
                "5. 핵심 단어나 항목 이름은 볼드체(**단어**)로 강조하세요."
            )
        else:
            # Prompt A: 일반 모드 (표준적이고 균형 잡힌 명확한 서술)
            system_instruction = (
                "당신은 친절하고 역량 있는 취업 전문 코치입니다. "
                "사용자가 제공한 정보를 바탕으로 읽기 쉽고 체계적인 "
                "이력서(Resume)와 포트폴리오(Portfolio) 초안을 작성하세요.\n\n"
                "[작성 가이드라인]\n"
                "1. 메인 제목은 '#', 각 소제목은 '##'으로 작성하여 한눈에 들어오게 구성하세요.\n"
                "2. 각 제목과 핵심 항목마다 어울리는 다채로운 이모지(🌟, 📌, 💼, 🎓, 💻, 🏆 등)를 풍성하게 사용하여 친근하고 읽기 즐겁게 꾸며주세요.\n"
                "3. 명확하고 정돈된 문장으로 강점을 표현하세요.\n"
                "4. 핵심 항목명은 볼드체(**항목**)로 강조하세요."
            )

        user_content = f"""
{system_instruction}

[지원자 정보]
- 이름: {name}
- 지원 직무: {target_role}
- 문체 스타일(Tone): {tone}

[경력 사항]
{experience}

[프로젝트 경험]
{projects}

[출력 형식 가이드]
아래와 같이 제목과 소제목을 마크다운(#, ##)과 이모티콘으로 명확히 구분하여 작성해 주세요:
# 📋 {name} 님의 맞춤형 이력서 & 포트폴리오

## 1. 💼 Resume (이력서)
- 👤 **프로필 요약 (Summary)**: 한 줄 소개 및 핵심 강점
- 🛠️ **핵심 보유 역량 (Key Skills)**: 직무 전문 기술 및 역량
- 🏢 **경력 상세 기술 (Work Experience)**: 주요 담당 업무 및 성과

## 2. 🚀 Portfolio (포트폴리오)
- 📌 **대표 프로젝트 개요**: 프로젝트 소개 및 목표
- 💡 **역할 및 문제 해결 과정**: 기술적 난관 극복 과정
- 📈 **주요 성과 및 배운 점**: 정량적/정성적 성과

지금 바로 다채로운 이모티콘과 강조 서식을 살려 작성을 시작하세요.
"""

        # 사용자가 지정한 모델: gemini-3.5-flash-lite
        target_model = "gemini-3.5-flash-lite"
        logger.info(f"지정된 모델 호출 시도: {target_model}")

        try:
            model = genai.GenerativeModel(target_model)
            response = model.generate_content(user_content)
        except Exception as model_err:
            logger.warning(
                f"{target_model} 호출 실패 ({model_err}). "
                f"계정에서 지원하는 대체 Flash 모델을 탐색합니다."
            )
            # 404 등 오류 발생 시 계정 내 활성화된 Flash 모델로 안전하게 대체
            try:
                available_models = [
                    m.name.replace("models/", "")
                    for m in genai.list_models()
                    if "generateContent" in m.supported_generation_methods
                ]
                logger.info(f"계정 내 사용 가능한 모델 목록: {available_models}")
                fallback = None
                for candidate in ["gemini-2.5-flash", "gemini-2.0-flash", "gemini-1.5-flash", "gemini-pro"]:
                    if candidate in available_models:
                        fallback = candidate
                        break
                if not fallback and available_models:
                    fallback = available_models[0]
                if not fallback:
                    raise model_err

                logger.info(f"대체 모델로 재시도: {fallback}")
                model = genai.GenerativeModel(fallback)
                response = model.generate_content(user_content)
            except Exception:
                raise model_err

        if not response or not response.text:
            logger.error("Gemini API에서 빈 응답이 반환되었습니다.")
            return jsonify({"error": "AI가 응답을 생성하지 못했습니다. 잠시 후 다시 시도해 주세요."}), 500

        result_text = response.text
        logger.info(f"생성 완료 -> 지원자: {name} (생성된 글자 수: {len(result_text)})")

        return jsonify({
            "success": True,
            "result": result_text
        })

    except Exception as e:
        logger.error(f"생성 도중 오류 발생: {str(e)}", exc_info=True)
        return jsonify({
            "error": f"AI 처리 중 서버 오류가 발생했습니다: {str(e)}"
        }), 500


if __name__ == "__main__":
    logger.info("Flask 백엔드 서버를 시작합니다. (http://127.0.0.1:5000)")
    app.run(debug=True, host="127.0.0.1", port=5000)
