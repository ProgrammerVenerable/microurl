from fastapi import FastAPI, Request, Form, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import Annotated
from fastapi.staticfiles import StaticFiles
from fastapi.responses import HTMLResponse
from sqlalchemy.exc import IntegrityError
from pydantic import HttpUrl, ValidationError
from fastapi.templating import Jinja2Templates
from .functions import generate_short_code
from .database import engine, Base, get_db
from fastapi.responses import RedirectResponse
import src.microurl.models as models

app = FastAPI()

app.mount("/static", StaticFiles(directory="src/microurl/static"), name="static")

templates = Jinja2Templates(directory="./src/microurl/templates")

Base.metadata.create_all(engine)

@app.get("/", response_class=HTMLResponse)
def home(request: Request, short_url: str | None = None):
    return templates.TemplateResponse(
        request,
        "home.html",
        {"short_url": short_url}
    )

@app.post("/", response_class=HTMLResponse)
def compute_ShortURL(request: Request, db: Annotated[Session, Depends(get_db)], u: str = Form(...)):
    try:
        original_url = str(HttpUrl(u))
    except ValidationError:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Enter a valid URL")

    while True:
        short_code = generate_short_code()
        code = db.get(models.Code, short_code)
        if not code:
            break

    final_url = models.Code(short_code=short_code, original_url=original_url)

    db.add(final_url)
    db.commit()
    db.refresh(final_url)
    
    return RedirectResponse(url=f"/success/{short_code}", status_code=status.HTTP_303_SEE_OTHER)


@app.get("/success/{short_code}")
def show_success(request: Request, short_code: str, db: Annotated[Session, Depends(get_db)]):
    code = db.get(models.Code, short_code)
    if not code:
        return templates.TemplateResponse(request, "error.html", status_code=status.HTTP_404_NOT_FOUND)

    microURL = f"http://127.0.0.1:8000/{short_code}"
    return templates.TemplateResponse(request, "success.html", {"short_url": microURL, "original_url": code.original_url})


@app.get("/{short_code}", response_class=HTMLResponse)
def compute_original_url(request: Request, short_code: str, db: Annotated[Session, Depends(get_db)]):
    url = db.get(models.Code, short_code)
    if not url:
        return templates.TemplateResponse(
            request,
            "error.html",
            status_code=status.HTTP_404_NOT_FOUND,
        )

    return RedirectResponse(url=url.original_url, status_code=status.HTTP_307_TEMPORARY_REDIRECT)