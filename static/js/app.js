/**
 * AI Resume & Portfolio Builder - 프론트엔드 로직 (app.js)
 * 폼 제출, API 호출, 로딩/오류 처리, 결과 복사, 마크다운 다운로드 구현
 */

document.addEventListener("DOMContentLoaded", () => {
    // 1. 주요 DOM 엘리먼트 가져오기
    const form = document.getElementById("resumeForm");
    const generateBtn = document.getElementById("generateBtn");
    const loadingArea = document.getElementById("loadingArea");
    const errorArea = document.getElementById("errorArea");
    const errorMessage = document.getElementById("errorMessage");
    const placeholderArea = document.getElementById("placeholderArea");
    const resultArea = document.getElementById("resultArea");
    const resultContent = document.getElementById("resultContent");
    const copyBtn = document.getElementById("copyBtn");
    const downloadBtn = document.getElementById("downloadBtn");
    let currentRawResult = "";

    // 2. 오류 메시지 표시 헬퍼 함수
    function showError(message) {
        errorMessage.textContent = message;
        errorArea.classList.remove("hidden");
        loadingArea.classList.add("hidden");
        generateBtn.disabled = false;
        generateBtn.textContent = "✨ AI 이력서 & 포트폴리오 생성하기";
    }

    // 3. 오류 메시지 숨김 헬퍼 함수
    function clearError() {
        errorArea.classList.add("hidden");
        errorMessage.textContent = "";
    }

    // 4. 폼 제출 이벤트 처리
    form.addEventListener("submit", async (e) => {
        // 브라우저의 기본 페이지 새로고침 동작 방지
        e.preventDefault();
        clearError();

        // 입력값 가져오기
        const name = document.getElementById("name").value.trim();
        const targetRole = document.getElementById("targetRole").value.trim();
        const tone = document.getElementById("tone").value;
        const promptTypeRadio = document.querySelector('input[name="promptType"]:checked');
        const promptType = promptTypeRadio ? promptTypeRadio.value : "A";
        const experience = document.getElementById("experience").value.trim();
        const projects = document.getElementById("projects").value.trim();

        // 프론트엔드 유효성 검사 (빈칸 여부 확인)
        if (!name) {
            showError("이름을 입력해 주세요.");
            return;
        }
        if (!targetRole) {
            showError("지원 직무를 입력해 주세요.");
            return;
        }
        if (!experience) {
            showError("경력 사항을 입력해 주세요.");
            return;
        }
        if (!projects) {
            showError("프로젝트 경험을 입력해 주세요.");
            return;
        }

        // 로딩 UI 활성화
        placeholderArea.classList.add("hidden");
        resultArea.classList.add("hidden");
        loadingArea.classList.remove("hidden");
        generateBtn.disabled = true;
        generateBtn.textContent = "⏳ Gemini AI가 작성 중입니다...";

        // 서버로 전송할 페이로드 데이터 구성
        const payload = {
            name: name,
            target_role: targetRole,
            tone: tone,
            prompt_type: promptType,
            experience: experience,
            projects: projects
        };

        try {
            // Flask 백엔드의 /generate API로 POST 요청 전송
            const response = await fetch("/generate", {
                method: "POST",
                headers: {
                    "Content-Type": "application/json"
                },
                body: JSON.stringify(payload)
            });

            const data = await response.json();

            // HTTP 응답 상태가 정상이 아닌 경우 처리
            if (!response.ok) {
                const errorText = data.error || "알 수 없는 오류가 발생했습니다.";
                showError(`[오류] ${errorText}`);
                return;
            }

            // 생성 성공: 마크다운을 예쁜 HTML로 렌더링하여 화면에 표시
            currentRawResult = data.result;
            if (typeof marked !== "undefined") {
                resultContent.innerHTML = marked.parse(data.result);
            } else {
                resultContent.textContent = data.result;
            }

            loadingArea.classList.add("hidden");
            resultArea.classList.remove("hidden");

            // 결과 영역으로 부드럽게 스크롤 이동
            resultArea.scrollIntoView({ behavior: "smooth" });

        } catch (error) {
            // 네트워크 오류 또는 서버 접속 실패 처리
            console.error("요청 실패:", error);
            showError("서버와의 통신에 실패했습니다. 서버가 실행 중인지 확인해 주세요.");
        } finally {
            // 버튼 상태 원상 복구
            generateBtn.disabled = false;
            generateBtn.textContent = "✨ AI 이력서 & 포트폴리오 생성하기";
        }
    });

    // 5. 결과 클립보드 복사 버튼 이벤트
    copyBtn.addEventListener("click", async () => {
        const textToCopy = currentRawResult || resultContent.innerText;
        if (!textToCopy) return;

        try {
            await navigator.clipboard.writeText(textToCopy);
            const originalText = copyBtn.textContent;
            copyBtn.textContent = "✅ 복사 완료!";
            setTimeout(() => {
                copyBtn.textContent = originalText;
            }, 2000);
        } catch (err) {
            console.error("클립보드 복사 실패:", err);
            alert("클립보드 복사에 실패했습니다. 텍스트를 직접 드래그하여 복사해 주세요.");
        }
    });

    // 6. 마크다운(.md) 파일 다운로드 버튼 이벤트
    downloadBtn.addEventListener("click", () => {
        const textToDownload = currentRawResult || resultContent.innerText;
        if (!textToDownload) return;

        const nameInput = document.getElementById("name").value.trim() || "이력서";
        const filename = `${nameInput}_Resume_Portfolio.md`;

        // 텍스트를 담은 Blob 객체 생성
        const blob = new Blob([textToDownload], { type: "text/markdown;charset=utf-8" });
        const downloadUrl = URL.createObjectURL(blob);

        // 가상의 a 태그를 만들어 다운로드 트리거
        const tempLink = document.createElement("a");
        tempLink.href = downloadUrl;
        tempLink.download = filename;
        document.body.appendChild(tempLink);
        tempLink.click();

        // 다운로드 완료 후 정리
        document.body.removeChild(tempLink);
        URL.revokeObjectURL(downloadUrl);
    });
});
