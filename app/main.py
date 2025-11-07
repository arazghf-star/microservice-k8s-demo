"""
Main Flask Application
Production-ready microservice with health checks and API endpoints
"""
from flask import Flask, jsonify, request
from datetime import datetime
import logging
import os
import time

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# Application initialization
app = Flask(__name__)
app.config['JSON_SORT_KEYS'] = False

# Application metadata
APP_NAME = os.getenv('APP_NAME', 'microservice')
VERSION = '1.0.0'
START_TIME = datetime.now()


@app.route('/')
def root():
    """Root endpoint"""
    return jsonify({
        'service': APP_NAME,
        'version': VERSION,
        'status': 'running',
        'endpoints': {
            'health': '/health',
            'health_live': '/health/live',
            'health_ready': '/health/ready',
            'api_v1': '/api/v1/*'
        }
    })


@app.route('/health')
def health():
    """Basic health check endpoint"""
    return jsonify({
        'status': 'healthy',
        'service': APP_NAME,
        'version': VERSION,
        'timestamp': datetime.now().isoformat()
    }), 200


@app.route('/health/live')
def health_live():
    """Kubernetes liveness probe endpoint"""
    return jsonify({'status': 'alive'}), 200


@app.route('/health/ready')
def health_ready():
    """Kubernetes readiness probe endpoint"""
    # In production, check database connections, cache, etc.
    return jsonify({'status': 'ready'}), 200


@app.route('/health/startup')
def health_startup():
    """Kubernetes startup probe endpoint"""
    uptime = (datetime.now() - START_TIME).total_seconds()
    return jsonify({
        'status': 'started',
        'uptime_seconds': uptime
    }), 200


@app.route('/api/v1/hello', methods=['GET'])
def api_hello():
    """Hello endpoint"""
    name = request.args.get('name', 'World')
    logger.info(f"Hello endpoint called with name: {name}")
    
    return jsonify({
        'message': f'Hello, {name}!',
        'service': APP_NAME,
        'version': VERSION,
        'timestamp': datetime.now().isoformat()
    }), 200


@app.route('/api/v1/status', methods=['GET'])
def api_status():
    """Service status endpoint"""
    uptime = (datetime.now() - START_TIME).total_seconds()
    
    return jsonify({
        'service': APP_NAME,
        'version': VERSION,
        'status': 'running',
        'uptime_seconds': round(uptime, 2),
        'uptime_formatted': format_uptime(uptime),
        'environment': os.getenv('ENVIRONMENT', 'development'),
        'timestamp': datetime.now().isoformat()
    }), 200


@app.route('/api/v1/echo', methods=['POST'])
def api_echo():
    """Echo endpoint - returns what was sent"""
    data = request.get_json()
    
    if not data:
        return jsonify({
            'error': 'No JSON data provided'
        }), 400
    
    logger.info(f"Echo endpoint called with data: {data}")
    
    return jsonify({
        'received': data,
        'timestamp': datetime.now().isoformat()
    }), 200


@app.errorhandler(404)
def not_found(error):
    """Handle 404 errors"""
    return jsonify({
        'error': 'Not Found',
        'message': 'The requested endpoint does not exist',
        'status': 404
    }), 404


@app.errorhandler(500)
def internal_error(error):
    """Handle 500 errors"""
    logger.error(f"Internal server error: {error}")
    return jsonify({
        'error': 'Internal Server Error',
        'message': 'An unexpected error occurred',
        'status': 500
    }), 500


def format_uptime(seconds):
    """Format uptime in human-readable format"""
    days = int(seconds // 86400)
    hours = int((seconds % 86400) // 3600)
    minutes = int((seconds % 3600) // 60)
    secs = int(seconds % 60)
    
    parts = []
    if days > 0:
        parts.append(f"{days}d")
    if hours > 0:
        parts.append(f"{hours}h")
    if minutes > 0:
        parts.append(f"{minutes}m")
    if secs > 0 or not parts:
        parts.append(f"{secs}s")
    
    return " ".join(parts)


if __name__ == '__main__':
    port = int(os.getenv('PORT', 8080))
    debug = os.getenv('DEBUG', 'False').lower() == 'true'
    
    logger.info(f"Starting {APP_NAME} v{VERSION} on port {port}")
    app.run(host='0.0.0.0', port=port, debug=debug)
