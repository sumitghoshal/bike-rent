#!/usr/bin/env python3
"""
RentBike — MongoDB Atlas Seed Script
Run from project root:  python seed.py
"""
import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'backend'))

from werkzeug.security import generate_password_hash
from datetime import datetime, timedelta

from config.database import get_db
from models.schemas  import (user_schema, bike_schema,
                              booking_schema, review_schema, payment_schema)

print('\n🔌 Connecting to MongoDB Atlas...')
db = get_db()
print('Connected!\n')

# ── Clear ──────────────────────────────────────────────────────────
print('🧹  Clearing existing data...')
for col in ('users', 'bikes', 'bookings', 'reviews', 'payments'):
    getattr(db, col).drop()
    print(f'   dropped: {col}')

# ── Users ──────────────────────────────────────────────────────────
print('\n👤  Seeding users...')
USERS = [
    ('Admin User',    'admin@rentbike.in',   'admin123',  '9999999999', 'admin',  'approved', False),
    ('Raj Vendor',    'vendor@rentbike.in',  'vendor123', '9888888888', 'vendor', 'approved', False),
    ('Meera Vendor',  'meera@rentbike.in',   'vendor123', '9877777777', 'vendor', 'approved', False),
    ('Rohan Sharma',  'rohan@example.com',   'user123',   '9777777777', 'user',   'approved', False),
    ('Priya Nair',    'priya@example.com',   'user123',   '9666666666', 'user',   'pending',  True),
    ('Arjun Patel',   'arjun@example.com',   'user123',   '9555555555', 'user',   'approved', False),
    ('Sneha Rao',     'sneha@example.com',   'user123',   '9444444444', 'vendor', 'pending',  True),
    ('Vikram Singh',  'vikram@example.com',  'user123',   '9333333333', 'user',   'approved', False),
    ('Kavya Reddy',   'kavya@example.com',   'user123',   '9222222222', 'user',   'approved', False),
    ('Aditya Kumar',  'aditya@example.com',  'user123',   '9111111111', 'user',   'approved', False),
]

ids = {}
for name, email, pwd, phone, role, kyc, has_lic in USERS:
    u = user_schema(name, email, generate_password_hash(pwd), phone, role)
    u['kyc_status'] = kyc
    if has_lic:
        u['license_image'] = f"lic_{name.lower().replace(' ', '_')}.jpg"
    r = db.users.insert_one(u)
    ids[email] = r.inserted_id
    print(f'   {role:6s}  {email}  /  {pwd}')

admin_id  = ids['admin@rentbike.in']
vendor_id = ids['vendor@rentbike.in']
vendor2_id= ids['meera@rentbike.in']
rohan_id  = ids['rohan@example.com']
priya_id  = ids['priya@example.com']
arjun_id  = ids['arjun@example.com']
vikram_id = ids['vikram@example.com']
kavya_id  = ids['kavya@example.com']
aditya_id = ids['aditya@example.com']

# ── Bikes ──────────────────────────────────────────────────────────
# Format:
# (name, type, brand, model, year, price_per_hour, price_per_day,
#  location, rating, total_reviews, description, features, image_url, vendor_id)
print('\n🏍️   Seeding bikes...')

