"""
config_data.py
--------------
Ground-truth civic data for the Ahmedabad Municipal Corporation (AMC).

Contains ward registry, department registry, area-to-ward mappings, and
issue classification rules. This is the single source of truth for all
civic agent tool calls — no other module defines ward or department data.

Data is modelled after AMC's actual administrative structure:
  - 7 AMC zones, 48 wards
  - 4 core municipal departments
  - Landmark-based area-to-ward resolution
"""

from typing import Dict, List

# ─────────────────────────────────────────────────────────────────────────────
# AMC Ward Registry
# Maps ward_id → ward metadata (zone, landmarks, officer, pincode).
# Subset of 8 representative wards covering all 7 AMC zones.
# ─────────────────────────────────────────────────────────────────────────────
WARD_REGISTRY: Dict[str, Dict] = {
    "W08": {
        "ward_id": "W08",
        "ward_name": "Bodakdev",
        "zone_name": "North West Zone",
        "pincode": "380054",
        "area_sq_km": 14.8,
        "officer_name": "R. V. Patel",
        "officer_designation": "Junior Engineer (Roads)",
        "officer_phone": "079-26871201",
        "landmarks": [
            "SG Highway", "Sindhu Bhavan Road", "Pakwan Crossroads",
            "Judges Bungalow", "Bodakdev", "Thaltej",
        ],
        "coordinates": {"lat": 23.0487, "lng": 72.5074},
    },
    "W09": {
        "ward_id": "W09",
        "ward_name": "Thaltej",
        "zone_name": "North West Zone",
        "pincode": "380059",
        "area_sq_km": 16.2,
        "officer_name": "D. C. Joshi",
        "officer_designation": "Chief Ward Inspector",
        "officer_phone": "079-26850410",
        "landmarks": [
            "Thaltej Cross Road", "Hebatpur Road", "Science City Circle",
            "Shilaj Road", "Thaltej",
        ],
        "coordinates": {"lat": 23.0569, "lng": 72.4967},
    },
    "W12": {
        "ward_id": "W12",
        "ward_name": "Navrangpura",
        "zone_name": "West Zone",
        "pincode": "380009",
        "area_sq_km": 8.5,
        "officer_name": "K. M. Solanki",
        "officer_designation": "Chief Ward Inspector",
        "officer_phone": "079-26563319",
        "landmarks": [
            "C.G. Road", "Gujarat University", "Stadium Cross Road",
            "Mithakhali Six Roads", "Navrangpura", "Law Garden",
        ],
        "coordinates": {"lat": 23.0350, "lng": 72.5610},
    },
    "W15": {
        "ward_id": "W15",
        "ward_name": "Satellite",
        "zone_name": "West Zone",
        "pincode": "380015",
        "area_sq_km": 11.3,
        "officer_name": "A. P. Shah",
        "officer_designation": "Junior Engineer (Water)",
        "officer_phone": "079-26742210",
        "landmarks": [
            "Satellite Road", "Jodhpur Cross Road", "Prahladnagar",
            "Anand Nagar", "Shyamal Cross Road", "Satellite",
        ],
        "coordinates": {"lat": 23.0225, "lng": 72.5290},
    },
    "W24": {
        "ward_id": "W24",
        "ward_name": "Maninagar",
        "zone_name": "South Zone",
        "pincode": "380008",
        "area_sq_km": 9.7,
        "officer_name": "N. S. Prajapati",
        "officer_designation": "Chief Ward Inspector",
        "officer_phone": "079-25460882",
        "landmarks": [
            "Kankaria Lake", "Gate 1-4", "Maninagar Railway Station",
            "Rambaug", "Balvatika", "Maninagar",
        ],
        "coordinates": {"lat": 23.0070, "lng": 72.6040},
    },
    "W03": {
        "ward_id": "W03",
        "ward_name": "Dariapur",
        "zone_name": "Central Zone",
        "pincode": "380001",
        "area_sq_km": 5.2,
        "officer_name": "M. R. Syed",
        "officer_designation": "Senior Ward Inspector",
        "officer_phone": "079-25620114",
        "landmarks": [
            "Dariapur", "Shahpur", "Kalupur Station", "Relief Road",
            "Teen Darwaza", "Old City",
        ],
        "coordinates": {"lat": 23.0290, "lng": 72.5920},
    },
    "W30": {
        "ward_id": "W30",
        "ward_name": "Vastral",
        "zone_name": "East Zone",
        "pincode": "382418",
        "area_sq_km": 18.6,
        "officer_name": "B. K. Rathod",
        "officer_designation": "Junior Engineer (Drainage)",
        "officer_phone": "079-22861140",
        "landmarks": [
            "Vastral", "Nikol", "Odhav Ring Road", "Narol",
            "Vastral Gam", "Lambha",
        ],
        "coordinates": {"lat": 22.9930, "lng": 72.6480},
    },
    "W42": {
        "ward_id": "W42",
        "ward_name": "Chandkheda",
        "zone_name": "North Zone",
        "pincode": "382424",
        "area_sq_km": 20.1,
        "officer_name": "P. S. Trivedi",
        "officer_designation": "Chief Ward Inspector",
        "officer_phone": "079-29292100",
        "landmarks": [
            "Chandkheda", "Zundal", "Adalaj", "Koba Circle",
            "Randesan", "Motera Stadium",
        ],
        "coordinates": {"lat": 23.1080, "lng": 72.5910},
    },
}


