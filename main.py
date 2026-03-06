from fastapi import FastAPI, Request, Depends, Form, HTTPException,Query
from urllib import request

from fastapi import FastAPI, Request, Depends, Form, HTTPException
from sqlalchemy.orm import Session
from sqlalchemy.sql.annotation import Annotated
from typing import Annotated
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


@app.post("/post/{post_id}/delete")
async def delete_post(
    post_id: int, db: Session = Depends(get_db), secret_key: str = Form(...)
):
    post = db.query(models.Post).filter(models.Post.id == post_id).first()

    if not post:
        raise HTTPException(status_code=404, detail="Post not found")

    if secret_key == "123":
        db.delete(post)
        db.commit()
        return RedirectResponse(url="/", status_code=303)
    else:
        return "Not authorized"


@app.get("/post/{post_id}/update")
async def update_post(request: Request, post_id: int, db: Session = Depends(get_db)):
    post = db.query(models.Post).filter(models.Post.id == post_id).first()

    if not post:
        raise HTTPException(status_code=404, detail="Post not found")

    return templates.TemplateResponse(
        "update_post.html", {"request": request, "post": post}
    )


@app.post("/post/{post_id}/update")
async def update_post(
    post_id: int,
    title: str = Form(...),
    content: str = Form(...),
    db: Session = Depends(get_db),
):
    post = db.query(models.Post).filter(models.Post.id == post_id).first()

    post.title = title
    post.content = content

    db.commit()

    return RedirectResponse(url="/", status_code=303)


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
async def home( request: Request,q:Annotated[str|None,Query(min_length=0, max_length=20)] = None, db: Session = Depends(get_db)):
    if q:
        posts = db.query(models.Post).filter(models.Post.title.contains(q)).all()
    else:
        posts = db.query(models.Post).order_by(models.Post.created_at.desc()).all()
    return templates.TemplateResponse(
        "index.html", {"request": request, "posts": posts}
    )
