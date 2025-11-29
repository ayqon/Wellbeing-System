from flask import Flask
from src.container import Container

def create_app(config_name="default"):
    app = Flask(__name__)
    
    # Initialize Container
    container = Container()
    
    # Store container in app config or extension for access in routes
    # For now, we'll attach it to the app instance for easy access in tests/views
    app.container = container
    
    # Register Blueprints (Placeholder for future tasks)
    from src.api.surveys import survey_bp
    app.register_blueprint(survey_bp, url_prefix='/api/surveys')
    # from src.api.auth import auth_bp
    # app.register_blueprint(auth_bp)
    
    @app.route("/health")
    def health():
        return {"status": "ok"}
        
    return app

if __name__ == "__main__":
    app = create_app()
    app.run(debug=True)
