from .models import Donor
import math

# All 77 official Nepal districts with GPS coordinates (lat, lng)
NEPAL_DISTRICTS = [
    "achham", "arghakhanchi", "baglung", "baitadi", "bajhang", "bajura",
    "banke", "bara", "bardiya", "bhaktapur", "bhojpur", "chitwan",
    "dadeldhura", "dailekh", "dang", "darchula", "dhading", "dhankuta",
    "dhanusa", "dolakha", "dolpa", "doti", "eastern rukum", "gorkha",
    "gulmi", "humla", "ilam", "jajarkot", "jhapa", "jumla", "kailali",
    "kalikot", "kanchanpur", "kapilvastu", "kaski", "kathmandu",
    "kavrepalanchok", "khotang", "lalitpur", "lamjung", "mahottari",
    "makwanpur", "manang", "morang", "mugu", "mustang", "myagdi",
    "nawalparasi east", "nawalparasi west", "nuwakot", "okhaldhunga",
    "palpa", "panchthar", "parbat", "parsa", "pyuthan", "ramechhap",
    "rasuwa", "rautahat", "rolpa", "rupandehi", "salyan", "sankhuwasabha",
    "saptari", "sarlahi", "sindhuli", "sindhupalchok", "siraha",
    "solukhumbu", "sunsari", "surkhet", "syangja", "tanahun", "taplejung",
    "tehrathum", "udayapur", "western rukum",
]

# District coordinates (lat, lng)
DISTRICT_COORDS = {
    "achham": (29.0875, 81.3497),
    "arghakhanchi": (27.9667, 83.1500),
    "baglung": (28.2700, 83.5900),
    "baitadi": (29.5333, 80.4333),
    "bajhang": (29.5500, 81.1833),
    "bajura": (29.3700, 81.6000),
    "banke": (28.0500, 81.6000),
    "bara": (27.0167, 85.0167),
    "bardiya": (28.3000, 81.5000),
    "bhaktapur": (27.6710, 85.4298),
    "bhojpur": (27.1700, 87.0500),
    "chitwan": (27.5300, 84.3542),
    "dadeldhura": (29.2933, 80.5750),
    "dailekh": (28.8433, 81.7167),
    "dang": (28.1000, 82.3000),
    "darchula": (29.8600, 80.5500),
    "dhading": (27.8700, 84.9000),
    "dhankuta": (26.9833, 87.3500),
    "dhanusa": (26.8100, 85.9200),
    "dolakha": (27.6700, 86.1000),
    "dolpa": (29.0000, 82.9667),
    "doti": (29.2667, 80.9500),
    "eastern rukum": (28.6167, 82.6333),
    "gorkha": (28.0000, 84.6333),
    "gulmi": (28.0833, 83.2833),
    "humla": (30.1200, 81.9200),
    "ilam": (26.9100, 87.9200),
    "jajarkot": (28.7000, 82.1833),
    "jhapa": (26.6500, 87.9167),
    "jumla": (29.2750, 82.1833),
    "kailali": (28.7167, 80.9667),
    "kalikot": (29.1333, 81.6333),
    "kanchanpur": (28.9833, 80.3667),
    "kapilvastu": (27.5500, 83.0500),
    "kaski": (28.2096, 83.9856),
    "kathmandu": (27.7172, 85.3240),
    "kavrepalanchok": (27.5333, 85.6667),
    "khotang": (27.0167, 86.8333),
    "lalitpur": (27.6588, 85.3247),
    "lamjung": (28.1500, 84.4000),
    "mahottari": (26.8500, 85.7000),
    "makwanpur": (27.4333, 85.0333),
    "manang": (28.6667, 84.0167),
    "morang": (26.6500, 87.3500),
    "mugu": (29.5167, 82.3833),
    "mustang": (28.9973, 83.8480),
    "myagdi": (28.4167, 83.5833),
    "nawalparasi east": (27.5667, 84.1167),
    "nawalparasi west": (27.6500, 83.6833),
    "nuwakot": (27.9333, 85.1667),
    "okhaldhunga": (27.3167, 86.5000),
    "palpa": (27.8667, 83.5333),
    "panchthar": (27.1500, 87.8000),
    "parbat": (28.2333, 83.6833),
    "parsa": (27.1333, 84.8667),
    "pyuthan": (28.1000, 82.8667),
    "ramechhap": (27.3267, 86.0833),
    "rasuwa": (28.1500, 85.3667),
    "rautahat": (27.0000, 85.3000),
    "rolpa": (28.3500, 82.6500),
    "rupandehi": (27.5333, 83.3667),
    "salyan": (28.3667, 82.1667),
    "sankhuwasabha": (27.3500, 87.2167),
    "saptari": (26.6500, 86.7167),
    "sarlahi": (27.0333, 85.5833),
    "sindhuli": (27.2500, 85.9667),
    "sindhupalchok": (27.9500, 85.6833),
    "siraha": (26.6500, 86.2000),
    "solukhumbu": (27.7000, 86.6667),
    "sunsari": (26.6500, 87.1667),
    "surkhet": (28.6000, 81.6167),
    "syangja": (28.0500, 83.8833),
    "tanahun": (27.9167, 84.2333),
    "taplejung": (27.3543, 87.6648),
    "tehrathum": (27.1167, 87.5667),
    "udayapur": (26.9167, 86.5167),
    "western rukum": (28.7667, 82.3667),
}

