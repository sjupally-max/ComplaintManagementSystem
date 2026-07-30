from flask import Flask
from config import Config
from models import db, Category
from auth import auth_bp
from routes import main_bp


def create_app():
    app = Flask(__name__)
    app.config.from_object(Config)
    db.init_app(app)
    app.register_blueprint(auth_bp)
    app.register_blueprint(main_bp)

    with app.app_context():
        db.create_all()
        for name in ("General", "Technical", "Billing", "Service", "Other"):
            if not Category.query.filter_by(name=name).first():
                db.session.add(Category(name=name))
        db.session.commit()
    return app


if __name__ == "__main__":
    create_app().run(debug=True)
