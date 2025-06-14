from typing import Union
from fastapi import FastAPI, Request, Form, Depends
from fastapi.responses import HTMLResponse
from fastapi.templating import Jinja2Templates
from app.database import SessionLocal, Base, engine
from sqlalchemy.orm import Session
import app.models as models
from app.utils import send_email
import re


# Create the database tables
Base.metadata.create_all(bind=engine)
app = FastAPI()

template = Jinja2Templates(directory="app/templates")

# Get db session
def get_database():
    """ Get a database session."""
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
    
@app.get("/", response_class=HTMLResponse)
async def homepage(request: Request, db: Session = Depends(get_database)):
    feedbacks = (
        db.query(models.Feedback)
        .order_by(models.Feedback.id.desc())
        .limit(3)
        .all()
    )
    return template.TemplateResponse("index.html", {
        "request": request,
        "feedbacks": feedbacks
    })




# Show contact form
@app.get("/contact", response_class=HTMLResponse)
async def contact_form(request: Request):
    """ Display the contact form page."""
    return template.TemplateResponse("contact.html", {"request": request, "title": "Contact Us"})



@app.post("/contact", response_class=HTMLResponse)
async def contact(
    request: Request,
    name: str = Form(...),
    email: str = Form(...),
    message: str = Form(...),
    db: Session = Depends(get_database)
):
    # Save to database
    new_contact = models.Contact(name=name, email=email, message=message)
    db.add(new_contact)
    db.commit()
    db.refresh(new_contact)

    # Send email
    send_email(name, email, message)

    return template.TemplateResponse("contact.html", {
        "request": request,
        "name": name,
        "email": email,
        "message": message,
        "success": True
    })

    

@app.post("/newsletter", response_class=HTMLResponse)
async def newsletter(
    request: Request,
    name: str = Form(...),
    email: str = Form(...),
    db: Session = Depends(get_database)
):
    # Validate name
    if len(name.strip()) < 2:
        return template.TemplateResponse("index.html", {
            "request": request,
            "error": "Name is too short.",
            # force modal to open again
            "show_modal": True  
        })

    # Validate email
    if not re.match(r"[^@]+@[^@]+\.[^@]+", email):
        return template.TemplateResponse("index.html", {
            "request": request,
            "error": "Invalid email format.",
            "show_modal": True
        })

    # Check if email already exists
    try:
        existing = db.query(models.Newsletter).filter(models.Newsletter.email == email).first()
        if existing:
            return template.TemplateResponse("index.html", {
                "request": request,
                "error": "Email already subscribed.",
                "show_modal": True
            })
    except Exception as e:
        return template.TemplateResponse("index.html", {
            "request": request,
            "error": f"Database error: {str(e)}",
            "show_modal": True
        })

    # Save new subscriber
    new_subscriber = models.Newsletter(name=name, email=email)
    db.add(new_subscriber)
    db.commit()

    return template.TemplateResponse("index.html", {
        "request": request,
        "success": "Thanks for subscribing!",
        "show_modal": True
    })

@app.post("/feedback", response_class=HTMLResponse)
async def handle_feedback(
    request: Request,
    name: str = Form(...),
    email: str = Form(...),
    message: str = Form(...),
    db: Session = Depends(get_database)
):
    # 1. Save feedback to DB
    new_feedback = models.Feedback(name=name, email=email, feedback=message)
    db.add(new_feedback)
    db.commit()

    # 2. Email notification to YOU
    await send_email(
        subject="📬 New Feedback Received",
        body=f"Name: {name}\nEmail: {email}\nMessage:\n{message}",
        to_email="youradminemail@gmail.com"
    )

    # 3. Thank-you email to the visitor
    await send_email(
        subject="🙏 Thank You for Your Feedback!",
        body=f"Hi {name},\n\nThank you for your kind feedback. We appreciate your time and support!\n\n– Team MediSync",
        to_email=email
    )

    return template.TemplateResponse("index.html", {
        "request": request,
        "name": name,
        "email": email,
        "feedback": message,
        "success": True
    })
