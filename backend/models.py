from datetime import time, datetime
from enum import Enum
from typing import Optional
from sqlalchemy import Enum as SqlEnum
from .extensions import db


class UserType(str, Enum):
    PATIENT = "Patient"
    DOCTOR = "Doctor"
    HOSPITAL_ADMIN = "Hospital Admin"


class User(db.Model):
    __tablename__ = "users"
    user_id = db.Column(db.Integer, primary_key=True)
    email = db.Column(db.String(255), unique=True, nullable=False)
    password_hash = db.Column(db.String(255), nullable=False)
    user_type = db.Column(SqlEnum(UserType), nullable=False)
    full_name = db.Column(db.String(255), nullable=True)

    doctor = db.relationship("Doctor", back_populates="user", uselist=False)
    hospital_admin = db.relationship("HospitalAdmin", back_populates="user", uselist=False)


class Hospital(db.Model):
    __tablename__ = "hospitals"
    hospital_id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(255), nullable=False)
    address = db.Column(db.String(500), nullable=False)
    latitude = db.Column(db.Float, nullable=True)
    longitude = db.Column(db.Float, nullable=True)
    fee_details = db.Column(db.String(255), nullable=True)
    phone = db.Column(db.String(50), nullable=True)

    doctors = db.relationship("Doctor", back_populates="hospital", cascade="all, delete-orphan")
    admin = db.relationship("HospitalAdmin", back_populates="hospital", uselist=False)


class HospitalAdmin(db.Model):
    __tablename__ = "hospital_admins"
    admin_id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey("users.user_id"), nullable=False)
    hospital_id = db.Column(db.Integer, db.ForeignKey("hospitals.hospital_id"), nullable=False)
    is_first_login = db.Column(db.Boolean, default=True)

    user = db.relationship("User", back_populates="hospital_admin")
    hospital = db.relationship("Hospital", back_populates="admin")


class Doctor(db.Model):
    __tablename__ = "doctors"
    doctor_id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey("users.user_id"), nullable=False)
    hospital_id = db.Column(db.Integer, db.ForeignKey("hospitals.hospital_id"), nullable=False)
    specialization = db.Column(db.String(255), nullable=False)
    qualifications = db.Column(db.String(255), nullable=True)
    experience_years = db.Column(db.Integer, nullable=True)
    is_available = db.Column(db.Boolean, default=True)

    user = db.relationship("User", back_populates="doctor")
    hospital = db.relationship("Hospital", back_populates="doctors")
    schedules = db.relationship("DoctorSchedule", back_populates="doctor", cascade="all, delete-orphan")
    appointments = db.relationship("Appointment", back_populates="doctor", cascade="all, delete-orphan")


class DoctorSchedule(db.Model):
    __tablename__ = "doctor_schedules"
    schedule_id = db.Column(db.Integer, primary_key=True)
    doctor_id = db.Column(db.Integer, db.ForeignKey("doctors.doctor_id"), nullable=False)
    day_of_week = db.Column(db.Integer, nullable=False)  # 0=Mon .. 6=Sun
    start_time = db.Column(db.Time, nullable=False)
    end_time = db.Column(db.Time, nullable=False)

    doctor = db.relationship("Doctor", back_populates="schedules")


class AppointmentStatus(str, Enum):
    SCHEDULED = "Scheduled"
    CONFIRMED = "Confirmed"
    CANCELLED = "Cancelled"
    COMPLETED = "Completed"


class Appointment(db.Model):
    __tablename__ = "appointments"
    appointment_id = db.Column(db.Integer, primary_key=True)
    patient_id = db.Column(db.Integer, db.ForeignKey("users.user_id"), nullable=False)
    doctor_id = db.Column(db.Integer, db.ForeignKey("doctors.doctor_id"), nullable=False)
    hospital_id = db.Column(db.Integer, db.ForeignKey("hospitals.hospital_id"), nullable=False)
    date = db.Column(db.Date, nullable=False)
    time = db.Column(db.Time, nullable=False)
    reason = db.Column(db.String(500), nullable=True)
    status = db.Column(SqlEnum(AppointmentStatus), default=AppointmentStatus.SCHEDULED, nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow, nullable=False)

    doctor = db.relationship("Doctor", back_populates="appointments")
