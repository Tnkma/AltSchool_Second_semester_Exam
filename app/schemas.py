from pydantic import BaseModel, EmailStr

class contactBase(BaseModel):
    name: str
    email: EmailStr
    message: str

class NewsletterBase(BaseModel):
    name: str
    email: EmailStr

class FeedbackBase(BaseModel):
    name: str
    email: EmailStr
    feedback: str
