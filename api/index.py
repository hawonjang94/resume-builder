import os
import sys

# 프로젝트 루트 디렉터리를 sys.path에 추가하여 app 모듈 정상 임포트
root_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if root_dir not in sys.path:
    sys.path.insert(0, root_dir)

from app import app


# Vercel Serverless 요청 경로 보정 미들웨어
class VercelPathMiddleware:
    def __init__(self, wsgi_app):
        self.wsgi_app = wsgi_app

    def __call__(self, environ, start_response):
        # 1. Vercel이 rewrites 시 전달하는 원본 요청 경로 헤더 확인
        original_path = (
            environ.get("HTTP_X_MATCHED_PATH")
            or environ.get("HTTP_X_FORWARDED_URI")
            or environ.get("REQUEST_URI")
            or environ.get("RAW_URI")
        )

        if original_path:
            clean_path = original_path.split("?")[0]
            # /api prefix가 없는 실제 요청 경로(/static/..., /sw.js 등)는 그대로 복원
            if not any(clean_path == p or clean_path.startswith(p + "/") for p in ["/api/index.py", "/api/index", "/api"]):
                environ["PATH_INFO"] = clean_path
            else:
                for prefix in ["/api/index.py", "/api/index", "/api"]:
                    if clean_path == prefix:
                        environ["PATH_INFO"] = "/"
                        break
                    elif clean_path.startswith(prefix + "/"):
                        environ["PATH_INFO"] = clean_path[len(prefix):]
                        break
        else:
            path_info = environ.get("PATH_INFO", "")
            for prefix in ["/api/index.py", "/api/index", "/api"]:
                if path_info == prefix:
                    environ["PATH_INFO"] = "/"
                    break
                elif path_info.startswith(prefix + "/"):
                    environ["PATH_INFO"] = path_info[len(prefix):]
                    break

        return self.wsgi_app(environ, start_response)


app.wsgi_app = VercelPathMiddleware(app.wsgi_app)
