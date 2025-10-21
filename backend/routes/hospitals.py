from math import radians, cos, sin, asin, sqrt
from flask import Blueprint, request
from ..extensions import db
from ..models import Hospital, Doctor

hospitals_bp = Blueprint("hospitals", __name__)


def haversine(lat1, lon1, lat2, lon2):
    if None in (lat1, lon1, lat2, lon2):
        return float("inf")
    # convert decimal degrees to radians
    lon1, lat1, lon2, lat2 = map(radians, [lon1, lat1, lon2, lat2])
    # haversine formula
    dlon = lon2 - lon1
    dlat = lat2 - lat1
    a = sin(dlat/2)**2 + cos(lat1) * cos(lat2) * sin(dlon/2)**2
    c = 2 * asin(sqrt(a))
    km = 6371 * c
    return km


@hospitals_bp.get("/hospitals")
def list_hospitals():
    hospitals = Hospital.query.all()
    return {"hospitals": [
        {
            "hospital_id": h.hospital_id,
            "name": h.name,
            "address": h.address,
            "latitude": h.latitude,
            "longitude": h.longitude,
            "fee_details": h.fee_details,
            "phone": h.phone,
        } for h in hospitals
    ]}


@hospitals_bp.get("/hospitals/nearby")
def nearby_hospitals():
    try:
        lat = float(request.args.get("lat"))
        lon = float(request.args.get("lon"))
    except (TypeError, ValueError):
        return {"message": "lat and lon query params required"}, 400

    hospitals = Hospital.query.all()
    enriched = []
    for h in hospitals:
        distance_km = haversine(lat, lon, h.latitude, h.longitude)
        enriched.append((distance_km, h))
    enriched.sort(key=lambda x: x[0])

    return {"hospitals": [
        {
            "hospital_id": h.hospital_id,
            "name": h.name,
            "address": h.address,
            "latitude": h.latitude,
            "longitude": h.longitude,
            "fee_details": h.fee_details,
            "phone": h.phone,
            "distance_km": round(dist, 2) if dist != float("inf") else None,
        }
        for dist, h in enriched
    ]}


@hospitals_bp.get("/doctors/hospital/<int:hospital_id>")
def doctors_by_hospital(hospital_id: int):
    doctors = Doctor.query.filter_by(hospital_id=hospital_id).all()
    return {"doctors": [
        {
            "doctor_id": d.doctor_id,
            "user_id": d.user_id,
            "hospital_id": d.hospital_id,
            "specialization": d.specialization,
            "qualifications": d.qualifications,
            "is_available": d.is_available,
        } for d in doctors
    ]}
