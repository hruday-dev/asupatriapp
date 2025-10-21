from flask import Blueprint, request
from flask_jwt_extended import create_access_token, jwt_required, get_jwt_identity
from passlib.hash import pbkdf2_sha256
from ..extensions import db
from ..models import User, UserType

auth_bp = Blueprint("auth", __name__)


@auth_bp.post("/register")
def register():
    data = request.get_json() or {}
    email = (data.get("email") or "").strip().lower()
    password = data.get("password")
    user_type = data.get("user_type")
    full_name = data.get("full_name")
    hospital_id = data.get("hospital_id")

    if not email or not password or user_type not in {t.value for t in UserType}:
        return {"message": "Invalid payload"}, 400

    if User.query.filter_by(email=email).first():
        return {"message": "Email already registered"}, 409

    password_hash = pbkdf2_sha256.hash(password)
    user = User()
    user.email = email
    user.password_hash = password_hash
    user.user_type = UserType(user_type)
    user.full_name = full_name
    db.session.add(user)
    db.session.flush()  # Get user_id without committing

    # Create hospital admin record if user_type is Hospital Admin
    if user_type == UserType.HOSPITAL_ADMIN.value and hospital_id:
        from ..models import HospitalAdmin
        hospital_admin = HospitalAdmin()
        hospital_admin.user_id = user.user_id
        hospital_admin.hospital_id = hospital_id
        db.session.add(hospital_admin)

    db.session.commit()

    token = create_access_token(identity={"user_id": user.user_id, "user_type": user.user_type.value})
    return {"access_token": token, "user": {"user_id": user.user_id, "email": user.email, "user_type": user.user_type.value}}, 201


@auth_bp.post("/login")
def login():
    data = request.get_json() or {}
    email = (data.get("email") or "").strip().lower()
    password = data.get("password") or ""

    user = User.query.filter_by(email=email).first()
    if not user or not pbkdf2_sha256.verify(password, user.password_hash):
        return {"message": "Invalid email or password"}, 401

    token = create_access_token(identity={"user_id": user.user_id, "user_type": user.user_type.value})
    return {"access_token": token, "user": {"user_id": user.user_id, "email": user.email, "user_type": user.user_type.value}}


@auth_bp.get("/profile")
@jwt_required()
def get_profile():
    identity = get_jwt_identity() or {}
    user_id = identity.get("user_id")
    
    if not user_id:
        return {"message": "Invalid token"}, 401
    
    user = User.query.get(user_id)
    if not user:
        return {"message": "User not found"}, 404
    
    # Get additional info based on user type
    profile_data = {
        "user_id": user.user_id,
        "email": user.email,
        "full_name": user.full_name,
        "user_type": user.user_type.value,
        "created_at": user.user_id  # We'll use user_id as a proxy for creation time
    }
    
    # If it's a doctor, get doctor-specific info
    if user.user_type == UserType.DOCTOR:
        from ..models import Doctor, Hospital
        doctor = Doctor.query.filter_by(user_id=user_id).first()
        if doctor:
            hospital = Hospital.query.get(doctor.hospital_id)
            profile_data.update({
                "specialization": doctor.specialization,
                "qualifications": doctor.qualifications,
                "experience_years": doctor.experience_years,
                "is_available": doctor.is_available,
                "hospital_name": hospital.name if hospital else None,
                "hospital_address": hospital.address if hospital else None
            })
    
    # If it's a hospital admin, get hospital-specific info
    elif user.user_type == UserType.HOSPITAL_ADMIN:
        from ..models import HospitalAdmin, Hospital
        hospital_admin = HospitalAdmin.query.filter_by(user_id=user_id).first()
        if hospital_admin:
            hospital = Hospital.query.get(hospital_admin.hospital_id)
            profile_data.update({
                "hospital_id": hospital_admin.hospital_id,
                "hospital_name": hospital.name if hospital else None,
                "hospital_address": hospital.address if hospital else None,
                "is_first_login": hospital_admin.is_first_login
            })
    
    return profile_data
