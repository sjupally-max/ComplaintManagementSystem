import os


class Config:
    SECRET_KEY = os.environ.get("SECRET_KEY", "change-this-secret-before-production")
    SQLALCHEMY_DATABASE_URI = "sqlite:///complaints.db"
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    UPLOAD_FOLDER = os.path.join(os.path.dirname(__file__), "static", "uploads")
    MAX_CONTENT_LENGTH = 8 * 1024 * 1024
    ALLOWED_EXTENSIONS = {"png", "jpg", "jpeg", "gif", "pdf", "doc", "docx"}