def is_valid_district(district):
    """Returns True if district is one of the 77 Nepal districts."""
    return district.strip().lower() in NEPAL_DISTRICTS

# Haversine formula - calculate distance in km between two GPS points
def haversine(lat1, lng1, lat2, lng2):
    R = 6371  # Earth radius in km
    lat1, lng1, lat2, lng2 = map(math.radians, [lat1, lng1, lat2, lng2])
    dlat = lat2 - lat1
    dlng = lng2 - lng1
    a = math.sin(dlat/2)**2 + math.cos(lat1) * math.cos(lat2) * math.sin(dlng/2)**2
    return R * 2 * math.asin(math.sqrt(a))

# Blood group compatibility chart
COMPATIBILITY = {
    'A+':  ['A+', 'A-', 'O+', 'O-'],
    'A-':  ['A-', 'O-'],
    'B+':  ['B+', 'B-', 'O+', 'O-'],
    'B-':  ['B-', 'O-'],
    'O+':  ['O+', 'O-'],
    'O-':  ['O-'],
    'AB+': ['A+', 'A-', 'B+', 'B-', 'O+', 'O-', 'AB+', 'AB-'],
    'AB-': ['A-', 'B-', 'O-', 'AB-'],
}

def proximity_score(distance_km):
    """Convert distance to score (max 30 points)"""
    if distance_km <= 10:
        return 30
    elif distance_km <= 30:
        return 25
    elif distance_km <= 60:
        return 20
    elif distance_km <= 100:
        return 15
    elif distance_km <= 200:
        return 10
    else:
        return 5

def calculate_score(donor, requested_blood, patient_lat, patient_lng):
    score = 0

    # Step 1 - Blood compatibility (50 points)
    compatible = COMPATIBILITY.get(requested_blood, [])
    if donor.blood_group in compatible:
        score += 50

    # Step 2 - GPS proximity (30 points)
    donor_coords = DISTRICT_COORDS.get(donor.district.lower())
    if donor_coords and patient_lat and patient_lng:
        distance = haversine(donor_coords[0], donor_coords[1], patient_lat, patient_lng)
        score += proximity_score(distance)

    # Step 3 - Donor is available (20 points)
    if donor.is_available:
        score += 20

    return score

def find_donors(requested_blood, patient_lat=None, patient_lng=None):
    donors = Donor.objects.filter(is_available=True)

    scored = []
    for donor in donors:
        score = calculate_score(donor, requested_blood, patient_lat, patient_lng)
        if score >= 50:
            # calculate distance for display
            donor_coords = DISTRICT_COORDS.get(donor.district.lower())
            distance_km = None
            if donor_coords and patient_lat and patient_lng:
                distance_km = round(haversine(
                    donor_coords[0], donor_coords[1],
                    patient_lat, patient_lng
                ))
            scored.append({
                'donor': donor,
                'score': score,
                'name': donor.user.get_full_name(),
                'blood_group': donor.blood_group,
                'district': donor.district,
                'phone': donor.phone,
                'distance_km': distance_km,
            })

    scored.sort(key=lambda x: x['score'], reverse=True)
    return scored