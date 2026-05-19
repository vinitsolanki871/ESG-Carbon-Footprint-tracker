"""
config.py
---------
All static constants: emission factors, scope mapping, and Indian facility registry.
Source: CEA 2025 grid EF · MoPNG fuel factors · GHG Protocol
"""

# kg CO2e emitted per kWh of energy consumed
EMISSION_FACTORS = {
    "Electricity": 0.82,   # CEA 2025 national grid average — Scope 2
    "Natural Gas": 0.202,  # MoPNG / GHG Protocol             — Scope 1
    "Diesel":      0.267,  # MoPNG / GHG Protocol             — Scope 1
    "Solar":       0.05,   # lifecycle estimate                — Scope 2
    "Wind":        0.03,   # lifecycle estimate                — Scope 2
    "Biomass":     0.11,   # combustion average                — Scope 1
}

SCOPE_MAP = {
    "Electricity": "Scope 2",
    "Natural Gas": "Scope 1",
    "Diesel":      "Scope 1",
    "Solar":       "Scope 2",
    "Wind":        "Scope 2",
    "Biomass":     "Scope 1",
}

# 20 Indian industrial cities with real 2025 coordinates
FACILITIES = {
    "IND-001": {"city": "New Delhi",     "state": "Delhi",           "lat": 28.7041, "lon": 77.1025, "industry": "Manufacturing"},
    "IND-002": {"city": "Mumbai",        "state": "Maharashtra",     "lat": 19.0760, "lon": 72.8777, "industry": "Petrochemical"},
    "IND-003": {"city": "Bengaluru",     "state": "Karnataka",       "lat": 12.9716, "lon": 77.5946, "industry": "IT & Data Centers"},
    "IND-004": {"city": "Chennai",       "state": "Tamil Nadu",      "lat": 13.0827, "lon": 80.2707, "industry": "Automobile"},
    "IND-005": {"city": "Kolkata",       "state": "West Bengal",     "lat": 22.5726, "lon": 88.3639, "industry": "Steel & Metals"},
    "IND-006": {"city": "Hyderabad",     "state": "Telangana",       "lat": 17.3850, "lon": 78.4867, "industry": "Pharma"},
    "IND-007": {"city": "Pune",          "state": "Maharashtra",     "lat": 18.5204, "lon": 73.8567, "industry": "Automobile"},
    "IND-008": {"city": "Ahmedabad",     "state": "Gujarat",         "lat": 23.0225, "lon": 72.5714, "industry": "Textile"},
    "IND-009": {"city": "Surat",         "state": "Gujarat",         "lat": 21.1702, "lon": 72.8311, "industry": "Diamond & Textile"},
    "IND-010": {"city": "Jaipur",        "state": "Rajasthan",       "lat": 26.9124, "lon": 75.7873, "industry": "Gems & Jewellery"},
    "IND-011": {"city": "Lucknow",       "state": "Uttar Pradesh",   "lat": 26.8467, "lon": 80.9462, "industry": "Food Processing"},
    "IND-012": {"city": "Kanpur",        "state": "Uttar Pradesh",   "lat": 26.4499, "lon": 80.3319, "industry": "Leather & Chemicals"},
    "IND-013": {"city": "Nagpur",        "state": "Maharashtra",     "lat": 21.1458, "lon": 79.0882, "industry": "Mining & Coal"},
    "IND-014": {"city": "Visakhapatnam","state": "Andhra Pradesh",   "lat": 17.6868, "lon": 83.2185, "industry": "Steel & Ports"},
    "IND-015": {"city": "Bhopal",        "state": "Madhya Pradesh",  "lat": 23.2599, "lon": 77.4126, "industry": "Heavy Engineering"},
    "IND-016": {"city": "Coimbatore",    "state": "Tamil Nadu",      "lat": 11.0168, "lon": 76.9558, "industry": "Textile & Pumps"},
    "IND-017": {"city": "Kochi",         "state": "Kerala",          "lat":  9.9312, "lon": 76.2673, "industry": "Shipbuilding"},
    "IND-018": {"city": "Indore",        "state": "Madhya Pradesh",  "lat": 22.7196, "lon": 75.8577, "industry": "Pharmaceuticals"},
    "IND-019": {"city": "Vadodara",      "state": "Gujarat",         "lat": 22.3072, "lon": 73.1812, "industry": "Petrochemical"},
    "IND-020": {"city": "Ludhiana",      "state": "Punjab",          "lat": 30.9010, "lon": 75.8573, "industry": "Hosiery & Cycles"},
}

# Industry-specific baseline monthly consumption (mean kWh, std dev)
INDUSTRY_CONSUMPTION = {
    "Manufacturing":       (18_000, 4_000),
    "Petrochemical":       (32_000, 7_000),
    "IT & Data Centers":   (12_000, 2_500),
    "Automobile":          (22_000, 5_000),
    "Steel & Metals":      (45_000, 9_000),
    "Pharma":              (14_000, 3_000),
    "Textile":             (10_000, 2_000),
    "Diamond & Textile":   (9_500,  2_000),
    "Gems & Jewellery":    (7_000,  1_500),
    "Food Processing":     (8_500,  1_800),
    "Leather & Chemicals": (11_000, 2_500),
    "Mining & Coal":       (38_000, 8_000),
    "Steel & Ports":       (42_000, 8_500),
    "Heavy Engineering":   (20_000, 4_500),
    "Textile & Pumps":     (10_000, 2_000),
    "Shipbuilding":        (16_000, 3_500),
    "Pharmaceuticals":     (13_000, 2_800),
    "Hosiery & Cycles":    (9_000,  2_000),
    "default":             (12_000, 3_000),
}

# Realistic 2024 energy source mix probabilities per industry
INDUSTRY_ENERGY_MIX = {
    "Manufacturing":       {"Electricity": 0.45, "Natural Gas": 0.20, "Diesel": 0.20, "Solar": 0.10, "Biomass": 0.05, "Wind": 0.00},
    "Petrochemical":       {"Electricity": 0.30, "Natural Gas": 0.45, "Diesel": 0.15, "Solar": 0.05, "Biomass": 0.05, "Wind": 0.00},
    "IT & Data Centers":   {"Electricity": 0.60, "Natural Gas": 0.05, "Diesel": 0.10, "Solar": 0.20, "Biomass": 0.00, "Wind": 0.05},
    "Automobile":          {"Electricity": 0.40, "Natural Gas": 0.25, "Diesel": 0.20, "Solar": 0.10, "Biomass": 0.05, "Wind": 0.00},
    "Steel & Metals":      {"Electricity": 0.35, "Natural Gas": 0.15, "Diesel": 0.25, "Solar": 0.05, "Biomass": 0.10, "Wind": 0.10},
    "Pharma":              {"Electricity": 0.50, "Natural Gas": 0.20, "Diesel": 0.10, "Solar": 0.15, "Biomass": 0.05, "Wind": 0.00},
    "default":             {"Electricity": 0.40, "Natural Gas": 0.20, "Diesel": 0.20, "Solar": 0.10, "Biomass": 0.05, "Wind": 0.05},
}

CHART_PALETTE = ["#00C896", "#FF6B6B", "#FFE66D", "#4ECDC4", "#A78BFA", "#FF9F43"]
