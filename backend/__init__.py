from flask import Flask
from .config import Config
from .extensions import db, jwt, cors


def create_app() -> Flask:
    app = Flask(__name__)
    app.config.from_object(Config)

    cors.init_app(app, resources={r"/api/*": {"origins": "*"}})
    db.init_app(app)
    jwt.init_app(app)

    from .routes.auth import auth_bp
    from .routes.hospitals import hospitals_bp
    from .routes.appointments import appointments_bp

    app.register_blueprint(auth_bp, url_prefix="/api")
    app.register_blueprint(hospitals_bp, url_prefix="/api")
    app.register_blueprint(appointments_bp, url_prefix="/api")
    
    # Register hospital admin routes
    # from .routes.hospital_admin import hospital_admin_bp
    # app.register_blueprint(hospital_admin_bp, url_prefix="/api")

    with app.app_context():
        db.create_all()
        # Add sample hospitals if none exist
        from .models import Hospital
        if Hospital.query.count() == 0:
            sample_hospitals = [
                Hospital()
            ]
            
            # Create first hospital
            hospital1 = Hospital()
            hospital1.name = "City General Hospital"
            hospital1.address = "123 Main Street, Downtown"
            hospital1.latitude = 18.5204
            hospital1.longitude = 73.8567
            hospital1.fee_details = "Consultation: $50, Emergency: $100"
            hospital1.phone = "+1-555-0101"
            sample_hospitals.append(hospital1)
            
            # Create second hospital
            hospital2 = Hospital()
            hospital2.name = "Metro Medical Center"
            hospital2.address = "456 Health Avenue, Midtown"
            hospital2.latitude = 18.5304
            hospital2.longitude = 73.8667
            hospital2.fee_details = "Consultation: $60, Emergency: $120"
            hospital2.phone = "+1-555-0102"
            sample_hospitals.append(hospital2)
            
            # Create third hospital
            hospital3 = Hospital()
            hospital3.name = "Sunrise Hospital"
            hospital3.address = "789 Wellness Blvd, Uptown"
            hospital3.latitude = 18.5404
            hospital3.longitude = 73.8767
            hospital3.fee_details = "Consultation: $45, Emergency: $90"
            hospital3.phone = "+1-555-0103"
            sample_hospitals.append(hospital3)
            
            # Create fourth hospital
            hospital4 = Hospital()
            hospital4.name = "Green Valley Medical"
            hospital4.address = "321 Care Street, Suburb"
            hospital4.latitude = 18.5104
            hospital4.longitude = 73.8467
            hospital4.fee_details = "Consultation: $40, Emergency: $80"
            hospital4.phone = "+1-555-0104"
            sample_hospitals.append(hospital4)
            
            # Create fifth hospital
            hospital5 = Hospital()
            hospital5.name = "Royal Healthcare"
            hospital5.address = "654 Premium Road, Elite District"
            hospital5.latitude = 18.5504
            hospital5.longitude = 73.8867
            hospital5.fee_details = "Consultation: $80, Emergency: $150"
            hospital5.phone = "+1-555-0105"
            sample_hospitals.append(hospital5)
            for hospital in sample_hospitals:
                db.session.add(hospital)
            db.session.commit()

    @app.get("/health")
    def health_check():
        return {"status": "ok"}

    return app