# ─────────────────────────────────────────────────────────────────────────────
# AMC Department Registry
# Maps department_id → department metadata (SLA, contact, scope).
# ─────────────────────────────────────────────────────────────────────────────
DEPARTMENT_REGISTRY: Dict[str, Dict] = {
    "ROADS_NW": {
        "department_id": "ROADS_NW",
        "department_name": "Roads & Buildings",
        "division": "Project Division (West)",
        "nodal_officer": "Er. Rajesh B. Vora",
        "helpline": "079-27550114",
        "sla_hours": 48,
        "scope": [
            "pothole", "road_damage", "asphalt_crack", "speed_bump",
            "road_cave_in", "footpath_damage",
        ],
    },
    "WATER_SW": {
        "department_id": "WATER_SW",
        "department_name": "Water & Sewerage",
        "division": "City Hydraulics & Drainage Wing",
        "nodal_officer": "Er. Sneha K. Mehta",
        "helpline": "079-25391800",
        "sla_hours": 24,
        "scope": [
            "water_logging", "water_leak", "pipe_burst", "sewage_overflow",
            "drainage_block", "water_contamination",
        ],
    },
    "SOLID_WASTE": {
        "department_id": "SOLID_WASTE",
        "department_name": "Solid Waste & Health",
        "division": "Public Sanitation & Vector Control",
        "nodal_officer": "Dr. Bhavin R. Solanki",
        "helpline": "1800-233-2330",
        "sla_hours": 12,
        "scope": [
            "garbage_dump", "waste_overflow", "dead_animal",
            "open_defecation", "debris", "construction_waste",
        ],
    },
    "ELECTRICAL": {
        "department_id": "ELECTRICAL",
        "department_name": "Streetlight & Electrical",
        "division": "Smart LED & Feeder Management",
        "nodal_officer": "Er. Anand P. Trivedi",
        "helpline": "079-27556100",
        "sla_hours": 24,
        "scope": [
            "streetlight_off", "broken_pole", "exposed_wire",
            "transformer_issue", "flickering_light", "electrical_hazard",
        ],
    },
}


# ─────────────────────────────────────────────────────────────────────────────
# Issue Classification Rules
# Maps detected issue class → (severity, department_id, urgency_label).
# Used by the vision engine to route complaints deterministically.
# ─────────────────────────────────────────────────────────────────────────────
ISSUE_CLASSIFICATION: Dict[str, Dict] = {
    "pothole": {
        "label": "Severe Asphalt Crater",
        "severity": 4,
        "max_severity": 5,
        "department_id": "ROADS_NW",
        "urgency": "URGENT",
        "sla_hours": 24,
        "repair_unit": "Rapid Asphalt Unit",
    },
    "road_damage": {
        "label": "Road Surface Damage",
        "severity": 3,
        "max_severity": 5,
        "department_id": "ROADS_NW",
        "urgency": "HIGH",
        "sla_hours": 48,
        "repair_unit": "Road Maintenance Crew",
    },
    "garbage_dump": {
        "label": "Illegal Garbage Dump",
        "severity": 3,
        "max_severity": 5,
        "department_id": "SOLID_WASTE",
        "urgency": "HIGH",
        "sla_hours": 12,
        "repair_unit": "Sanitation Response Van",
    },
    "water_logging": {
        "label": "Severe Water Logging",
        "severity": 4,
        "max_severity": 5,
        "department_id": "WATER_SW",
        "urgency": "URGENT",
        "sla_hours": 24,
        "repair_unit": "Drainage Emergency Crew",
    },
    "pipe_burst": {
        "label": "Municipal Water Pipe Burst",
        "severity": 5,
        "max_severity": 5,
        "department_id": "WATER_SW",
        "urgency": "CRITICAL",
        "sla_hours": 6,
        "repair_unit": "Emergency Pipeline Squad",
    },
    "streetlight_off": {
        "label": "Streetlight Inactive",
        "severity": 2,
        "max_severity": 5,
        "department_id": "ELECTRICAL",
        "urgency": "NORMAL",
        "sla_hours": 24,
        "repair_unit": "LED Maintenance Team",
    },
    "broken_pole": {
        "label": "Broken Utility Pole",
        "severity": 4,
        "max_severity": 5,
        "department_id": "ELECTRICAL",
        "urgency": "URGENT",
        "sla_hours": 12,
        "repair_unit": "Pole Replacement Unit",
    },
    "sewage_overflow": {
        "label": "Open Sewage Overflow",
        "severity": 5,
        "max_severity": 5,
        "department_id": "WATER_SW",
        "urgency": "CRITICAL",
        "sla_hours": 6,
        "repair_unit": "Sewage Emergency Response",
    },
}


# ─────────────────────────────────────────────────────────────────────────────
# Area → Ward Lookup
# Flattened mapping of area/landmark names to ward IDs.
# Built from WARD_REGISTRY landmarks for O(1) lookups.
# ─────────────────────────────────────────────────────────────────────────────
AREA_TO_WARD: Dict[str, str] = {}
for _ward_id, _ward_data in WARD_REGISTRY.items():
    for _landmark in _ward_data["landmarks"]:
        AREA_TO_WARD[_landmark.lower()] = _ward_id


# ─────────────────────────────────────────────────────────────────────────────
# Severity Thresholds → Status Labels
# ─────────────────────────────────────────────────────────────────────────────
SEVERITY_STATUS_MAP: List[tuple] = [
    (5, "CRITICAL"),
    (4, "URGENT"),
    (3, "HIGH"),
    (2, "NORMAL"),
    (1, "LOW"),
]


def get_severity_label(severity: int) -> str:
    """Return the human-readable severity label for a numeric score."""
    for threshold, label in SEVERITY_STATUS_MAP:
        if severity >= threshold:
            return label
    return "LOW"
