from functools import wraps
from flask import Blueprint, request, jsonify
import jwt
import os
from datetime import datetime, timedelta
from werkzeug.security import generate_password_hash, check_password_hash
import boto3

auth_bp = Blueprint('auth', __name__)

SECRET_KEY = os.getenv('SECRET_KEY', 'your-secret-key')

rds_client = boto3.client(
    'rds-data',
    aws_access_key_id=os.getenv('AWS_ACCESS_KEY_ID'),
    aws_secret_access_key=os.getenv('AWS_SECRET_ACCESS_KEY'),
    region_name=os.getenv('AWS_REGION', 'ap-south-1')
)

DATABASE_NAME = os.getenv('AWS_RDS_DATABASE_NAME')
DB_CLUSTER_ARN = os.getenv('AWS_RDS_CLUSTER_ARN')
SECRET_ARN = os.getenv('AWS_RDS_SECRET_ARN')

def token_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        token = None
        if 'Authorization' in request.headers:
            token = request.headers['Authorization'].split(" ")[1]

        if not token:
            return jsonify({'message': 'Token is missing!'}), 403

        try:
            data = jwt.decode(token, SECRET_KEY, algorithms=["HS256"])
        except Exception as e:
            return jsonify({'message': 'Token is invalid or expired!'}), 403

        return f(data['user'], *args, **kwargs)
    return decorated_function

@auth_bp.route('/signup', methods=['POST'])
def signup():
    if not request.json:
        return jsonify({"error": "Invalid input, JSON expected"}), 400

    username = request.json.get('username')
    password = request.json.get('password')

    if not username or not password:
        return jsonify({"error": "Username and password are required"}), 400

    hashed_password = generate_password_hash(password, method='bcrypt')
    try:
        query = """
        INSERT INTO users (username, password)
        VALUES (:username, :password)
        """
        parameters = [
            {'name': 'username', 'value': {'stringValue': username}},
            {'name': 'password', 'value': {'stringValue': hashed_password}}
        ]
        rds_client.execute_statement(
            resourceArn=DB_CLUSTER_ARN,
            secretArn=SECRET_ARN,
            database=DATABASE_NAME,
            sql=query,
            parameters=parameters
        )
        return jsonify({"message": "User signed up successfully"}), 201
    except Exception as e:
        return jsonify({"error": f"Failed to sign up: {str(e)}"}), 500

@auth_bp.route('/login', methods=['POST'])
def login():
    if not request.json:
        return jsonify({"error": "Invalid input, JSON expected"}), 400

    username = request.json.get('username')
    password = request.json.get('password')

    if not username or not password:
        return jsonify({'message': 'Invalid credentials'}), 401

    try:
        query = "SELECT password FROM users WHERE username = :username"
        parameters = [{'name': 'username', 'value': {'stringValue': username}}]
        response = rds_client.execute_statement(
            resourceArn=DB_CLUSTER_ARN,
            secretArn=SECRET_ARN,
            database=DATABASE_NAME,
            sql=query,
            parameters=parameters
        )
        if not response['records']:
            return jsonify({'message': 'Invalid credentials'}), 401

        hashed_password = response['records'][0][0]['stringValue']
        if not check_password_hash(hashed_password, password):
            return jsonify({'message': 'Invalid credentials'}), 401

        token = jwt.encode({'user': username, 'exp': datetime.utcnow() + timedelta(hours=1)}, SECRET_KEY, algorithm='HS256')
        return jsonify({'token': token})
    except Exception as e:
        return jsonify({"error": f"Failed to login: {str(e)}"}), 500
