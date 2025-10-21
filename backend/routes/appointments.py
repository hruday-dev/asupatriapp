from datetime import datetime, date, time as time_cls
from flask import Blueprint, request
from flask_jwt_extended import jwt_required, get_jwt_identity
from ..extensions import db
from ..models import Appointment, AppointmentStatus, Doctor, DoctorSchedule

appointments_bp = Blueprint("appointments", __name__)


def is_slot_available(doctor_id: int, when_date: date, when_time: time_cls) -> bool:
    # Check schedule
    schedules = DoctorSchedule.query.filter_by(doctor_id=doctor_id, day_of_week=when_date.weekday()).all()
    within_schedule = any(s.start_time <= when_time < s.end_time for s in schedules)
    if not within_schedule:
        return False
    # Check conflicting appointment
    conflict = Appointment.query.filter_by(doctor_id=doctor_id, date=when_date, time=when_time).first()
    return conflict is None


@appointments_bp.post("/appointments")
@jwt_required()
def create_appointment():
    data = request.get_json() or {}
    identity = get_jwt_identity() or {}
    patient_id = identity.get("user_id")

    doctor_id = data.get("doctor_id")
    hospital_id = data.get("hospital_id")
    date_str = data.get("date")  # YYYY-MM-DD
    time_str = data.get("time")  # HH:MM
    reason = data.get("reason")

    if not all([patient_id, doctor_id, hospital_id, date_str, time_str]):
        return {"message": "Missing fields"}, 400

    try:
        when_date = datetime.strptime(date_str, "%Y-%m-%d").date()
        when_time = datetime.strptime(time_str, "%H:%M").time()
    except ValueError:
        return {"message": "Invalid date/time format"}, 400

    if not is_slot_available(doctor_id, when_date, when_time):
        return {"message": "Selected slot is not available"}, 409

    appt = Appointment(
        patient_id=patient_id,
        doctor_id=doctor_id,
        hospital_id=hospital_id,
        date=when_date,
        time=when_time,
        reason=reason,
        status=AppointmentStatus.SCHEDULED,
    )
    db.session.add(appt)
    db.session.commit()

    return {"appointment_id": appt.appointment_id}, 201


@appointments_bp.get("/appointments/<int:user_id>")
@jwt_required()
def list_user_appointments(user_id: int):
    identity = get_jwt_identity() or {}
    if user_id != identity.get("user_id"):
        return {"message": "Forbidden"}, 403

    # Check if we should filter by today's date
    filter_today = request.args.get('today', 'false').lower() == 'true'
    today_date = date.today() if filter_today else None

    # For doctors, show their appointments; for patients, their own
    # We don't have direct relation from user->doctor_id, so let client pass role via token
    role = (identity.get("user_type") or "").lower()
    if role == "doctor":
        # find doctor id by user id
        doctor = Doctor.query.filter_by(user_id=user_id).first()
        doctor_id = doctor.doctor_id if doctor else None
        q = Appointment.query.filter_by(doctor_id=doctor_id)
    else:
        q = Appointment.query.filter_by(patient_id=user_id)

    # Filter by today's date if requested
    if filter_today and today_date:
        q = q.filter(Appointment.date == today_date)

    appts = q.order_by(Appointment.date.asc(), Appointment.time.asc()).all()
    return {"appointments": [
        {
            "appointment_id": a.appointment_id,
            "patient_id": a.patient_id,
            "doctor_id": a.doctor_id,
            "hospital_id": a.hospital_id,
            "date": a.date.isoformat(),
            "time": a.time.strftime("%H:%M"),
            "reason": a.reason,
            "status": a.status.value,
        } for a in appts
    ]}


@appointments_bp.put("/appointments/<int:appointment_id>")
@jwt_required()
def update_appointment_status(appointment_id: int):
    identity = get_jwt_identity() or {}
    role = (identity.get("user_type") or "").lower()
    if role != "doctor" and role != "admin":
        return {"message": "Only doctors/admins can update appointments"}, 403

    data = request.get_json() or {}
    new_status = data.get("status")
    if new_status not in {s.value for s in AppointmentStatus}:
        return {"message": "Invalid status"}, 400

    appt = Appointment.query.get_or_404(appointment_id)
    appt.status = AppointmentStatus(new_status)
    db.session.commit()
    return {"message": "Updated"}
