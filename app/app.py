from flask import Flask, jsonify, render_template
import os
import logging

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = Flask(__name__, 
            template_folder='templates',
            static_folder='static')

# Health check endpoint
@app.route('/health', methods=['GET'])
def health():
    """Health check endpoint for monitoring"""
    return jsonify({
        "status": "healthy",
        "service": "cicd-python-app",
        "environment": os.getenv('FLASK_ENV', 'development')
    }), 200

@app.route('/', methods=['GET'])
def index():
    """Serve the HTML dashboard"""
    environment = os.getenv('FLASK_ENV', 'development')
    return render_template('index.html', environment=environment)

@app.route('/api/', methods=['GET'])
def api_hello():
    """Main API endpoint"""
    return jsonify({
        "message": "Hello from CI/CD Python App!",
        "version": "1.0.0",
        "environment": os.getenv('FLASK_ENV', 'development'),
        "status": "running"
    }), 200

@app.route('/info', methods=['GET'])
def info():
    """Application info endpoint"""
    return jsonify({
        "app_name": "cicd-python-app",
        "version": "1.0.0",
        "description": "CI/CD Pipeline Deployment Demo using Ansible, Jenkins, and Docker",
        "endpoints": {
            "/": "Main endpoint",
            "/health": "Health check",
            "/info": "Application info"
        }
    }), 200

@app.errorhandler(404)
def not_found(error):
    """Handle 404 errors"""
    return jsonify({"error": "Not found"}), 404

@app.errorhandler(500)
def internal_error(error):
    """Handle 500 errors"""
    logger.error(f"Internal server error: {error}")
    return jsonify({"error": "Internal server error"}), 500

if __name__ == '__main__':
    debug_mode = os.getenv('FLASK_ENV', 'development') == 'development'
    logger.info(f"Starting application in {os.getenv('FLASK_ENV', 'development')} mode")
    app.run(
        host='0.0.0.0',
        port=5000,
        debug=debug_mode,
        use_reloader=False
    )
