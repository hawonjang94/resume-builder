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
        path_info = environ.get("PATH_INFO", "")
        # Vercel이 /api/index.py 또는 /api/index 경로를 붙여서 넘겼을 경우 원본 경로로 복원
        for prefix in ["/api/index.py", "/api/index", "/api"]:
            if path_info == prefix:
                path_info = "/"
                environ["PATH_INFO"] = path_info
                break
            elif path_info.startswith(prefix + "/"):
                path_info = path_info[len(prefix):]
                environ["PATH_INFO"] = path_info
                break
        return self.wsgi_app(environ, start_response)


app.wsgi_app = VercelPathMiddleware(app.wsgi_app)
