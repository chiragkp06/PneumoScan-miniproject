from flask import Blueprint, request, jsonify
import boto3
import os
from .auth import token_required
from fpdf import FPDF

results_bp = Blueprint('results', __name__)

# Connect to RDS
rds_client = boto3.client(
    'rds-data',
    aws_access_key_id=os.getenv('AWS_ACCESS_KEY_ID'),
    aws_secret_access_key=os.getenv('AWS_SECRET_ACCESS_KEY'),
    region_name=os.getenv('AWS_REGION', 'ap-south-1')
)

DATABASE_NAME = os.getenv('AWS_RDS_DATABASE_NAME')
DB_CLUSTER_ARN = os.getenv('AWS_RDS_CLUSTER_ARN')
SECRET_ARN = os.getenv('AWS_RDS_SECRET_ARN')

@results_bp.route('/', methods=['POST'])
@token_required
def store_result(user):
    if not request.json:
        return jsonify({"error": "Invalid input, JSON expected"}), 400

    data = request.json
    required_fields = ['image_url', 'confidence', 'diagnosis']
    if not all(field in data for field in required_fields):
        return jsonify({"error": f"Missing required fields: {required_fields}"}), 400

    try:
        # Store the result in AWS RDS
        query = """
        INSERT INTO results (image_url, confidence, diagnosis, created_by)
        VALUES (:image_url, :confidence, :diagnosis, :created_by)
        """
        parameters = [
            {'name': 'image_url', 'value': {'stringValue': data['image_url']}},
            {'name': 'confidence', 'value': {'doubleValue': data['confidence']}},
            {'name': 'diagnosis', 'value': {'stringValue': data['diagnosis']}},
            {'name': 'created_by', 'value': {'stringValue': user}}
        ]
        rds_client.execute_statement(
            resourceArn=DB_CLUSTER_ARN,
            secretArn=SECRET_ARN,
            database=DATABASE_NAME,
            sql=query,
            parameters=parameters
        )
        return jsonify({'message': 'Result stored successfully'}), 201
    except Exception as e:
        return jsonify({"error": f"Failed to store result: {str(e)}"}), 500


@results_bp.route('/<int:id>', methods=['GET'])
@token_required
def fetch_result(user, id):
    try:
        # Fetch the result from AWS RDS
        query = "SELECT * FROM results WHERE id = :id AND created_by = :created_by"
        parameters = [
            {'name': 'id', 'value': {'longValue': id}},
            {'name': 'created_by', 'value': {'stringValue': user}}
        ]

        response = rds_client.execute_statement(
            resourceArn=DB_CLUSTER_ARN,
            secretArn=SECRET_ARN,
            database=DATABASE_NAME,
            sql=query,
            parameters=parameters
        )

        if not response['records']:
            return jsonify({"message": "Result not found"}), 404

        record = response['records'][0]
        return jsonify({
            "id": record[0]['longValue'],
            "image_url": record[1]['stringValue'],
            "confidence": record[2]['doubleValue'],
            "diagnosis": record[3]['stringValue'],
            "created_by": record[4]['stringValue']
        })
    except Exception as e:
        return jsonify({"error": f"Failed to fetch result: {str(e)}"}), 500


@results_bp.route('/report/<int:id>', methods=['GET'])
@token_required
def generate_report(user, id):
    try:
        # Fetch the result from AWS RDS
        query = "SELECT * FROM results WHERE id = :id AND created_by = :created_by"
        parameters = [
            {'name': 'id', 'value': {'longValue': id}},
            {'name': 'created_by', 'value': {'stringValue': user}}
        ]

        response = rds_client.execute_statement(
            resourceArn=DB_CLUSTER_ARN,
            secretArn=SECRET_ARN,
            database=DATABASE_NAME,
            sql=query,
            parameters=parameters
        )

        if not response['records']:
            return jsonify({"message": "Result not found"}), 404

        result = response['records'][0]
        pdf = FPDF()
        pdf.add_page()
        pdf.set_font("Arial", size=12)
        pdf.cell(200, 10, txt="Pneumoscan Report", ln=True, align='C')
        pdf.cell(200, 10, txt=f"Image URL: {result[1]['stringValue']}", ln=True)
        pdf.cell(200, 10, txt=f"Confidence: {result[2]['doubleValue']}%", ln=True)
        pdf.cell(200, 10, txt=f"Diagnosis: {result[3]['stringValue']}", ln=True)

        file_name = f"report_{result[0]['longValue']}.pdf"
        pdf.output(file_name)
        return jsonify({"message": f"Report {file_name} generated successfully!"})
    except Exception as e:
        return jsonify({"error": f"Failed to generate report: {str(e)}"}), 500