BIKES = [

    # ═══════════════════════════════════════════════
    # MOUNTAIN BIKES  (10 bikes)
    # ═══════════════════════════════════════════════
    (
        'Royal Enfield Himalayan 450', 'mountain', 'Trek', 'X-Caliber 9', 2024,
        140, 900, 'Hyderabad', 4.9, 87,
        '29" hardtail MTB with Fox fork and Shimano SLX drivetrain. Perfect for cross-country trails.',
        ['29" Fox Fork', 'Shimano SLX 12sp', 'Hydraulic Disc Brakes', 'Tubeless Ready', 'Alloy Frame'],
        'https://images.openai.com/static-rsc-4/H4C9y-DhLqPU4tofUbGdQTROwlS5wkbDs9Mb3mUS7MlFEUEx15d5MfWj7DQPuNcrcOH3AGy7cnfe_qKC4yrwUKDT9QmeDGXoGto3_IJkOHM4DpINJ6JAqhohp3x0uPLvn3vzSli44_Q-xUgrT7OxeZBLBFbQyg47KfM9p3yCShkXkjYuAsMxHRtORxlwW8X5?purpose=fullsize',
        vendor_id,
    ),
    (
        'KTM 390 Adventure', 'mountain', 'Scott', 'Scale 940', 2024,
        220, 1400, 'Bangalore', 4.8, 54,
        'Full suspension XC race machine with carbon frame and Shimano XTR components.',
        ['Full-Suspension', 'Carbon Frame', 'Shimano XTR 12sp', 'Fox TCS Fork', 'Tubeless'],
        'https://www.ktmindia.com/-/media/images/ktm/booking/ktm-pngs-and-webps/2025-ktm-390-adventure/ktm-390-adventure_orange.webp',
        vendor_id,
    ),
    (
        'Hero Xpulse 200 4V', 'mountain', 'Giant', 'Trance 29', 2023,
        180, 1100, 'Pune', 4.7, 41,
        'Trail enduro bike with 130mm travel and powerful braking for aggressive riding.',
        ['130mm Travel', 'Maestro Suspension', '29" Wheels', 'Dropper Post', 'Shimano Deore'],
        'https://images.openai.com/static-rsc-4/MXCPH2Bh_MTJtOf8I_MKGAjdyMQRIIDd937aKVhITPqk19MeBkr5Q0igTGEuF9LF6-Ob7sDus0eQDLxB6M7sHhQRb0mTgcmuiwnz7qYLVev5u0vzWGXOBxcPM3M_Dp3fXLJskzFNoum8Rqh3oUQkC4PpW8Nj0Gr1VRGUG_D1f-TG6B_EMUTSW5izUZm6-wM8?purpose=fullsize',
        vendor_id,
    ),
    (
        'BMW G 310 GS', 'mountain', 'Merida', 'Big Nine 300', 2023,
        110, 700, 'Hyderabad', 4.5, 33,
        'Versatile beginner-friendly MTB with reliable components and comfortable geometry.',
        ['29" Wheels', 'Shimano Deore 10sp', 'SR Suntour Fork', 'Disc Brakes', 'Alloy Frame'],
        'https://images.financialexpressdigital.com/2022/07/2022-BMW-G-310-GS-Launched-2.jpg',
        vendor_id,
    ),
    (
        'Yezdi Adventure', 'mountain', 'Specialized', 'Stumpjumper', 2023,
        200, 1200, 'Delhi', 4.8, 62,
        'Iconic trail bike for all terrains with SWAT storage and superb handling.',
        ['140mm Travel', 'SWAT Door Storage', 'RockShox Pike', 'SRAM GX Eagle', 'Dropper Post'],
        'https://imgd.aeplcdn.com/1280x720/n/cw/ec/1/versions/yezdi-adventure-forest-green-white1749039950945.jpg',
        vendor2_id,
    ),
    (
        'Suzuki V-Strom SX', 'mountain', 'Cannondale', 'Trail 5', 2024,
        130, 820, 'Mumbai', 4.6, 28,
        'Dependable trail hardtail with Cannondale\'s SmartForm alloy and 3x drivetrain.',
        ['27.5" Wheels', 'SR Suntour XCT Fork', 'Shimano Altus 3x8', 'Disc Brakes', 'SmartForm Alloy'],
        'https://imgd.aeplcdn.com/1280x720/n/cw/ec/125103/v-strom-sx-right-side-view-4.png?isig=0',
        vendor2_id,
    ),
    (
        'Royal Enfield Scram 411', 'mountain', 'BMC', 'Fourstroke 01', 2024,
        250, 1600, 'Hyderabad', 4.9, 45,
        'Swiss-engineered XC race bike with carbon frame and top-tier Shimano XTR build.',
        ['Carbon Frame', 'Shimano XTR Di2', 'RockShox SID', 'Tubeless', 'Integrated Cockpit'],
        'https://images.openai.com/static-rsc-4/jfj76pKgR8on0mskwO-jGSEffYGWhpSeKig82KL2LSU99uBpye2FnhhZ0EDi-nOQo9bhcyNqIz2UW1yDDi5MrD--cLwQ4mFIL9wsgWa14mqe_l_0-5Ntw-bVoxF9pNunpoRVKy2tbzRGrMhxYA9HlsYBpWiNGcXQAZFFMIucjYBHeJ673eulDc-mEVWGQ-YI?purpose=fullsize',
        vendor_id,
    ),
    (
        'KTM 250 Adventure', 'mountain', 'Firefox', 'Tremor Pro', 2023,
        95, 600, 'Chennai', 4.3, 21,
        'Affordable hardtail MTB ideal for beginners exploring off-road trails.',
        ['26" Wheels', 'Alloy Frame', 'Shimano 21sp', 'V-Brakes', 'SR Suntour Fork'],
        'https://cdn.bajajauto.com/-/media/images/ktm/ktm-bikes/travel/2025-ktm-250-adv/cards/rally-3/ktm-250-adventure_featues_desktop_590-x-490_bodywork.webp',
        vendor2_id,
    ),
    (
        'Honda CB200X', 'mountain', 'Hero', 'Sprint Cyclone', 2023,
        90, 560, 'Kolkata', 4.2, 18,
        'Entry-level mountain bike with sturdy frame and multi-terrain capability.',
        ['26" Wheels', 'Steel Frame', '21-Speed Shimano', 'Disc Brakes', 'Suspension Fork'],
        'https://images.openai.com/static-rsc-4/GcLl3jKIsRhn8w_R08H8MvkBEWrPC-MvV8d-ERzAY1wXIXnl3dir9_UsilQ9eNdc7KvQdZAKTIceg3ceA3aAsIFHHhYy2KxYqPwL25ZL_skfWEzA8TnstEree6vRbfc_h8SbJq7oQwhwDZqaefwpd9JfzH9eptabB5Y5whUGy6X4fjd-pb8HjQbuj3xJcPiD?purpose=fullsize',
        vendor2_id,
    ),
    (
        'Benelli TRK 502X', 'mountain', 'Btwin', 'Rockrider 500', 2024,
        105, 680, 'Jaipur', 4.4, 24,
        'Well-equipped MTB for weekend trail riders with reliable hydraulic disc brakes.',
        ['27.5" Wheels', 'Alloy Frame', 'Shimano Altus', 'Hydraulic Disc', 'Suspension Fork'],
        'https://cdn.bikedekho.com/processedimages/benelli/benelli-trk-502/source/benelli-trk-5026936828dac483.jpg?imwidth=400&impolicy=resize',
        vendor_id,
    ),

   #═══════════════════════════════════════════════
    # ROAD BIKES  (10 bikes)
    # ═══════════════════════════════════════════════
    (
        'Hero HF Deluxe', 'road', 'Hero', 'Domane SL 6', 2024,
        170, 1050, 'Bangalore', 4.8, 49,
        'Endurance carbon road bike with IsoSpeed decoupler for smooth long-distance rides.',
        ['OCLV Carbon Frame', 'Shimano 105 Di2', 'Carbon Fork', 'Disc Brakes', 'IsoSpeed'],
        'https://imgd.aeplcdn.com/664x374/n/bw/models/colors/hero-select-model-blue-black-1707131824745.png?q=80',
        vendor_id,
    ),
    (
        'Bajaj CT 100', 'road', 'Bajaj', 'SuperSix EVO', 2023,
        150, 920, 'Hyderabad', 4.7, 38,
        'Lightweight aero road bike built for climbing and fast group rides.',
        ['BallisTec Carbon', 'Shimano 105 12sp', 'Carbon Fork', 'Hydraulic Disc', 'Aero Design'],
        'https://imgd.aeplcdn.com/664x374/n/bw/models/colors/undefined-gloss-ebony-black-with-blue-decals-1587632761911.jpg?q=80',
        vendor_id,
    ),
    (
        'Hero Splendor Plus', 'road', 'Hero', 'Teammachine ALR', 2023,
        190, 1150, 'Mumbai', 4.9, 71,
        'Premium Swiss alloy road bike with race geometry and Shimano Ultegra components.',
        ['Swiss Engineering', 'Shimano Ultegra 11sp', 'Aero Geometry', 'Integrated Cockpit', 'Disc Brakes'],
        'https://imgd.aeplcdn.com/664x374/n/b35v6hb_1880993.jpg?q=80',
        vendor2_id,
    ),
    (
        'TVS Radeon', 'road', 'TVS ', 'Allez Sprint', 2024,
        160, 980, 'Delhi', 4.8, 56,
        'E5 premium aluminum road bike with an aero-tuned frame for criterium racing.',
        ['E5 Alloy', 'Shimano 105 Di2', 'Aero Tuned', 'Disc Brakes', 'FACT Carbon Fork'],
        'https://www.tvsmotor.com/-/media/sept_2024/Radeon-110.jpg',
        vendor_id,
    ),
    (
        'Honda Shine 125', 'road', 'Honda ', 'Contend AR 2', 2024,
        145, 900, 'Pune', 4.6, 32,
        'Endurance road bike with wide tyre clearance for mixed-surface adventures.',
        ['ALUXX Alloy', 'Shimano Tiagra', 'Disc Brakes', '32mm Tyre Clearance', 'Carbon Fork'],
        'https://encrypted-tbn0.gstatic.com/images?q=tbn:ANd9GcSBETKwcbfufv_4v7iRIc-2wqnc05vPNBNFvw&s',
        vendor2_id,
    ),
    (
        'Hero Passion Plus', 'road', 'Hero', 'Paris', 2023,
        210, 1300, 'Bangalore', 4.9, 44,
        'Italian racing heritage with an asymmetric frame design for superior power transfer.',
        ['Torayca T600 Carbon', 'Shimano Ultegra Di2', 'Asymmetric Frame', 'Disc Brakes', 'MOST Cockpit'],
        'https://5.imimg.com/data5/SELLER/Default/2023/8/336052023/YD/ZB/VL/5590721/hero-passion-plus-bike-500x500.jpg',
        vendor_id,
    ),
    (
        'TVS Apache RTR 160', 'road', 'TVS Apache ', 'Via Nirone 7', 2023,
        155, 950, 'Mumbai', 4.7, 37,
        'Classic Italian road bike with Celeste paint and Shimano 105 drivetrain.',
        ['Alloy Frame', 'Shimano 105 11sp', 'Carbon Fork', 'Caliper Brakes', 'Italian Design'],
        'https://images.openai.com/static-rsc-4/jvAoszcR5NqsJh-_DbWZ_LyFcheCvMPF-OcLm2UEsCmI0XhkFVxNn8sQlVMPu39mgHFa_Y6mPpAoO3cI4qBjsDudmooP4JgzbU4lB-JH6x6-og6h1AC7yIOfCHr03z-HzWDxpkNWz2UikkGdFzvm3CYnjjV9ze4NfMY8h8e1p94TlhMTiOrdYNqFjktj-gst?purpose=fullsize',
        vendor2_id,
    ),
    (
        'Bajaj CT 110', 'road', 'Bajaj ', 'Speedster 10', 2024,
        135, 840, 'Chennai', 4.5, 27,
        'Alloy endurance road bike with solid geometry for long days in the saddle.',
        ['Alloy Frame', 'Shimano Tiagra 10sp', 'Carbon Fork', 'Disc Brakes', 'Endurance Geometry'],
        'https://imgd.aeplcdn.com/664x374/n/wg0nigb_1845510.jpg?q=80',
        vendor_id,
    ),
    (
        'TVS Star City Plus', 'road', 'TVS ', 'Merit 2', 2023,
        120, 760, 'Kolkata', 4.4, 19,
        'Comfortable road bike with relaxed geometry, great for beginners and city commutes.',
        ['Alloy Frame', 'Shimano Claris 8sp', 'Carbon Fork', 'Caliper Brakes', 'Relaxed Geometry'],
        'https://imgd.aeplcdn.com/1280x720/n/cw/ec/211699/star-city-right-front-three-quarter.jpeg?isig=0',
        vendor2_id,
    ),
    (
        'Honda Shine', 'road', 'Honda ', 'Dart 21S', 2023,
        100, 630, 'Hyderabad', 4.3, 15,
        'Budget-friendly road bike with 700C wheels and 21-speed drivetrain for daily training.',
        ['700C Wheels', 'Alloy Frame', '21-Speed Shimano', 'Caliper Brakes', 'Carbon Fork'],
        'https://cdn.bikedekho.com/processedimages/honda/shine-bs6/640X309/shine-bs6697b0541ef23f.jpg',
        vendor_id,
    ),

    # ═══════════════════════════════════════════════
    # ELECTRIC BIKES  (10 bikes)
    # ═══════════════════════════════════════════════
    (
        'Ultraviolette F77', 'electric', 'Ultraviolette ', 'Vado SL 4.0', 2024,
        220, 1300, 'Hyderabad', 4.9, 103,
        'Ultralight electric bike with 320Wh battery and SL 1.1 motor for effortless commuting.',
        ['320Wh Battery', '80km Range', 'SL 1.1 Motor', 'Carbon Belt Drive', 'Integrated Lights'],
        'https://images.openai.com/static-rsc-4/qSu6heJzzwC3eOP58a_A1Pn6fP_tKseBbfI4VtGC7JzAZNleHwX-vRBc11u8fnUMMFrJSYDyC4v7wdZaV0ialLVgILci9t9T2jk-c0Gx-M8FfDdqNxk7tKYH4W8YhhjzSqMC3LRlQ97hU6-rJ3_eOtubbCY-UEX84G0Cx1wlNnswY3pZYnSwttA4GHqUmkeX?purpose=fullsize',
        vendor_id,
    ),
    (
        'Revolt RV400', 'electric', 'Revolt ', 'Allant+ 7S', 2024,
        200, 1200, 'Mumbai', 4.8, 67,
        'Powerful electric commuter with Bosch Performance motor and integrated cargo rack.',
        ['500Wh Battery', 'Bosch Performance', '85Nm Torque', 'Integrated Rack', 'Hydraulic Disc'],
        'https://images.openai.com/static-rsc-4/cDl-nOlt0Zu740-Y4yEYsBBhBxNX-Xa1QUbg_Xj1Jp3AekEjwTYnP_gQBSuM6B6RxqydVhe059jl9CUPT042sYE35b_dTKK4KSvM9MZAoy7_RjIY2kmzqbgAjPZRzRvkquw5FTcsP5XSlIZEOOb5ZzuuYHPLKXVW9rPfuxg0iBJlFQFHr7u_J8M7Q1igTugq?purpose=fullsize',
        vendor_id,
    ),
    (
        'Oben Rorr', 'electric', 'Oben ', 'Quick-E+', 2024,
        175, 1050, 'Bangalore', 4.7, 44,
        'Smart e-bike with SyncDrive Pro motor and EnergyPak 500 battery for city and beyond.',
        ['SyncDrive Pro Motor', '500Wh EnergyPak', 'Auto Assist', 'Integrated Lights', 'Disc Brakes'],
        'https://images.openai.com/static-rsc-4/_FjLrZ8i6B-MfRrmzGy88wdXnU9RSCaeCbVSpH0BYPee0Iyfwwx3pe_ATf11kvXzko24BX0WScZ2mjuvPfzuk_Sbt0jj3V9zrRxYFi-k5rFA4nYLblhMP1uQ0XVj6AULaJcsjO30SMDSkdr3Ws1-eof61eXa0yi9Eo6FIRXS2wmmOUF6n9ukU405AHM6dzY2?purpose=fullsize',
        vendor2_id,
    ),
    (
        'Komaki Ranger', 'electric', 'Komaki ', 'Tesoro Neo X 3', 2023,
        185, 1120, 'Delhi', 4.7, 39,
        'Versatile electric adventure bike with 500Wh battery and Bosch Performance CX motor.',
        ['500Wh Battery', 'Bosch CX Motor', '85Nm Torque', 'Dropper Post', 'Disc Brakes'],
        'https://m.media-amazon.com/images/I/51z6to83OzL._AC_UF1000%2C1000_QL80_.jpg',
        vendor_id,
    ),
    (
        'Hop Oxo', 'electric', 'Hop ', 'F77 Mach 2', 2024,
        230, 1380, 'Hyderabad', 4.9, 58,
        'India\'s fastest electric bike with 150km range and rapid charging capability.',
        ['10.3kWh Battery', '150km Range', '100Nm Torque', 'Rapid Charge', 'Multiple Ride Modes'],
        'https://imgd.aeplcdn.com/1280x720/n/cw/ec/130955/oxo-right-front-three-quarter-3.jpeg?isig=0',
        vendor2_id,
    ),
    (
        'Revolt RV400 BRZ', 'electric', 'Revolt', 'RV400 BRZ', 2024,
        190, 1150, 'Pune', 4.6, 34,
        'Smart electric bike with swappable battery, AI-powered riding modes and low maintenance.',
        ['3.24kWh Battery', '150km Range', 'Swappable Battery', 'AI Modes', 'App Connected'],
        'https://encrypted-tbn0.gstatic.com/images?q=tbn:ANd9GcTvITZvP5C0nTID7iqNd_njvPfrh2PffIn07w&s',
        vendor_id,
    ),
    (
        'Oben Rorr 4.4kWh', 'electric', 'Oben', 'Rorr', 2023,
        165, 1000, 'Chennai', 4.5, 29,
        'Feature-rich electric commuter with liquid-cooled motor and IP67 water resistance.',
        ['4.4kWh Battery', '187km Range', 'Liquid Cooled Motor', 'IP67 Rated', '4G Connectivity'],
        'https://cdn.bikedekho.com/processedimages/oben/rorr-ez/source/rorr-ez672c8c01549f0.jpg',
        vendor2_id,
    ),
    (
        'Ather 450X Gen 3', 'electric', 'Ather', '450X', 2024,
        210, 1260, 'Bangalore', 4.8, 76,
        'Smart scooter with 146km range and Ather Grid fast-charging network access.',
        ['3.7kWh Battery', '146km Range', 'Fast Charging', 'Touchscreen', 'OTA Updates'],
        'https://cdn-s3.autocarindia.com/legacy/cdni/ExtraImages/20220719040657_Ather.jpg?w=728&q=75',
        vendor_id,
    ),
    (
        'Tork Kratos R', 'electric', 'Tork', 'Kratos R', 2023,
        170, 1020, 'Mumbai', 4.5, 22,
        'Performance electric motorcycle with 4G connectivity and multiple riding modes.',
        ['4kWh Battery', '180km Range', '4G Connected', 'Multiple Modes', 'CBS Brakes'],
        'https://c.ndtvimg.com/2022-02/9j8ggfr4_tork-kratos-r-first-ride-review_625x300_25_February_22.jpg',
        vendor2_id,
    ),
    (
        'Bajaj Chetak Premium', 'electric', 'Bajaj', 'Chetak Premium', 2024,
        140, 860, 'Hyderabad', 4.4, 47,
        'Iconic retro-styled electric scooter with steel body and comfortable city ride.',
        ['3kWh Battery', '126km Range', 'Steel Body', 'IP67 Rated', 'Regenerative Braking'],
        'https://images.overdrive.in/wp-content/uploads/2024/01/DSC01548-900x506.jpg',
        vendor_id,
    ),
    # ═══════════════════════════════════════════════
    # CITY BIKES  (10 bikes)
    # ═══════════════════════════════════════════════
    (
        'Hero Splendor Plus', 'city', 'Hero', 'Lectro E5', 2024,
        65, 400, 'Hyderabad', 4.4, 110,
        'Reliable electric-assist city bike with 7-speed gears and front suspension.',
        ['700C Wheels', '7-Speed Shimano', 'Front Suspension', 'Disc Brakes', 'LED Lights'],
        'https://images.openai.com/static-rsc-4/5HvjVM2uS6CNACU0_Z3KRhm-hgPld5_KHvHK4PqiDBbc0BNZTJmamjeEInTJ2D1T-xpr-TdMgQW9WxYmWMA2MEzggNjLO8Hg7MPZGUz4TMN_Mhq8eFO7c0G0xMQwZtROUxZgwFhSfmtA0Y5fJoLpRJ-zBv38IolQlihVGJf2X9qZQq2j6_07xP_parXreULv?purpose=fullsize',
        vendor_id,
    ),
    (
        'Honda Shine', 'city', 'Firefox', 'Breezer Uptown', 2024,
        80, 500, 'Bangalore', 4.5, 72,
        'Step-through frame city cruiser with 8-speed internal hub and integrated fenders.',
        ['700C Wheels', '8-Speed Internal Hub', 'Alloy Frame', 'Fenders & Rack', 'Caliper Brakes'],
        'https://cdn.bikedekho.com/processedimages/honda/shine-bs6/640X309/shine-bs6697b0541ef23f.jpg',
        vendor_id,
    ),
    (
        'Bajaj Pulsar 125', 'city', 'Btwin', 'Elops 500', 2023,
        70, 440, 'Mumbai', 4.4, 58,
        'Dutch-inspired city bike with low step-in, wide saddle and practical accessories.',
        ['Comfort Geometry', 'Hybrid Design', 'Light Alloy Frame', 'Fenders', 'Carrier Rack'],
        'https://cdn.bikedekho.com/processedimages/bajaj/pulsar-125/source/pulsar-12569b91c3b7d5f9.jpg',
        vendor2_id,
    ),
    (
        'TVS Radeon', 'city', 'Trek', 'FX 3 Disc', 2024,
        95, 600, 'Delhi', 4.7, 64,
        'Versatile fitness hybrid bike for fast commuting and recreational riding.',
        ['700C Wheels', 'Alloy Frame', 'Shimano Deore 10sp', 'Disc Brakes', 'Carbon Fork'],
        'https://images.openai.com/static-rsc-4/nmBkBV3VMjMFbigv1vC5oCbiTmP8tflBTypRYCWzhqMYRfdNaPFFBvosL5PUuwbvqcyqMMJ1NrUKgU6maTWdtOA8FvgyowD42-hqgDbHnajzrfNHpJBC95sofC3ce8ZMbxrE9M3UVmLEcjId9_GlhZPHfXQO2nzSuRyosKutwsOC01BQGjS2R7G1oCpKgQxp?purpose=fullsize',
        vendor_id,
    ),
    (
        'Hero HF Deluxe', 'city', 'Giant', 'Escape 3 Disc', 2024,
        75, 470, 'Pune', 4.5, 43,
        'Lightweight city bike with flat handlebars and smooth-rolling 700C wheels.',
        ['ALUXX Alloy', '700C Wheels', 'Shimano Altus 3x8', 'Disc Brakes', 'Relaxed Geometry'],
        'https://images.openai.com/static-rsc-4/hFPfpuZ_RbHbSrXhtgEGSt1fKwyLFkHGJJBdMUVyfwO5JmMCd2RxYvKG13r8Qd6MEIm4DJLgt3ajs_peJOWXFn8aMHhRCna_xy46zEQM63exLhgwsAYH1m8LAdccklAoZocS-0fxUNXzdcW0m6DvcFz2acTEbFAqLSJS8XN4StFk6alR7etTziOccBknOOTR?purpose=fullsize',
        vendor2_id,
    ),
    (
        'TVS Star City Plus', 'city', 'Specialized', 'Sirrus 2.0', 2023,
        90, 560, 'Hyderabad', 4.6, 51,
        'Fitness city bike with lightweight alloy frame and Body Geometry saddle.',
        ['Alloy Frame', 'Shimano Altus 16sp', 'Disc Brakes', 'Carbon Fork', 'Body Geometry Saddle'],
        'https://imgd.aeplcdn.com/1280x720/n/cw/ec/211699/star-city-right-front-three-quarter.jpeg?isig=0',
        vendor_id,
    ),
    (
        'Bajaj CT 110', 'city', 'Scott', 'Sub Sport 30', 2024,
        85, 530, 'Chennai', 4.5, 36,
        'Sporty urban bike with light alloy frame, disc brakes and 27-speed drivetrain.',
        ['Alloy Frame', '700C Wheels', 'Shimano 27sp', 'Disc Brakes', 'Ergonomic Grips'],
        'https://imgd.aeplcdn.com/664x374/n/wg0nigb_1845510.jpg?q=80',
        vendor2_id,
    ),
    (
        'Honda SP 125', 'city', 'Raleigh', 'Strada 2', 2023,
        60, 380, 'Kolkata', 4.3, 27,
        'Classic city commuter with comfortable upright geometry and practical mudguards.',
        ['700C Wheels', 'Alloy Frame', '14-Speed Shimano', 'V-Brakes', 'Mudguards'],
        'https://images.openai.com/static-rsc-4/t7-zoiPLjNSo4JZZOmlSMVbh6Ee9yWXMxOFTZcFPzGZvtEh2lcHXYIPBlIoAKkjNdLec3ED-aPXbhmoOVwsFnxXu3ErWt3OV5rROyePWmQLnrT1cJATuXuR4EffzMwnK4McWU5V2kq7FHSgRsQpcR7oaP5B8JXtOdzozmhuFPrEmWGmA5KuKwl_7DJylYKgW?purpose=fullsize',
        vendor_id,
    ),
    (
        'TVS Apache RTR 160', 'city', 'Hero', 'Sprint Rapid', 2023,
        55, 350, 'Jaipur', 4.2, 19,
        'Affordable and reliable 21-speed city bike with front suspension for daily commutes.',
        ['26" Wheels', 'Alloy Frame', '21-Speed Shimano', 'Front Suspension', 'V-Brakes'],
        'https://images.openai.com/static-rsc-4/jvAoszcR5NqsJh-_DbWZ_LyFcheCvMPF-OcLm2UEsCmI0XhkFVxNn8sQlVMPu39mgHFa_Y6mPpAoO3cI4qBjsDudmooP4JgzbU4lB-JH6x6-og6h1AC7yIOfCHr03z-HzWDxpkNWz2UikkGdFzvm3CYnjjV9ze4NfMY8h8e1p94TlhMTiOrdYNqFjktj-gst?purpose=fullsize',
        vendor2_id,
    ),
    (
        'Yamaha FZ-S FI', 'city', 'Cannondale', 'Quick 5', 2024,
        88, 550, 'Bangalore', 4.6, 48,
        'Snappy urban fitness bike with smooth ride quality and quick handling.',
        ['SmartForm Alloy', '700C Wheels', 'Shimano Altus 21sp', 'Disc Brakes', 'Flat Bar'],
        'https://images.openai.com/static-rsc-4/NpoaqhP3F00g38UZG-gKm_sURy3PDtZ5HyVXDpxrgOsY0DProcucSliEh8WmAqLpcC91jz4wl9-THWZDuR9ixJYciNhpK2JwbHwPX0h_vhgJUNibXOgpGJUs1mwOSJugqdeaAGt6kqBbA3HHR7343_HCnkXPKSc653d_ea29ovGUy-2tVA4AGsl0179MQ2lW?purpose=fullsize',
        vendor_id,
    ),
    # ═══════════════════════════════════════════════
    # HYBRID BIKES  (10 bikes)
    # ═══════════════════════════════════════════════
   (
        'Yamaha FZ-S Fi Hybrid', 'hybrid', 'Yamaha ', 'Dual Sport 3', 2024,
        105, 660, 'Hyderabad', 4.7, 63,
        'Versatile hybrid built for trails and tarmac with suspension fork and disc brakes.',
        ['700C / 27.5" Wheels', 'Suspension Fork', 'Shimano Deore 10sp', 'Disc Brakes', 'Adjustable Stem'],
        'https://images.openai.com/static-rsc-4/G5Z96Cnaw8YtBwjY0OIu_VjbAiPircSL978FkpiRjoyOiICoSDg6bMmq7A4QE9Duqu9qeogmyHNbSKCsNBYLzB93R_DTq2U2JqWXUXozN8eV4RMcoeNbKnNQYvbn4wYYVCn1813N7cOTGeUnMz33R91sSpAHGFbtz8yK65Zk1g9DlRUMO_ccSzrULZEbZbmX?purpose=fullsize',
        vendor_id,
    ),
    (
        'TVS Raider 125', 'hybrid', 'TVS', 'Roam 2 Disc', 2023,
        85, 530, 'Bangalore', 4.5, 37,
        'Comfortable all-road hybrid with 700C wheels and 24-speed drivetrain.',
        ['700C Wheels', 'ALUXX Alloy', 'Shimano 24sp', 'Disc Brakes', 'Comfort Saddle'],
        'https://imgd.aeplcdn.com/1280x720/n/cw/ec/1/versions/tvs-raider-125-drum1741766352464.jpg',
        vendor2_id,
    ),
    (
        'Honda SP160', 'hybrid', 'Honda', 'Crosstrail Sport', 2024,
        115, 720, 'Mumbai', 4.7, 55,
        'Sport hybrid for trail and urban riders with Body Geometry contact points.',
        ['29" Wheels', 'SR Suntour Fork', 'SRAM NX 10sp', 'Disc Brakes', 'Body Geometry Saddle'],
        'https://imgd.aeplcdn.com/1280x720/n/cw/ec/154781/sp160-right-side-view-11.png?isig=0',
        vendor_id,
    ),
    (
        'Bajaj Pulsar N160', 'hybrid', 'Bajaj motor', 'Quick CX 3', 2023,
        100, 640, 'Delhi', 4.6, 42,
        'Cyclocross-inspired hybrid that handles gravel, trails and city streets with ease.',
        ['700C x 38mm Tyres', 'SmartForm Alloy', 'Shimano 24sp', 'Disc Brakes', 'Flat Bar'],
        'https://images.openai.com/static-rsc-4/J2h066HcwTA2Xfq45J0oGqnT4WKyWRQDh4M3eCn42sAJezk8Q7oS8b7QYLTtLVyEiHjFUr8YUYWMkhaQBW6Ek3Tyju73Of5Ak-xdAB2sQ0fpEaWSp1MLlVzJ2s1DJMBMlVqAh49Ar5fctFhWTlB-tbS0zFDm-NqzuERzGUwGgokvfg-KV6h5snzZTZRq-fe5?purpose=fullsize',
        vendor2_id,
    ),
    (
        'Hero Splendor Plus XTEC', 'hybrid', 'Hero Motor', 'Sportster 20', 2024,
        90, 570, 'Pune', 4.5, 31,
        'Lightweight alloy hybrid with confident handling for fitness and leisure rides.',
        ['700C Wheels', 'Alloy Frame', 'Shimano Altus 21sp', 'Hydraulic Disc', 'Suspension Fork'],
        'https://images.openai.com/static-rsc-4/JVdcNuWBtb7X96LZiYeuMnAPwaOedRdw-c2UEAppTUHfGAN2_dLdd_26neS73I2BOdSXmjaO_Yz_SEIN47kH6066UTW9uGHTVMS4-2NIMs5V1nLi9mlqMXa8I3FCU2brxRXer3NWvmiI5P9eCHzWnITbSTqXBWuBhfPfIVGSpr2S6RmBQ-jxthVH6a87Ph9U?purpose=fullsize',
        vendor_id,
    ),
    (
        'TVS Apache RTR 160 4V', 'hybrid', 'TVS Motor', 'Tarmac 21S', 2023,
        78, 490, 'Chennai', 4.4, 26,
        'Practical hybrid for daily commuters with reliable shifting and comfortable seating.',
        ['700C Wheels', 'Alloy Frame', '21-Speed Shimano', 'Disc Brakes', 'Ergonomic Saddle'],
        'https://images.openai.com/static-rsc-4/2ehOvsHrdcN58BYf8GM9OMtDuLr9cX5Acf1iKtOm6I1mPRnHnjWXIJHbpSEjMofZH-GylDzV9-wdmrHv8dB5QymzKxvL_AfCuHFCb0Px-S5dK49OTVbnAMR6mjQmRBsigMlBoXMSDV0xqPh988stC0icjNyDhuO6YJheaXueE8a4RigtAxv58cUGALLwjPI-?purpose=fullsize',
        vendor2_id,
    ),
    (
        'Honda Hornet Hybrid e:HEV', 'hybrid', 'Honda', 'Riverside 500', 2024,
        95, 600, 'Hyderabad', 4.6, 40,
        'Adventure hybrid designed for light touring with wide tyres and rack mounts.',
        ['700C x 40mm Tyres', 'Alloy Frame', 'Shimano 21sp', 'Hydraulic Disc', 'Rack Mounts'],
        'https://imgd.aeplcdn.com/1056x594/n/5ib9hgb_1844282.png?q=80',
        vendor_id,
    ),
    (
        'Yamaha Tracer 9 HY', 'hybrid', 'Yamaha Motor', 'Sprint Triton', 2023,
        72, 460, 'Kolkata', 4.3, 17,
        'Budget hybrid with front suspension for everyday mixed-terrain commutes.',
        ['700C Wheels', 'Alloy Frame', '21-Speed Shimano', 'Suspension Fork', 'V-Brakes'],
        'https://imgd.aeplcdn.com/642x361/n/cw/ec/97045/right-front-three-quarter3.jpeg?q=75',
        vendor2_id,
    ),
    (
        'Hero MotoCorp Vida VXZ', 'hybrid', 'Hero Motor', 'Crossway 40', 2024,
        110, 700, 'Mumbai', 4.6, 35,
        'Smooth hybrid with lightweight frame and Shimano 24-speed for urban adventures.',
        ['700C Wheels', 'Lite Alloy Frame', 'Shimano Altus 24sp', 'Disc Brakes', 'SR Suntour Fork'],
        'https://eauto.co.in/cdn/shop/articles/19-01-2026image_1768795311944_800x.jpg?v=1768795388',
        vendor_id,
    ),
    (
        'Yamaha MT-15 (smart efficiency tech)', 'hybrid', 'Yamaha', 'Misceo 2', 2023,
        82, 520, 'Bangalore', 4.4, 23,
        'Classic hybrid cruiser with comfortable geometry and quality components for easy rides.',
        ['700C Wheels', 'Alloy Frame', 'Shimano Acera 21sp', 'Disc Brakes', 'Comfort Saddle'],
        'https://imgd.aeplcdn.com/664x374/n/cw/ec/1/versions/yamaha-mt-15-standard-20241759582770305.jpg?q=80',
        vendor2_id,
    ),
]

