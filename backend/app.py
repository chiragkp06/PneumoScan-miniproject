from flask import Flask
from api.upload import upload_bp  # Correct import from api.upload
from api.results import results_bp  # Correct import from api.results

app = Flask(__name__)
app.register_blueprint(upload_bp, url_prefix='/api')
app.register_blueprint(results_bp, url_prefix='/api')

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=5000)
