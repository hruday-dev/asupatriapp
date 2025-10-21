from flask import Blueprint, request, jsonify
from flask_jwt_extended import jwt_required, get_jwt_identity
from ..extensions import db
from ..models import User, Doctor, Hospital, HospitalAdmin, UserType

hospital_admin_bp = Blueprint("hospital_admin", __name__)


@hospital_admin_bp.post("/doctors")
@jwt_required()
def add_doctor():
    identity = get_jwt_identity() or {}
    user_id = identity.get("user_id")
    
    if not user_id:
        return {"message": "Invalid token"}, 401
    
    # Verify user is hospital admin
    user = User.query.get(user_id)
    if not user or user.user_type != UserType.HOSPITAL_ADMIN:
        return {"message": "Unauthorized - Hospital admin only"}, 403
    
    hospital_admin = HospitalAdmin.query.filter_by(user_id=user_id).first()
    if not hospital_admin:
        return {"message": "Hospital admin not found"}, 404
    
    data = request.get_json() or {}
    doctor_email = data.get("email")
    doctor_password = data.get("password")
    doctor_name = data.get("full_name")
    specialization = data.get("specialization")
    qualifications = data.get("qualifications")
    experience_years = data.get("experience_years")
    
    if not all([doctor_email, doctor_password, doctor_name, specialization]):
        return {"message": "Missing required fields"}, 400
    
    # Check if doctor email already exists
    if doctor_email and User.query.filter_by(email=doctor_email.strip().lower()).first():
        return {"message": "Email already registered"}, 409
    
    try:
        # Create doctor user
        from passlib.hash import pbkdf2_sha256
        doctor_user = User()
        doctor_user.email = doctor_email.strip().lower() if doctor_email else ""
        doctor_user.password_hash = pbkdf2_sha256.hash(str(doctor_password))
        doctor_user.user_type = UserType.DOCTOR
        doctor_user.full_name = doctor_name
        db.session.add(doctor_user)
        db.session.flush()
        
        # Create doctor record
        doctor = Doctor()
        doctor.user_id = doctor_user.user_id
        doctor.hospital_id = hospital_admin.hospital_id
        doctor.specialization = specialization
        doctor.qualifications = qualifications
        doctor.experience_years = experience_years
        doctor.is_available = True
        db.session.add(doctor)
        
        db.session.commit()
        
        return {
            "message": "Doctor added successfully",
            "doctor": {
                "doctor_id": doctor.doctor_id,
                "user_id": doctor.user_id,
                "email": doctor_user.email,
                "full_name": doctor_user.full_name,
                "specialization": doctor.specialization,
                "qualifications": doctor.qualifications,
                "experience_years": doctor.experience_years
            }
        }, 201
        
    except Exception as e:
        db.session.rollback()
        return {"message": f"Error adding doctor: {str(e)}"}, 500


@hospital_admin_bp.get("/doctors")
@jwt_required()
def get_doctors():
    identity = get_jwt_identity() or {}
    user_id = identity.get("user_id")
    
    if not user_id:
        return {"message": "Invalid token"}, 401
    
    # Verify user is hospital admin
    user = User.query.get(user_id)
    if not user or user.user_type != UserType.HOSPITAL_ADMIN:
        return {"message": "Unauthorized - Hospital admin only"}, 403
    
    hospital_admin = HospitalAdmin.query.filter_by(user_id=user_id).first()
    if not hospital_admin:
        return {"message": "Hospital admin not found"}, 404
    
    doctors = Doctor.query.filter_by(hospital_id=hospital_admin.hospital_id).all()
    
    return {
        "doctors": [
            {
                "doctor_id": d.doctor_id,
                "user_id": d.user_id,
                "email": d.user.email,
                "full_name": d.user.full_name,
                "specialization": d.specialization,
                "qualifications": d.qualifications,
                "experience_years": d.experience_years,
                "is_available": d.is_available
            } for d in doctors
        ]
    }


@hospital_admin_bp.put("/doctors/<int:doctor_id>")
@jwt_required()
def update_doctor(doctor_id):
    identity = get_jwt_identity() or {}
    user_id = identity.get("user_id")
    
    if not user_id:
        return {"message": "Invalid token"}, 401
    
    # Verify user is hospital admin
    user = User.query.get(user_id)
    if not user or user.user_type != UserType.HOSPITAL_ADMIN:
        return {"message": "Unauthorized - Hospital admin only"}, 403
    
    hospital_admin = HospitalAdmin.query.filter_by(user_id=user_id).first()
    if not hospital_admin:
        return {"message": "Hospital admin not found"}, 404
    
    doctor = Doctor.query.filter_by(doctor_id=doctor_id, hospital_id=hospital_admin.hospital_id).first()
    if not doctor:
        return {"message": "Doctor not found"}, 404
    
    data = request.get_json() or {}
    
    # Update doctor fields
    if "specialization" in data:
        doctor.specialization = data["specialization"]
    if "qualifications" in data:
        doctor.qualifications = data["qualifications"]
    if "experience_years" in data:
        doctor.experience_years = data["experience_years"]
    if "is_available" in data:
        doctor.is_available = data["is_available"]
    
    try:
        db.session.commit()
        return {"message": "Doctor updated successfully"}
    except Exception as e:
        db.session.rollback()
        return {"message": f"Error updating doctor: {str(e)}"}, 500


@hospital_admin_bp.delete("/doctors/<int:doctor_id>")
@jwt_required()
def delete_doctor(doctor_id):
    identity = get_jwt_identity() or {}
    user_id = identity.get("user_id")
    
    if not user_id:
        return {"message": "Invalid token"}, 401
    
    # Verify user is hospital admin
    user = User.query.get(user_id)
    if not user or user.user_type != UserType.HOSPITAL_ADMIN:
        return {"message": "Unauthorized - Hospital admin only"}, 403
    
    hospital_admin = HospitalAdmin.query.filter_by(user_id=user_id).first()
    if not hospital_admin:
        return {"message": "Hospital admin not found"}, 404
    
    doctor = Doctor.query.filter_by(doctor_id=doctor_id, hospital_id=hospital_admin.hospital_id).first()
    if not doctor:
        return {"message": "Doctor not found"}, 404
    
    try:
        # Also delete the associated user
        user_to_delete = User.query.get(doctor.user_id)
        db.session.delete(doctor)
        if user_to_delete:
            db.session.delete(user_to_delete)
        db.session.commit()
        return {"message": "Doctor deleted successfully"}
    except Exception as e:
        db.session.rollback()
        return {"message": f"Error deleting doctor: {str(e)}"}, 500


@hospital_admin_bp.put("/first-login-complete")
@jwt_required()
def complete_first_login():
    identity = get_jwt_identity() or {}
    user_id = identity.get("user_id")
    
    if not user_id:
        return {"message": "Invalid token"}, 401
    
    hospital_admin = HospitalAdmin.query.filter_by(user_id=user_id).first()
    if not hospital_admin:
        return {"message": "Hospital admin not found"}, 404
    
    hospital_admin.is_first_login = False
    try:
        db.session.commit()
        return {"message": "First login setup completed"}
    except Exception as e:
        db.session.rollback()
        return {"message": f"Error completing setup: {str(e)}"}, 500