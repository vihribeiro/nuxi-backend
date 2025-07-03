import os
import sys
# DON'T CHANGE THIS !!!
sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))

from flask import Flask, send_from_directory
from flask_cors import CORS
from flask_jwt_extended import JWTManager
from src.models.user import db
from src.routes.user import user_bp
from src.routes.auth import auth_bp
from src.routes.client import client_bp
from src.routes.service import service_bp
from src.routes.professional import professional_bp
from src.routes.appointment import appointment_bp
from src.routes.waitlist import waitlist_bp
from src.routes.whatsapp import whatsapp_bp

# Importar todos os modelos para garantir que sejam criados
from src.models.client import Client
from src.models.service import Service
from src.models.professional import Professional
from src.models.work_schedule import WorkSchedule
from src.models.appointment import Appointment
from src.models.waitlist import Waitlist

app = Flask(__name__, static_folder=os.path.join(os.path.dirname(__file__), 'static'))
app.config['SECRET_KEY'] = 'asdf#FGSgvasgf$5$WGT'
app.config['JWT_SECRET_KEY'] = 'jwt-secret-string-change-this'

# Configurar CORS
CORS(app, origins="*")

# Configurar JWT
jwt = JWTManager(app)

# Registrar blueprints
app.register_blueprint(user_bp, url_prefix='/api/v1')
app.register_blueprint(auth_bp, url_prefix='/api/v1')
app.register_blueprint(client_bp, url_prefix='/api/v1')
app.register_blueprint(service_bp, url_prefix='/api/v1')
app.register_blueprint(professional_bp, url_prefix='/api/v1')
app.register_blueprint(appointment_bp, url_prefix='/api/v1')
app.register_blueprint(waitlist_bp, url_prefix='/api/v1')
app.register_blueprint(whatsapp_bp, url_prefix='/api/v1')

# Configurar banco de dados
app.config['SQLALCHEMY_DATABASE_URI'] = f"sqlite:///{os.path.join(os.path.dirname(__file__), 'database', 'app.db')}"
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
db.init_app(app)

with app.app_context():
    db.create_all()

@app.route('/', defaults={'path': ''})
@app.route('/<path:path>')
def serve(path):
    static_folder_path = app.static_folder
    if static_folder_path is None:
            return "Static folder not configured", 404

    if path != "" and os.path.exists(os.path.join(static_folder_path, path)):
        return send_from_directory(static_folder_path, path)
    else:
        index_path = os.path.join(static_folder_path, 'index.html')
        if os.path.exists(index_path):
            return send_from_directory(static_folder_path, 'index.html')
        else:
            return "index.html not found", 404

@app.route('/api/v1/health', methods=['GET'])
def health_check():
    return {'status': 'OK', 'message': 'Nuxi API está funcionando'}

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=True)
