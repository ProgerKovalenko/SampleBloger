from fastapi import FastAPI, Request, Depends, Form, HTTPException
from sqlalchemy.orm import Session
from database import SessionLocal, engine
from fastapi.responses import HTMLResponse, RedirectResponse
from fastapi.templating import Jinja2Templates
import models

models.Base.metadata.create_all(bind=engine)

app = FastAPI()


templates = Jinja2Templates(directory="templates")


def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


@app.get("/create", response_class=HTMLResponse)
async def create_template(request: Request):
    return templates.TemplateResponse("create_post.html", {"request": request})


@app.get("/post/{post_id}", response_class=HTMLResponse)
async def get_post(request: Request, post_id: int, db: Session = Depends(get_db)):
    post = db.query(models.Post).filter(models.Post.id == post_id).first()

    if not post:
        raise HTTPException(status_code=404, detail="Post not found")

    return templates.TemplateResponse(
        "post_detail.html", {"request": request, "post": post}
    )


@app.post("/create")
async def add_post(
    title: str = Form(...),
    content: str = Form(...),
    author: str = Form(...),
    db: Session = Depends(get_db),
):
    new_post = models.Post(title=title, content=content, author=author)
    db.add(new_post)
    db.commit()

    db.add(new_post)
    db.commit()
    db.refresh(new_post)

    return RedirectResponse(url="/", status_code=303)


@app.get("/", response_class=HTMLResponse)
async def home(request: Request, db: Session = Depends(get_db)):
    posts = db.query(models.Post).order_by(models.Post.created_at.desc()).all()

    return templates.TemplateResponse(
        "index.html", {"request": request, "posts": posts}
    )
