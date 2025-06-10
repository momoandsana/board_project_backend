# FastAPI 게시판 백엔드

이 프로젝트는 FastAPI와 PostgreSQL을 기반으로 한 간단한 게시판 백엔드 서버입니다. 회원가입, 로그인, 게시글/댓글 CRUD, 이미지 업로드, 관리자 기능 등을 제공합니다.

## 🔧 설치 및 실행

```bash
pip install fastapi uvicorn sqlalchemy psycopg2-binary passlib[bcrypt] python-multipart
uvicorn main:app --reload
```

## 📌 기본 계정

| 아이디 | 비밀번호 | 권한    |
|--------|----------|---------|
| admin  | admin    | 관리자 ✅ |

## 🌐 허용된 CORS 출처

- http://localhost:5173
- http://localhost:5174
- https://board-project-frontend.vercel.app

## 📦 기술 스택

- FastAPI
- SQLAlchemy
- PostgreSQL (Render 호스팅)
- Passlib[bcrypt]
- Uvicorn
- python-multipart (파일 업로드)

## 🧪 주요 API

### 🔐 인증

- `POST /signup` - 회원가입
- `POST /login` - 로그인
- `DELETE /users/me` - 내 계정 삭제

### 👤 관리자

- `GET /admin/users` - 모든 유저 목록 조회
- `DELETE /admin/users/{user_id}` - 유저 삭제

### 📝 게시글

- `POST /posts` - 게시글 작성 (이미지 업로드 가능)
- `GET /posts?board=free` - 게시글 목록 조회
- `GET /posts/{post_id}` - 게시글 상세 보기
- `DELETE /posts/{post_id}` - 게시글 삭제

### 💬 댓글

- `POST /posts/{post_id}/comments` - 댓글 작성
- `GET /posts/{post_id}/comments` - 댓글 목록
- `DELETE /comments/{comment_id}` - 댓글 삭제

## 📁 기타

- 이미지 업로드 경로: `/static/파일명`
- `main.py` 실행 시 자동으로 DB 초기화 및 관리자 계정 생성

## 🗂 requirements.txt 내용

```txt
fastapi
uvicorn
sqlalchemy
psycopg2-binary
passlib[bcrypt]
python-multipart
```

---
