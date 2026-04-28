from flask import Flask
from config import Config
from extensions import db, login_manager, csrf


def create_app():
    app = Flask(__name__)
    app.config.from_object(Config)

    db.init_app(app)
    login_manager.init_app(app)
    @login_manager.user_loader
    def load_user(user_id):
        from models import User
        return User.query.get(int(user_id))
    csrf.init_app(app)

    login_manager.login_view = 'auth.login'
    login_manager.login_message = 'Пожалуйста, войдите для доступа к панели управления.'

    # Импорт и регистрация blueprint'ов
    from routes.public import public_bp
    from routes.auth import auth_bp
    from routes.admin import admin_bp

    app.register_blueprint(public_bp)
    app.register_blueprint(auth_bp)
    app.register_blueprint(admin_bp)

    with app.app_context():
        from models import User, Survey, Question, Option, Response, Answer
        db.create_all()

    return app

if __name__ == '__main__':
    app = create_app()
    app.run(debug=True)