bike_ids = []
for row in BIKES:
    (name, typ, brand, model, year, pph, ppd,
     loc, rating, revs, desc, feats, img, vid) = row
    b = bike_schema(str(vid), name, typ, brand, model, year, pph, ppd, loc, desc, img)
    b['features']       = feats
    b['rating']         = rating
    b['total_reviews']  = revs
    b['total_bookings'] = revs // 3
    r = db.bikes.insert_one(b)
    bike_ids.append(r.inserted_id)
    print(f'   [{typ:8s}]  {name}  —  ₹{pph}/hr  |  {loc}')

# Convenience references for bookings/reviews
mountain_bikes = [bid for bid, row in zip(bike_ids, BIKES) if row[1] == 'mountain']
road_bikes     = [bid for bid, row in zip(bike_ids, BIKES) if row[1] == 'road']
electric_bikes = [bid for bid, row in zip(bike_ids, BIKES) if row[1] == 'electric']
city_bikes     = [bid for bid, row in zip(bike_ids, BIKES) if row[1] == 'city']
hybrid_bikes   = [bid for bid, row in zip(bike_ids, BIKES) if row[1] == 'hybrid']

# ── Bookings ───────────────────────────────────────────────────────
print('\n📅  Seeding bookings...')
now = datetime.utcnow()

