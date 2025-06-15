# FastAPI Bulletin Board Backend

This project is a simple bulletin board backend server built with FastAPI and PostgreSQL. It provides user registration, login, post/comment CRUD, image upload, and admin features.

## 🔧 Installation & Running

    pip install fastapi uvicorn sqlalchemy psycopg2-binary passlib[bcrypt] python-multipart
    uvicorn main:app --reload

## 📌 Default Account

| Username | Password | Role      |
|----------|----------|-----------|
| admin    | admin    | Admin ✅  |

## 🌐 Allowed CORS Origins

- http://localhost:5173
- http://localhost:5174
- https://board-project-frontend.vercel.app

## 📦 Tech Stack

- FastAPI  
- SQLAlchemy  
- PostgreSQL (hosted on Render)  
- Passlib[bcrypt]  
- Uvicorn  
- python-multipart (file upload)

## 🧪 Main API Endpoints

### 🔐 Authentication
- `POST /signup` — Register a new user  
- `POST /login` — Log in  
- `DELETE /users/me` — Delete my account  

### 👤 Admin
- `GET /admin/users` — Get list of all users  
- `DELETE /admin/users/{user_id}` — Delete a user  

### 📝 Posts
- `POST /posts` — Create a post (image upload supported)  
- `GET /posts?board=free` — List posts  
- `GET /posts/{post_id}` — Get post details  
- `DELETE /posts/{post_id}` — Delete a post  

### 💬 Comments
- `POST /posts/{post_id}/comments` — Create a comment  
- `GET /posts/{post_id}/comments` — List comments  
- `DELETE /comments/{comment_id}` — Delete a comment  

## 📁 Additional Information

- Image upload path: `/static/{filename}`  
- On `main.py` startup, database is initialized and the admin account is created automatically  

## 🗂 requirements.txt

    fastapi
    uvicorn
    sqlalchemy
    psycopg2-binary
    passlib[bcrypt]
    python-multipart
