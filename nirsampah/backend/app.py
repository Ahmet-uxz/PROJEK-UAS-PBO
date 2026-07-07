import os
from functools import wraps
from flask import Flask, render_template, request, redirect, url_for, session, flash
import requests as http_requests

from models import WasteClassifier, Database, PickupRequest, User

BASE_DIR     = os.path.dirname(os.path.abspath(__file__))
PROJECT_ROOT = os.path.dirname(BASE_DIR)
FRONTEND_DIR = os.path.join(PROJECT_ROOT, "frontend")
TEMPLATE_DIR = os.path.join(FRONTEND_DIR, "templates")
STATIC_DIR   = os.path.join(FRONTEND_DIR, "static")
DB_PATH      = os.path.join(PROJECT_ROOT, "database.db")

app = Flask(__name__, template_folder=TEMPLATE_DIR, static_folder=STATIC_DIR)
app.secret_key = "swc-secret-key-2025-ganti-ini-di-produksi"
db  = Database(DB_PATH)


# AUTH HELPERS
def login_required(f):
    @wraps(f)
    def decorated(*args, **kwargs):
        if "user_id" not in session:
            flash("Silakan login terlebih dahulu.", "warning")
            return redirect(url_for("login"))
        return f(*args, **kwargs)
    return decorated

def current_user():
    if "user_id" in session:
        return User.get_by_id(db, session["user_id"])
    return None

# Inject current_user ke semua template
@app.context_processor
def inject_user():
    return {"current_user": current_user()}


# HOME
@app.route("/")
def home():
    return render_template("home.html")


# AUTH: REGISTER
@app.route("/register", methods=["GET","POST"])
def register():
    if "user_id" in session:
        return redirect(url_for("home"))

    error = None
    form_data = {}

    if request.method == "POST":
        username = request.form.get("username","").strip()
        email    = request.form.get("email","").strip()
        password = request.form.get("password","")
        confirm  = request.form.get("confirm_password","")
        form_data = {"username": username, "email": email}

        if not all([username, email, password, confirm]):
            error = "Semua field wajib diisi."
        elif len(username) < 3:
            error = "Username minimal 3 karakter."
        elif len(password) < 6:
            error = "Password minimal 6 karakter."
        elif password != confirm:
            error = "Konfirmasi password tidak cocok."
        else:
            user = User(username, email)
            user.set_password(password)
            success, msg = user.register(db)
            if success:
                session["user_id"]  = user.get_user_id()
                session["username"] = user.get_username()
                flash("Registrasi berhasil! Selamat datang.", "success")
                return redirect(url_for("home"))
            else:
                error = msg

    return render_template("auth/register.html", error=error, form_data=form_data)


# AUTH: LOGIN
@app.route("/login", methods=["GET","POST"])
def login():
    if "user_id" in session:
        return redirect(url_for("home"))

    error = None
    username_val = ""

    if request.method == "POST":
        username     = request.form.get("username","").strip()
        password     = request.form.get("password","")
        username_val = username

        if not username or not password:
            error = "Username dan password wajib diisi."
        else:
            user = User(username, "")
            if user.login(db, password):
                session["user_id"]  = user.get_user_id()
                session["username"] = user.get_username()
                flash(f"Selamat datang kembali, {user.get_username()}!", "success")
                next_page = request.args.get("next")
                return redirect(next_page or url_for("home"))
            else:
                error = "Username atau password salah."

    return render_template("auth/login.html", error=error, username_val=username_val)


# AUTH: LOGOUT
@app.route("/logout")
def logout():
    session.clear()
    flash("Kamu telah berhasil logout.", "info")
    return redirect(url_for("home"))


# KLASIFIKASI SAMPAH
@app.route("/classify", methods=["GET","POST"])
def classify():
    result, error, waste_name_input = None, None, ""

    if request.method == "POST":
        waste_name_input = request.form.get("waste_name","").strip()
        if not waste_name_input:
            error = "Nama sampah tidak boleh kosong."
        else:
            waste_obj = WasteClassifier.classify(waste_name_input)
            if waste_obj is None:
                error = f"Sampah '{waste_name_input}' tidak dikenali. Coba masukkan nama sampah yang lebih spesifik, contoh: Botol Plastik, Kulit Pisang, atau Baterai Bekas."
            else:
                db.save_classification(waste_obj)
                result = {
                    "name":        waste_obj.get_name(),
                    "category":    waste_obj.get_category(),
                    "description": waste_obj.get_description(),
                    "handling":    waste_obj.get_handling(),
                }

    history = db.get_history(10)
    return render_template("classify.html", result=result, error=error,
                           waste_name_input=waste_name_input, history=history)