BOOKINGS_DEF = [
    # (user_id, bike_id, day_offset, hours, status, pay_status)
    (rohan_id,  mountain_bikes[0],   -5,  8,  'completed', 'paid'),
    (rohan_id,  road_bikes[0],        2, 24,  'confirmed', 'paid'),
    (priya_id,  electric_bikes[0],    7,  3,  'pending',   'unpaid'),
    (arjun_id,  city_bikes[0],       10,  4,  'pending',   'unpaid'),
    (vikram_id, hybrid_bikes[0],     -2,  6,  'completed', 'paid'),
    (kavya_id,  mountain_bikes[1],    1, 12,  'confirmed', 'paid'),
    (aditya_id, electric_bikes[1],    3,  5,  'pending',   'unpaid'),
    (rohan_id,  road_bikes[2],       -8,  4,  'completed', 'paid'),
]

bk_ids = []
for uid, bid, day_off, hrs, status, pay_status in BOOKINGS_DEF:
    start = now + timedelta(days=day_off)
    end   = start + timedelta(hours=hrs)
    bike  = db.bikes.find_one({'_id': bid})
    amt   = hrs * bike['price_per_hour'] if hrs < 24 else bike['price_per_day']
    bk = booking_schema(
        str(uid), str(bid), str(vendor_id),
        start, end, hrs, amt, 'Demo Pickup Location'
    )
    bk['status']         = status
    bk['payment_status'] = pay_status
    r = db.bookings.insert_one(bk)
    bk_ids.append(r.inserted_id)
    print(f'   {status:10s}  Rs.{amt:.0f}  ({hrs}h)')

