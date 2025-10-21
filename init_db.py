#!/usr/bin/env python3
"""
Initialize database with tables and sample data.
Run this script locally to set up your database.
"""

from backend import create_app
from backend.models import Hospital

def init_database():
    app = create_app()
    
    with app.app_context():
        # Create all tables
        from backend.extensions import db
        db.create_all()
        print("Database tables created successfully!")
        
        # Add sample hospitals if none exist
        if Hospital.query.count() == 0:
            sample_hospitals = [
                {
                    "name": "City General Hospital",
                    "address": "123 Main Street, Downtown",
                    "latitude": 18.5204,
                    "longitude": 73.8567,
                    "fee_details": "Consultation: $50, Emergency: $100",
                    "phone": "+1-555-0101"
                },
                {
                    "name": "Metro Medical Center",
                    "address": "456 Health Avenue, Midtown",
                    "latitude": 18.5304,
                    "longitude": 73.8667,
                    "fee_details": "Consultation: $60, Emergency: $120",
                    "phone": "+1-555-0102"
                },
                {
                    "name": "Sunrise Hospital",
                    "address": "789 Wellness Blvd, Uptown",
                    "latitude": 18.5404,
                    "longitude": 73.8767,
                    "fee_details": "Consultation: $45, Emergency: $90",
                    "phone": "+1-555-0103"
                },
                {
                    "name": "Green Valley Medical",
                    "address": "321 Care Street, Suburb",
                    "latitude": 18.5104,
                    "longitude": 73.8467,
                    "fee_details": "Consultation: $40, Emergency: $80",
                    "phone": "+1-555-0104"
                },
                {
                    "name": "Royal Healthcare",
                    "address": "654 Premium Road, Elite District",
                    "latitude": 18.5504,
                    "longitude": 73.8867,
                    "fee_details": "Consultation: $80, Emergency: $150",
                    "phone": "+1-555-0105"
                }
            ]
            
            for hospital_data in sample_hospitals:
                hospital = Hospital(**hospital_data)
                db.session.add(hospital)
            
            db.session.commit()
            print(f"Added {len(sample_hospitals)} sample hospitals!")
        else:
            print("Hospitals already exist in database.")

if __name__ == "__main__":
    init_database()