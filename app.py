from flask import Flask
from config import Config
from extensions import db, login_manager, csrf


def create_app():
    app = Flask(__name__)
    app.config.from_object(Config)

    db.init_app(app)
    login_manager.init_app(app)
    csrf.init_app(app)

    login_manager.login_view = 'auth.login'
    login_manager.login_message = 'Пожалуйста, войдите для доступа к панели управления.'

    from routes.public import public_bp
    from routes.auth import auth_bp
    from routes.admin import admin_bp

    app.register_blueprint(public_bp)
    app.register_blueprint(auth_bp)
    app.register_blueprint(admin_bp)

    with app.app_context():
        from models import User, Survey, Question, Option, Response, Answer
        db.create_all()

        # Автоматическое создание администратора, если его нет
        if not User.query.filter_by(username='admin').first():
            admin = User(username='admin', role='admin')
            admin.set_password('admin123')  # замените на свой надёжный пароль
            db.session.add(admin)
            db.session.commit()
            print('Создан пользователь admin с паролем admin123')

    return app

if __name__ == '__main__':
    app = create_app()
    app.run(debug=True)