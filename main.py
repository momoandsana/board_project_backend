from fastapi import FastAPI, Depends, HTTPException, UploadFile, File, Form, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.security import HTTPBasic, HTTPBasicCredentials
from fastapi.staticfiles import StaticFiles
from sqlalchemy import create_engine, Column, Integer, String, Text, DateTime, Boolean, ForeignKey
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker, relationship
from passlib.context import CryptContext
from datetime import datetime
from urllib.parse import quote_plus
import shutil
import time

# PostgreSQL 연결
DATABASE_URL = "postgresql://board_project_db_user:%s@dpg-d134b3buibrs73fq8kr0-a.singapore-postgres.render.com/board_project_db" % quote_plus("1epCVMoI6FAd30rjLF3fGvjG35kuSriu")
engine = create_engine(DATABASE_URL)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()

# 암호화 설정
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")
security = HTTPBasic()

# 모델 정의
default_image_path = None

class User(Base):
    __tablename__ = 'users'
    id = Column(Integer, primary_key=True, index=True)
    username = Column(String, unique=True, index=True)
    hashed_password = Column(String)
    is_admin = Column(Boolean, default=False)
    posts = relationship("Post", back_populates="owner")
    comments = relationship("Comment", back_populates="owner")

class Post(Base):
    __tablename__ = 'posts'
    id = Column(Integer, primary_key=True, index=True)
    title = Column(String, index=True)
    content = Column(Text)
    image_path = Column(String, nullable=True)
    board = Column(String, default="free")
    created_at = Column(DateTime, default=datetime.utcnow)
    owner_id = Column(Integer, ForeignKey('users.id'))
    views = Column(Integer, default=0)
    owner = relationship("User", back_populates="posts")
    comments = relationship("Comment", back_populates="post", cascade="all, delete")

class Comment(Base):
    __tablename__ = 'comments'
    id = Column(Integer, primary_key=True, index=True)
    content = Column(Text)
    created_at = Column(DateTime, default=datetime.utcnow)
    owner_id = Column(Integer, ForeignKey('users.id'))
    post_id = Column(Integer, ForeignKey('posts.id'))
    owner = relationship("User", back_populates="comments")
    post = relationship("Post", back_populates="comments")

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173", "http://localhost:5174"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.middleware("http")
async def log_requests(request: Request, call_next):
    start_time = time.time()
    response = await call_next(request)
    duration = time.time() - start_time
    print(f"[REQUEST] {request.method} {request.url.path} - {response.status_code} ({duration:.2f}s)")
    return response

@app.on_event("startup")
def on_startup():
    Base.metadata.create_all(bind=engine)
    db = SessionLocal()
    admin = db.query(User).filter(User.username == 'admin').first()
    if not admin:
        user = User(username='admin', hashed_password=pwd_context.hash('admin'), is_admin=True)
        db.add(user)
        db.commit()
    db.close()

app.mount("/static", StaticFiles(directory="static"), name="static")

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

def get_current_user(credentials: HTTPBasicCredentials = Depends(security), db=Depends(get_db)):
    user = db.query(User).filter(User.username == credentials.username).first()
    if not user or not pwd_context.verify(credentials.password, user.hashed_password):
        print(f"[LOGIN FAIL] username={credentials.username}")
        raise HTTPException(status_code=401, detail="Invalid credentials")
    print(f"[LOGIN SUCCESS] username={credentials.username}")
    return user

@app.post("/signup")
def signup(username: str = Form(...), password: str = Form(...), db=Depends(get_db)):
    print(f"[SIGNUP ATTEMPT] username={username}")
    if db.query(User).filter(User.username == username).first():
        print(f"[SIGNUP FAIL] username already exists: {username}")
        raise HTTPException(status_code=400, detail="Username already registered")
    user = User(username=username, hashed_password=pwd_context.hash(password))
    db.add(user)
    db.commit()
    print(f"[SIGNUP SUCCESS] New user registered: '{username}'")
    return {"success": True, "username": user.username}

@app.post("/login")
def login(credentials: HTTPBasicCredentials = Depends(security), db=Depends(get_db)):
    user = db.query(User).filter(User.username == credentials.username).first()
    valid = user and pwd_context.verify(credentials.password, user.hashed_password)
    print(f"[LOGIN API] username={credentials.username} result={'SUCCESS' if valid else 'FAIL'}")
    return {"success": bool(valid), "user": {"username": user.username, "is_admin": user.is_admin} if valid else None}

@app.delete("/users/me")
def delete_me(current: User = Depends(get_current_user), db=Depends(get_db)):
    print(f"[DELETE ACCOUNT] User '{current.username}' deleted their account")
    db.delete(current)
    db.commit()
    return {"success": True}

