from flask import request, jsonify
from models import Report
from extensions import db
from datetime import datetime

def send_report():
    try:
        data = request.get_json()
        gmail = data.get('gmail')
        subject = data.get('subject')
        description = data.get('description')

        if not gmail or not subject or not description:
            return jsonify({'error': 'Gmail, subject, and description are required'}), 400

        # Create a new report instance and add it to the database
        report = Report(
            gmail=gmail,
            subject=subject,
            description=description,
            status='pending',
            sent_at=datetime.utcnow()
        )

        db.session.add(report)
        db.session.commit()

        return jsonify({'message': 'Report submitted successfully'}), 201

    except Exception as e:
        return jsonify({'error': f'An error occurred: {str(e)}'}), 500
