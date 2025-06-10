Board Project API

간단한 게시판 백엔드 REST API입니다. FastAPI와 SQLAlchemy, PostgreSQL 기반으로 회원, 게시글, 댓글 기능을 제공합니다.

주요 기능
	•	회원가입/로그인 (HTTP Basic Auth)
	•	관리자 사용자 생성 및 관리
	•	게시글 CRUD (이미지 업로드 지원)
	•	댓글 작성/조회/삭제
	•	게시글 조회 시 조회수 카운트

사용 기술
	•	Python 3.9+
	•	FastAPI
	•	Uvicorn
	•	SQLAlchemy
	•	psycopg2-binary
	•	Passlib (bcrypt)
	•	python-multipart

설치 및 실행
	1.	저장소 클론

git clone <REPO_URL>
cd <REPO_DIR>


	2.	가상환경 생성 및 활성화

python -m venv venv
source venv/bin/activate   # macOS/Linux
venv\\Scripts\\activate  # Windows


	3.	의존성 설치

pip install fastapi uvicorn sqlalchemy psycopg2-binary passlib[bcrypt] python-multipart


	4.	환경 변수 설정 (필요 시)

export DATABASE_URL="postgresql://USER:PASSWORD@HOST:PORT/DB_NAME"


	5.	데이터베이스 초기화 및 관리자 계정 생성

uvicorn main:app --reload

서버 기동 시 users 테이블과 기본 admin 계정이 자동 생성됩니다.

실행

uvicorn main:app --host 0.0.0.0 --port 8000 --reload

API 엔드포인트

메서드	경로	설명
POST	/signup	회원가입 (username, password)
POST	/login	로그인 (HTTP Basic 인증)
DELETE	/users/me	내 계정 삭제
GET	/admin/users	전체 사용자 조회 (관리자)
DELETE	/admin/users/{user_id}	사용자 삭제 (관리자)
POST	/posts	게시글 생성 (title, content, board, file)
GET	/posts?board={board}	게시글 목록 조회
GET	/posts/{post_id}	게시글 상세 조회 (조회수 증가)
DELETE	/posts/{post_id}	게시글 삭제
POST	/posts/{post_id}/comments	댓글 작성 (content)
GET	/posts/{post_id}/comments	댓글 목록 조회
DELETE	/comments/{comment_id}	댓글 삭제

정적 파일 제공
	•	업로드된 이미지는 /static/{filename} 경로로 접근 가능합니다.

CORS 설정
	•	허용 출처:
	•	http://localhost:5173
	•	http://localhost:5174
	•	https://board-project-frontend.vercel.app

라이선스

MIT
