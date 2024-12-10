from flask import Flask, request, g
from .config import Config
from .routes import bp
from .models import db
import time

def create_app():
    app = Flask(__name__)
    app.config.from_object(Config)
    
    # DB 초기화
    db.init_app(app)
    
    with app.app_context():
        db.create_all()
    
    @app.before_request
    def before_request():
        g.start_time = time.time()

    @app.after_request
    def after_request(response):
        diff = time.time() - g.start_time
        app.logger.info(f"Request to {request.path} took {diff:.2f} seconds")
        return response
    
    app.register_blueprint(bp)
    return app