# CARI TPS
@app.route("/tps", methods=["GET","POST"])
def tps():
    locations, error, city_input = [], None, ""

    if request.method == "POST":
        city_input = request.form.get("city","").strip()
        if not city_input:
            error = "Nama kota tidak boleh kosong."
        else:
            try:
                locations, error = search_tps_nominatim(city_input)
            except http_requests.exceptions.ConnectionError:
                error = "Gagal terhubung ke server API. Periksa koneksi internet."
            except http_requests.exceptions.Timeout:
                error = "Permintaan ke API melebihi batas waktu."
            except Exception as exc:
                error = f"Terjadi kesalahan: {exc}"

    return render_template("tps.html", locations=locations, error=error, city_input=city_input)


def search_tps_nominatim(city_input):
    headers = {"User-Agent": "SmartWasteClassifier/1.0"}
    queries = [
        f"tempat pembuangan sampah {city_input}",
        f"TPS {city_input}",
        f"waste disposal {city_input}",
        f"recycling {city_input}",
        city_input,
    ]
    for query in queries:
        resp = http_requests.get(
            "https://nominatim.openstreetmap.org/search",
            params={"q": query, "format": "json", "addressdetails": 1, "limit": 10},
            headers=headers, timeout=10,
        )
        resp.raise_for_status()
        locations = []
        for item in resp.json():
            try:
                lat = float(item["lat"]); lon = float(item["lon"])
            except: continue
            address = item.get("display_name","-")
            locations.append({
                "name":      item.get("name") or address.split(",")[0],
                "address":   address,
                "latitude":  lat,
                "longitude": lon,
            })
        if locations:
            if query == city_input:
                return locations, (f"Data TPS spesifik untuk '{city_input}' belum tersedia di OpenStreetMap. "
                                   f"Menampilkan titik lokasi kota sebagai referensi.")
            return locations, None
    return [], f"Tidak ditemukan TPS di kota '{city_input}'."


# JADWAL PENGANGKUTAN
@app.route("/schedule", methods=["GET","POST"])
def schedule():
    schedules, wilayah_input = [], ""
    all_wilayah = db.get_all_wilayah()

    if request.method == "POST":
        wilayah_input = request.form.get("wilayah","").strip()
        if wilayah_input:
            schedules = db.get_schedule(wilayah_input)

    return render_template("schedule.html", schedules=schedules,
                           wilayah_input=wilayah_input, all_wilayah=all_wilayah)


# PENJEMPUTAN
@app.route("/pickup", methods=["GET","POST"])
@login_required
def pickup():
    success, error, new_request, form_data = None, None, None, {}
    user = current_user()

    if request.method == "POST":
        nama          = request.form.get("nama","").strip()
        alamat        = request.form.get("alamat","").strip()
        nomor_telepon = request.form.get("nomor_telepon","").strip()
        jenis_sampah  = request.form.get("jenis_sampah","").strip()
        jadwal        = request.form.get("jadwal","").strip()
        form_data = {"nama":nama,"alamat":alamat,"nomor_telepon":nomor_telepon,
                     "jenis_sampah":jenis_sampah,"jadwal":jadwal}

        if not all([nama,alamat,nomor_telepon,jenis_sampah,jadwal]):
            error = "Semua field wajib diisi."
        elif len(nomor_telepon)<8 or not nomor_telepon.replace("+","").replace("-","").isdigit():
            error = "Nomor telepon tidak valid (min. 8 digit)."
        else:
            pickup_obj = PickupRequest(nama, alamat, nomor_telepon, jenis_sampah, jadwal,
                                       user_id=user.get_user_id())
            rid        = pickup_obj.create_request(db)
            new_request= PickupRequest.get_request(db, rid)
            success    = f"Permintaan penjemputan berhasil diajukan! ID: #{rid}"
            form_data  = {}

    # Pengguna hanya lihat permintaan milik sendiri
    my_requests = db.get_pickup_requests_by_user(user.get_user_id())

    return render_template("pickup.html",
        success=success, error=error,
        new_request=new_request.to_dict() if new_request else None,
        form_data=form_data,
        all_requests=my_requests,
        available_slots=PickupRequest.AVAILABLE_SLOTS,
        jenis_options=PickupRequest.JENIS_OPTIONS,
        status_flow=PickupRequest.STATUS_FLOW,
    )


@app.route("/pickup/update/<int:request_id>", methods=["POST"])
@login_required
def pickup_update(request_id):
    new_status = request.form.get("status","").strip()
    pickup_obj = PickupRequest.get_request(db, request_id)
    user       = current_user()
    if pickup_obj and pickup_obj.get_user_id() == user.get_user_id():
        pickup_obj.update_status(db, new_status)
    return redirect(url_for("pickup") + "#daftar-permintaan")


# TENTANG
@app.route("/about")
def about():
    return render_template("about.html")


if __name__ == "__main__":
    app.run(debug=True)