@app.get("/admin/users")
def list_users(current: User = Depends(get_current_user), db=Depends(get_db)):
    if not current.is_admin:
        raise HTTPException(status_code=403, detail="Not authorized")
    print(f"[ADMIN] User '{current.username}' requested user list")
    users = db.query(User).all()
    return [{"id": u.id, "username": u.username, "is_admin": u.is_admin} for u in users]

@app.delete("/admin/users/{user_id}")
def delete_user(user_id: int, current: User = Depends(get_current_user), db=Depends(get_db)):
    if not current.is_admin:
        raise HTTPException(status_code=403, detail="Not authorized")
    user = db.query(User).filter(User.id == user_id).first()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    print(f"[ADMIN DELETE USER] User '{current.username}' deleted user ID {user_id}")
    db.delete(user)
    db.commit()
    return {"success": True}

@app.post("/posts")
def create_post(title: str = Form(...), content: str = Form(...), board: str = Form(...), file: UploadFile = File(None), current: User = Depends(get_current_user), db=Depends(get_db)):
    image_path = None
    if file:
        path = f"static/{file.filename}"
        with open(path, "wb") as buffer:
            shutil.copyfileobj(file.file, buffer)
        image_path = path
    post = Post(title=title, content=content, board=board, owner_id=current.id, image_path=image_path)
    db.add(post)
    db.commit()
    db.refresh(post)
    print(f"[POST CREATED] User '{current.username}' created a post in '{board}' board with title '{title}'")
    return {"id": post.id}

@app.get("/posts")
def get_posts(board: str, db=Depends(get_db)):
    print(f"[GET POSTS] Fetching posts from board: '{board}'")
    posts = db.query(Post).filter(Post.board == board).order_by(Post.created_at.desc()).all()
    return [{"id": p.id, "title": p.title, "author": p.owner.username, "created_at": p.created_at, "views": p.views} for p in posts]

@app.get("/posts/{post_id}")
def get_post(post_id: int, db=Depends(get_db)):
    post = db.query(Post).filter(Post.id == post_id).first()
    if not post:
        raise HTTPException(status_code=404, detail="Post not found")
    post.views += 1
    db.commit()
    print(f"[GET POST] Viewed post #{post_id}, updated views to {post.views}")
    return {"id": post.id, "title": post.title, "content": post.content, "image": post.image_path, "author": post.owner.username, "created_at": post.created_at}

@app.delete("/posts/{post_id}")
def delete_post(post_id: int, current: User = Depends(get_current_user), db=Depends(get_db)):
    post = db.query(Post).filter(Post.id == post_id).first()
    if not post:
        raise HTTPException(status_code=404, detail="Post not found")
    if post.owner_id != current.id and not current.is_admin:
        raise HTTPException(status_code=403, detail="Not authorized")
    print(f"[POST DELETED] User '{current.username}' deleted post #{post_id}")
    db.delete(post)
    db.commit()
    return {"success": True}

@app.post("/posts/{post_id}/comments")
def add_comment(post_id: int, content: str = Form(...), current: User = Depends(get_current_user), db=Depends(get_db)):
    post = db.query(Post).filter(Post.id == post_id).first()
    if not post:
        raise HTTPException(status_code=404, detail="Post not found")
    comment = Comment(content=content, owner_id=current.id, post_id=post_id)
    db.add(comment)
    db.commit()
    db.refresh(comment)
    print(f"[COMMENT ADDED] User '{current.username}' commented on post #{post_id}: '{content[:30]}...'")
    return {"id": comment.id}

@app.get("/posts/{post_id}/comments")
def get_comments(post_id: int, db=Depends(get_db)):
    print(f"[GET COMMENTS] Fetching comments for post #{post_id}")
    comments = db.query(Comment).filter(Comment.post_id == post_id).order_by(Comment.created_at).all()
    return [{"id": c.id, "content": c.content, "author": c.owner.username, "created_at": c.created_at} for c in comments]

@app.delete("/comments/{comment_id}")
def delete_comment(comment_id: int, current: User = Depends(get_current_user), db=Depends(get_db)):
    comment = db.query(Comment).filter(Comment.id == comment_id).first()
    if not comment:
        raise HTTPException(status_code=404, detail="Comment not found")
    if comment.owner_id != current.id and not current.is_admin:
        raise HTTPException(status_code=403, detail="Not authorized")
    print(f"[COMMENT DELETED] User '{current.username}' deleted comment #{comment_id}")
    db.delete(comment)
    db.commit()
    return {"success": True}