# ── Payments ───────────────────────────────────────────────────────
print('\n💳  Seeding payments...')
for i, (bk_id, row) in enumerate(zip(bk_ids, BOOKINGS_DEF)):
    if row[5] == 'paid':
        bk  = db.bookings.find_one({'_id': bk_id})
        pmt = payment_schema(str(bk_id), bk['user_id'], bk['total_amount'], 'card')
        pmt['status']         = 'success'
        pmt['transaction_id'] = f'SEED{i:04d}TXNABC{i * 1337:06d}'
        r = db.payments.insert_one(pmt)
        db.bookings.update_one(
            {'_id': bk_id},
            {'$set': {'payment_id': str(r.inserted_id), 'payment_status': 'paid'}}
        )
        print(f'   Rs.{bk["total_amount"]:.0f}  ->  {pmt["transaction_id"]}')

# ── Reviews ────────────────────────────────────────────────────────
print('\n⭐  Seeding reviews...')
REVIEWS = [
    (rohan_id,  mountain_bikes[0], bk_ids[0], 5, 'Absolutely loved the Trek X-Caliber! Smooth ride, excellent brakes. Perfect for Banjara Hills trails.'),
    (vikram_id, mountain_bikes[0], bk_ids[4], 4, 'Great mountain bike, well maintained. Slightly heavy for steep climbs but handles trails beautifully.'),
    (rohan_id,  electric_bikes[0], bk_ids[0], 5, 'Electric bike is a game changer! Battery lasted the entire day. Glided through Hyderabad traffic silently.'),
    (kavya_id,  mountain_bikes[1], bk_ids[5], 5, 'The Scott Scale is phenomenal. Full suspension made the rough trail feel like nothing. Highly recommend!'),
    (vikram_id, hybrid_bikes[0],   bk_ids[4], 4, 'Trek Dual Sport handled city roads and park paths equally well. Great versatile bike.'),
    (rohan_id,  road_bikes[2],     bk_ids[7], 5, 'BMC Teammachine felt like a pro machine. Spotless condition, fast and responsive. Will rent again!'),
    (arjun_id,  city_bikes[0],     bk_ids[3], 4, 'Hero Lectro E5 was perfect for my city commute. Comfortable saddle and the assist modes are great.'),
    (aditya_id, electric_bikes[1], bk_ids[6], 4, 'Trek Allant+ is powerful and well built. Bosch motor is silent and torquey. Excellent city cruiser.'),
]

