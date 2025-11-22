import RPi.GPIO as GPIO
import time
import firebase_admin
from firebase_admin import credentials, db

# ---------------------------
#  Firebase Config
# ---------------------------
cred = credentials.Certificate("serviceAccountKey.json")
firebase_admin.initialize_app(cred, {
    "databaseURL": "https://tongsampah-fb84c-default-rtdb.firebaseio.com/"
})

# ---------------------------
# Sensor Setup (organik, anorganik, B3)
# ---------------------------
GPIO.setmode(GPIO.BCM)

sensors = [
    {"trig": 23, "echo": 24, "firebase_key": "organik"},
    {"trig": 17, "echo": 27, "firebase_key": "anorganik"},
    {"trig": 5,  "echo": 6,  "firebase_key": "B3"},
]

for s in sensors:
    GPIO.setup(s["trig"], GPIO.OUT)
    GPIO.setup(s["echo"], GPIO.IN)

# ---------------------------
# Baca jarak ultrasonik
# ---------------------------
def get_distance(trig, echo):
    GPIO.output(trig, False)
    time.sleep(0.05)

    GPIO.output(trig, True)
    time.sleep(0.00001)
    GPIO.output(trig, False)

    while GPIO.input(echo) == 0:
        pulse_start = time.time()

    while GPIO.input(echo) == 1:
        pulse_end = time.time()

    pulse_duration = pulse_end - pulse_start
    distance = pulse_duration * 17150
    return round(distance, 2)

# ---------------------------
# Loop utama
# ---------------------------
try:
    while True:
        data = {}

        for s in sensors:
            jarak = get_distance(s["trig"], s["echo"])
            data[s["firebase_key"]] = jarak
            print(f"{s['firebase_key']}: {jarak} cm")

        # kirim ke Firebase
        ref = db.reference("/Tongsampah1")
        ref.set(data)

        print("Terkirim:", data)
        print("--------------------------------")
        time.sleep(1)

except KeyboardInterrupt:
    GPIO.cleanup()
    print("Program dihentikan")
