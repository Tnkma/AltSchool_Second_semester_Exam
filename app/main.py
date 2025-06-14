from typing import Union
from fastapi import FastAPI, Request, Form, Depends, status
from fastapi.responses import HTMLResponse, RedirectResponse
from fastapi.templating import Jinja2Templates
from app.database import SessionLocal, Base, engine
from sqlalchemy.orm import Session
import app.models as models
from app.utils import send_email
import re
from starlette.middleware.sessions import SessionMiddleware




# Initialize app and templates
app = FastAPI()
templates = Jinja2Templates(directory="app/templates")
app.add_middleware(SessionMiddleware, secret_key="our-secret-key")

# Create DB tables.
Base.metadata.create_all(bind=engine)

# Dependency: DB session
def get_database():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

# ----------------------------------------
# HOME PAGE
# ----------------------------------------
@app.get("/", response_class=HTMLResponse)
async def home(request: Request, db: Session = Depends(get_database)):
    feedbacks = db.query(models.Feedback).order_by(models.Feedback.id.desc()).limit(3).all()

    newsletter_error = request.session.pop("newsletter_error", None)
    newsletter_success = request.session.pop("newsletter_success", None)

    feedback_success = request.session.pop("feedback_success", None)

    show_modal = True if newsletter_error or newsletter_success else False
    show_feedback_modal = request.query_params.get("show_feedback_modal", None)

    return templates.TemplateResponse("index.html", {
        "request": request,
        "feedbacks": feedbacks,
        "error": newsletter_error,
        "success": newsletter_success,
        "show_modal": show_modal,
        "feedback_success": feedback_success,
        "show_feedback_modal": show_feedback_modal
    })


# ----------------------------------------
# CONTACT PAGE
# ----------------------------------------
@app.get("/contact", response_class=HTMLResponse)
async def contact_form(request: Request):
    return templates.TemplateResponse("contact.html", {"request": request})

@app.post("/contact", response_class=HTMLResponse)
async def contact(
    request: Request,
    name: str = Form(...),
    email: str = Form(...),
    message: str = Form(...),
    db: Session = Depends(get_database)
):
    # Save contact info
    new_contact = models.Contact(name=name, email=email, message=message)
    db.add(new_contact)
    db.commit()

    # Send emails (admin + thank you)
    await send_email(
        subject=f"📬 New Contact Message from {name}",
        body=f"Name: {name}\nEmail: {email}\nMessage:\n{message}",
        to_email="youradminemail@gmail.com"
    )
    await send_email(
        subject="✅ Thanks for Contacting Us!",
        body=f"Hi {name},\n\nThank you for reaching out. We’ll get back to you soon!\n\n– Tnkma Team",
        to_email=email
    )

    return templates.TemplateResponse("contact.html", {
        "request": request,
        "success": True,
        "name": name,
        "email": email,
        "message": message
    })

# ----------------------------------------
# NEWSLETTER
# ------------------------------------

@app.post("/newsletter", response_class=HTMLResponse)
async def newsletter(
    request: Request,
    name: str = Form(...),
    email: str = Form(...),
    db: Session = Depends(get_database)
):
    # Basic validation
    if len(name.strip()) < 2:
        request.session["newsletter_error"] = "Name is too short."
        return RedirectResponse(
            url="/?show_modal=True", status_code=status.HTTP_303_SEE_OTHER
    )

    if not re.match(r"[^@]+@[^@]+\.[^@]+", email):
        request.session["newsletter_error"] = "Invalid email format."
        return RedirectResponse(url="/?show_modal=True", status_code=status.HTTP_303_SEE_OTHER)

    # Check if email already exists
    existing = db.query(models.Newsletter).filter(models.Newsletter.email == email).first()
    if existing:
        request.session["newsletter_error"] = "Email already subscribed."
        return RedirectResponse(url="/?show_modal=True", status_code=status.HTTP_303_SEE_OTHER)

    # Save subscriber
    new_subscriber = models.Newsletter(name=name, email=email)
    db.add(new_subscriber)
    db.commit()

    request.session["newsletter_success"] = "Thanks for subscribing!"
    return RedirectResponse(url="/?show_modal=True", status_code=status.HTTP_303_SEE_OTHER)


# ----------------------------------------
# FEEDBACK
# ----------------------------------------
@app.post("/feedback", response_class=HTMLResponse)
async def handle_feedback(
    request: Request,
    name: str = Form(...),
    email: str = Form(...),
    message: str = Form(...),
    db: Session = Depends(get_database)
):
    new_feedback = models.Feedback(name=name, email=email, feedback=message)
    db.add(new_feedback)
    db.commit()

    await send_email(
        subject="📬 New Feedback Received",
        body=f"Name: {name}\nEmail: {email}\nMessage:\n{message}",
        to_email="onwusilikenonso@gmail.com"
    )

    await send_email(
        subject="🙏 Thank You for Your Feedback!",
        body=f"Hi {name},\n\nThank you for your kind feedback. We appreciate your time and support!\n\n– Team Tnkma",
        to_email=email
    )

    # Flash session message
    request.session["feedback_success"] = "✅ Thank you for your feedback!"
    return RedirectResponse(url="/?show_feedback_modal=true", status_code=status.HTTP_303_SEE_OTHER)