for uid, bid, bkid, rating, comment in REVIEWS:
    rev = review_schema(str(uid), str(bid), str(bkid), rating, comment)
    db.reviews.insert_one(rev)
    print(f'   {rating}★  on {str(bid)[-8:]}...')

# ── Summary ────────────────────────────────────────────────────────
u_cnt  = db.users.count_documents({})
b_cnt  = db.bikes.count_documents({})
bk_cnt = db.bookings.count_documents({})
rv_cnt = db.reviews.count_documents({})
pm_cnt = db.payments.count_documents({})

mtb_cnt = db.bikes.count_documents({'type': 'mountain'})
rod_cnt = db.bikes.count_documents({'type': 'road'})
ele_cnt = db.bikes.count_documents({'type': 'electric'})
cty_cnt = db.bikes.count_documents({'type': 'city'})
hyb_cnt = db.bikes.count_documents({'type': 'hybrid'})

print(f"""
╔══════════════════════════════════════════════════════════╗
║         MongoDB Atlas Seeded Successfully!               ║
╠══════════════════════════════════════════════════════════╣
║  users        : {u_cnt:>3}                                       ║
║  bikes        : {b_cnt:>3}  ({mtb_cnt} mountain · {rod_cnt} road · {ele_cnt} electric     ║
║                      {cty_cnt} city · {hyb_cnt} hybrid)                   ║
║  bookings     : {bk_cnt:>3}                                       ║
║  reviews      : {rv_cnt:>3}                                       ║
║  payments     : {pm_cnt:>3}                                       ║
╠══════════════════════════════════════════════════════════╣
║  LOGIN CREDENTIALS:                                      ║
║  Admin  : admin@rentbike.in   /  admin123                ║
║  Vendor : vendor@rentbike.in  /  vendor123               ║
║  Vendor : meera@rentbike.in   /  vendor123               ║
║  User   : rohan@example.com   /  user123                 ║
║  User   : arjun@example.com   /  user123                 ║
║  User   : vikram@example.com  /  user123                 ║
╠══════════════════════════════════════════════════════════╣
║  Run the API:  cd backend && python app.py               ║
╚══════════════════════════════════════════════════════════╝
""")