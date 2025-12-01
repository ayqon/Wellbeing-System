from flask import Flask
from src.container import Container

def create_app(config_name="default"):
    app = Flask(__name__)
    app.secret_key = 'dev_secret_key' # Change in production
    
    # Initialize Container
    container = Container()
    
    # Store container in app config or extension for access in routes
    # For now, we'll attach it to the app instance for easy access in tests/views
    app.container = container
    
    # Register Blueprints (Placeholder for future tasks)
    from src.api.surveys import survey_bp
    app.register_blueprint(survey_bp, url_prefix='/api/surveys')
    from src.api.auth import auth_bp
    app.register_blueprint(auth_bp, url_prefix='/auth')
    
    from src.api.analytics import analytics_bp
    app.register_blueprint(analytics_bp, url_prefix='/analytics')
    
    from src.api.admin import admin_bp
    app.register_blueprint(admin_bp, url_prefix='/admin')
    
    # Initialize Flask-Login
    from flask_login import LoginManager
    login_manager = LoginManager()
    login_manager.login_view = 'auth.login'
    login_manager.init_app(app)
    
    @login_manager.user_loader
    def load_user(user_id):
        repo = container.user_repository()
        return repo.get_by_id(user_id)
    
    @app.route("/health")
    def health():
        return {"status": "ok"}
        
    return app

if __name__ == "__main__":
    app = create_app()
    app.run(debug=True)
