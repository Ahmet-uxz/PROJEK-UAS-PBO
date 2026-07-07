import sqlite3
from datetime import datetime
from werkzeug.security import generate_password_hash, check_password_hash

# OOP: Inheritance, Encapsulation, Polymorphism

class Waste:
    def __init__(self, name: str):
        self.__name = name

    def get_name(self) -> str:      return self.__name
    def set_name(self, n: str):     self.__name = n
    def get_category(self) -> str:  return "Tidak Diketahui"
    def get_description(self) -> str: return "Tidak ada deskripsi."
    def get_handling(self) -> str:  return "Tidak ada panduan penanganan."
    def __repr__(self):             return f"<Waste name='{self.__name}' category='{self.get_category()}'>"


class OrganicWaste(Waste):
    def __init__(self, name): super().__init__(name)
    def get_category(self):    return "Organik"
    def get_description(self): return "Dapat terurai secara alami oleh mikroorganisme di dalam tanah."
    def get_handling(self):
        return ("Dapat dijadikan kompos atau pupuk organik. "
                "Pisahkan dari sampah anorganik dan masukkan ke tempat sampah hijau. "
                "Hindari mencampur dengan sampah B3 agar proses penguraian berjalan optimal.")


class InorganicWaste(Waste):
    def __init__(self, name): super().__init__(name)
    def get_category(self):    return "Anorganik"
    def get_description(self): return "Sulit terurai secara alami dan membutuhkan waktu ratusan tahun."
    def get_handling(self):
        return ("Dapat didaur ulang dan dipisahkan dari sampah organik. "
                "Kumpulkan di tempat sampah kuning dan serahkan ke bank sampah atau pengepul. "
                "Beberapa jenis anorganik seperti plastik dapat dikonversi menjadi bahan bakar.")


class HazardousWaste(Waste):
    def __init__(self, name): super().__init__(name)
    def get_category(self):    return "B3 (Bahan Berbahaya & Beracun)"
    def get_description(self): return "Mengandung zat berbahaya yang dapat merusak lingkungan dan kesehatan manusia."
    def get_handling(self):
        return ("Memerlukan penanganan khusus oleh pihak berwenang. "
                "Jangan buang sembarangan! Serahkan ke fasilitas pengelolaan limbah B3 resmi. "
                "Simpan dalam wadah tertutup rapat dan beri label yang jelas sebelum diserahkan.")


class WasteClassifier:
    ORGANIC_KEYWORDS = [
        "pisang","apel","jeruk","mangga","nanas","semangka","melon","tomat","wortel",
        "bayam","kangkung","singkong","ubi","kulit","daun","ranting","bunga","rumput",
        "sayur","buah","nasi","roti","daging","ikan","telur","susu","keju","ampas",
        "kotoran","pupuk","dedaunan","kayu","bambu","sisa makanan","cangkang telur",
        "teh","kopi","tulang","cumi","udang","kepiting","kerang","sisa","makanan",
        "pepaya","durian","salak","jambu","anggur","alpukat","leci","kurma","kiwi",
        "kubis","brokoli","labu","jagung","kacang","tempe","tahu","oncom","tauge",
        "seledri","bawang","jahe","kunyit","lengkuas","sereh","daun pisang","pelepah",
        "sekam","jerami","serbuk kayu","kotoran hewan","sisa sayur","sisa buah",
    ]

    HAZARDOUS_KEYWORDS = [
        "baterai","aki","accu","cat","thinner","bensin","solar","oli","minyak bekas",
        "racun","pestisida","herbisida","obat","jarum suntik","syringe","termometer",
        "merkuri","lampu neon","lampu led rusak","lampu fluorescent","kimia","asam",
        "basa","deterjen","pemutih","bayclin","bahan kimia","limbah medis","limbah industri",
        "kaleng cat","spray","aerosol","tabung gas","gas elpiji","gas lpg","gas bocor","elektronik rusak","hp rusak",
        "laptop rusak","tv rusak","tinta printer","cartridge","toner","solvent",
        "korek api","lilin","cairan pembersih","antiseptik","disinfektan","formalin",
        "alkohol","spiritus","minyak tanah","bahan bakar","sisa obat","kadaluarsa",
        "beracun","berbahaya","radioaktif","bahan peledak","pupuk kimia","insektisida",
    ]

    INORGANIC_KEYWORDS = [
        "plastik","botol plastik","kantong plastik","sedotan","styrofoam","ember plastik",
        "baskom","toples","wadah plastik","pipa plastik","selang","karet","ban",
        "kertas","koran","majalah","buku","kardus","karton","dus","tissue","pampers",
        "popok","pembalut","kotak","amplop","struk","nota","kalender",
        "kaleng","besi","baja","aluminium","tembaga","seng","paku","kawat","kunci",
        "sendok","garpu","pisau","wajan","panci","spatula","gunting","jarum",
        "logam","metal","baut","mur","engsel","rantai","kabel","tembaga",
        "kaca","gelas","botol kaca","cermin","jendela","piring","mangkok","toples kaca",
        "baju","celana","kaos","kemeja","jaket","sepatu","sandal","tas","dompet",
        "kain","tekstil","benang","karpet","tikar","bantal","kasur","selimut",
        "charger","kabel","headset","earphone","mouse","keyboard","remote","lampu",
        "styrofoam","gabus","busa","spons","sikat","sapu","pel","ember",
        "ember","balon","mainan","boneka","helm","payung","tali","tambang",
    ]

    @classmethod
    def classify(cls, waste_name: str) -> "Waste | None":
        """
        Mengklasifikasikan nama sampah.
        Return objek Waste jika dikenali, None jika tidak dikenali.
        """
        name_lower = waste_name.lower().strip()

        for keyword in cls.HAZARDOUS_KEYWORDS:
            if keyword in name_lower:
                return HazardousWaste(waste_name)

        for keyword in cls.ORGANIC_KEYWORDS:
            if keyword in name_lower:
                return OrganicWaste(waste_name)

        for keyword in cls.INORGANIC_KEYWORDS:
            if keyword in name_lower:
                return InorganicWaste(waste_name)

        # Tidak cocok dengan keyword manapun → tidak dikenali
        return None

# USER: class untuk autentikasi pengguna
class User:
    """
    Class untuk mengelola data dan autentikasi pengguna.

    Encapsulation: semua atribut private (__username, __email, __password_hash).
    Method:
        register(db)        – daftarkan user baru ke database
        login(db, password) – verifikasi password, return True jika cocok
        get_by_username(db) – class method, ambil user dari DB berdasarkan username
        get_by_id(db, id)   – class method, ambil user dari DB berdasarkan id
    """

    def __init__(self, username: str, email: str, password_hash: str = "", user_id: int = 0):
        self.__username      = username.strip().lower()
        self.__email         = email.strip().lower()
        self.__password_hash = password_hash
        self.__user_id       = user_id

    # Getters
    def get_username(self)      -> str: return self.__username
    def get_email(self)         -> str: return self.__email
    def get_user_id(self)       -> int: return self.__user_id
    def get_password_hash(self) -> str: return self.__password_hash

    def set_password(self, plain_password: str):
        """Hash dan simpan password (Encapsulation)."""
        self.__password_hash = generate_password_hash(plain_password)

    def check_password(self, plain_password: str) -> bool:
        """Verifikasi password dengan hash yang tersimpan."""
        return check_password_hash(self.__password_hash, plain_password)

    def register(self, db: "Database") -> tuple[bool, str]:
        """
        Daftarkan user baru ke database.
        Return (True, '') jika berhasil, (False, pesan_error) jika gagal.
        """
        existing = User.get_by_username(db, self.__username)
        if existing:
            return False, "Username sudah digunakan. Pilih username lain."

        existing_email = User.get_by_email(db, self.__email)
        if existing_email:
            return False, "Email sudah terdaftar. Gunakan email lain."

        conn = db._get_connection()
        cursor = conn.execute(
            "INSERT INTO users (username, email, password_hash, created_at) VALUES (?,?,?,?)",
            (self.__username, self.__email, self.__password_hash,
             datetime.now().strftime("%Y-%m-%d %H:%M:%S")),
        )
        conn.commit()
        self.__user_id = cursor.lastrowid
        conn.close()
        return True, ""

    def login(self, db: "Database", plain_password: str) -> bool:
        """
        Verifikasi login. Return True jika username ada dan password cocok.
        """
        user = User.get_by_username(db, self.__username)
        if not user:
            return False
        if user.check_password(plain_password):
            self.__user_id       = user.get_user_id()
            self.__email         = user.get_email()
            self.__password_hash = user.get_password_hash()
            return True
        return False

    @classmethod
    def get_by_username(cls, db: "Database", username: str) -> "User | None":
        conn = db._get_connection()
        row  = conn.execute(
            "SELECT * FROM users WHERE username = ?", (username.lower(),)
        ).fetchone()
        conn.close()
        if not row: return None
        return cls(row["username"], row["email"], row["password_hash"], row["id"])

    @classmethod
    def get_by_email(cls, db: "Database", email: str) -> "User | None":
        conn = db._get_connection()
        row  = conn.execute(
            "SELECT * FROM users WHERE email = ?", (email.lower(),)
        ).fetchone()
        conn.close()
        if not row: return None
        return cls(row["username"], row["email"], row["password_hash"], row["id"])

    @classmethod
    def get_by_id(cls, db: "Database", user_id: int) -> "User | None":
        conn = db._get_connection()
        row  = conn.execute(
            "SELECT * FROM users WHERE id = ?", (user_id,)
        ).fetchone()
        conn.close()
        if not row: return None
        return cls(row["username"], row["email"], row["password_hash"], row["id"])

    def to_dict(self) -> dict:
        return {"id": self.__user_id, "username": self.__username, "email": self.__email}

    def __repr__(self):
        return f"<User id={self.__user_id} username='{self.__username}'>"

# PICKUP REQUEST
class PickupRequest:
    AVAILABLE_SLOTS = [
        "Senin, 08:00–12:00","Senin, 13:00–17:00",
        "Selasa, 08:00–12:00","Selasa, 13:00–17:00",
        "Rabu, 08:00–12:00","Rabu, 13:00–17:00",
        "Kamis, 08:00–12:00","Kamis, 13:00–17:00",
        "Jumat, 08:00–12:00","Jumat, 13:00–17:00",
        "Sabtu, 08:00–12:00","Sabtu, 13:00–17:00",
    ]
    JENIS_OPTIONS = ["Organik","Anorganik","B3 (Bahan Berbahaya & Beracun)","Campuran"]
    STATUS_FLOW   = ["Menunggu Konfirmasi","Dikonfirmasi","Dalam Penjemputan","Selesai"]

    def __init__(self, nama, alamat, nomor_telepon, jenis_sampah, jadwal,
                 status="Menunggu Konfirmasi", request_id=0, user_id=0):
        self.__nama          = nama.strip()
        self.__alamat        = alamat.strip()
        self.__nomor_telepon = nomor_telepon.strip()
        self.__jenis_sampah  = jenis_sampah.strip()
        self.__jadwal        = jadwal.strip()
        self.__status        = status
        self.__request_id    = request_id
        self.__user_id       = user_id

    def get_nama(self)          -> str: return self.__nama
    def get_alamat(self)        -> str: return self.__alamat
    def get_nomor_telepon(self) -> str: return self.__nomor_telepon
    def get_jenis_sampah(self)  -> str: return self.__jenis_sampah
    def get_jadwal(self)        -> str: return self.__jadwal
    def get_status(self)        -> str: return self.__status
    def get_request_id(self)    -> int: return self.__request_id
    def get_user_id(self)       -> int: return self.__user_id
    def set_status(self, s):           self.__status = s
    def set_request_id(self, rid):     self.__request_id = rid

    def create_request(self, db: "Database") -> int:
        new_id = db.save_pickup_request(self)
        self.__request_id = new_id
        return new_id

    @classmethod
    def get_request(cls, db: "Database", request_id: int) -> "PickupRequest | None":
        data = db.get_pickup_request(request_id)
        if not data: return None
        return cls(data["nama"], data["alamat"], data["nomor_telepon"],
                   data["jenis_sampah"], data["jadwal_penjemputan"],
                   data["status"], data["id"], data.get("user_id", 0))

    def update_status(self, db: "Database", new_status: str) -> bool:
        if self.__request_id == 0: return False
        success = db.update_pickup_status(self.__request_id, new_status)
        if success: self.__status = new_status
        return success

    def to_dict(self) -> dict:
        return {
            "id": self.__request_id, "nama": self.__nama,
            "alamat": self.__alamat, "nomor_telepon": self.__nomor_telepon,
            "jenis_sampah": self.__jenis_sampah,
            "jadwal_penjemputan": self.__jadwal, "status": self.__status,
            "user_id": self.__user_id,
        }

    def __repr__(self):
        return f"<PickupRequest id={self.__request_id} nama='{self.__nama}' status='{self.__status}'>"

# DATABASE
class Database:
    def __init__(self, db_path: str = "database.db"):
        self.db_path = db_path
        self._init_db()
        self._init_users()
        self._init_schedule()
        self._init_pickup()

    def _get_connection(self):
        conn = sqlite3.connect(self.db_path)
        conn.row_factory = sqlite3.Row
        return conn

    def _init_db(self):
        conn = self._get_connection()
        conn.execute("""
            CREATE TABLE IF NOT EXISTS history (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                waste_name TEXT NOT NULL, category TEXT NOT NULL,
                description TEXT NOT NULL, created_at TEXT NOT NULL
            )""")
        conn.commit(); conn.close()

    def _init_users(self):
        conn = self._get_connection()
        conn.execute("""
            CREATE TABLE IF NOT EXISTS users (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                username TEXT NOT NULL UNIQUE,
                email TEXT NOT NULL UNIQUE,
                password_hash TEXT NOT NULL,
                created_at TEXT NOT NULL
            )""")
        conn.commit(); conn.close()

    def save_classification(self, waste_obj: Waste) -> int:
        conn = self._get_connection()
        cursor = conn.execute(
            "INSERT INTO history (waste_name, category, description, created_at) VALUES (?,?,?,?)",
            (waste_obj.get_name(), waste_obj.get_category(), waste_obj.get_description(),
             datetime.now().strftime("%Y-%m-%d %H:%M:%S")),
        )
        conn.commit(); new_id = cursor.lastrowid; conn.close()
        return new_id

    def get_history(self, limit=20):
        conn = self._get_connection()
        rows = conn.execute("SELECT * FROM history ORDER BY id DESC LIMIT ?", (limit,)).fetchall()
        conn.close()
        return [dict(r) for r in rows]

    def _init_schedule(self):
        conn = self._get_connection()
        conn.execute("""
            CREATE TABLE IF NOT EXISTS schedule (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                wilayah TEXT NOT NULL, hari TEXT NOT NULL,
                jam_mulai TEXT NOT NULL, jam_selesai TEXT NOT NULL,
                jenis TEXT NOT NULL, keterangan TEXT
            )""")
        conn.commit()
        count = conn.execute("SELECT COUNT(*) FROM schedule").fetchone()[0]
        if count == 0:
            seed = [
                ("Sukabumi - Kota","Senin, Rabu, Jumat","05:30","08:30","Organik","Truk hijau, pisahkan dari anorganik"),
                ("Sukabumi - Kota","Selasa, Kamis","05:30","08:30","Anorganik","Truk kuning, siapkan dalam kantong terpisah"),
                ("Sukabumi - Kota","Sabtu","06:30","10:00","B3","Armada khusus B3, bungkus rapat & beri label"),
                ("Sukabumi - Cikole","Senin, Kamis","06:00","09:00","Organik","Truk hijau, pisahkan dari anorganik"),
                ("Sukabumi - Cikole","Selasa, Jumat","06:00","09:00","Anorganik","Truk kuning, siapkan dalam kantong terpisah"),
                ("Sukabumi - Cikole","Sabtu","07:00","10:00","B3","Armada khusus B3, bungkus rapat & beri label"),
                ("Sukabumi - Gunung Puyuh","Senin, Rabu","05:30","08:30","Organik","Truk hijau, pisahkan dari anorganik"),
                ("Sukabumi - Gunung Puyuh","Selasa, Kamis","05:30","08:30","Anorganik","Truk kuning, siapkan dalam kantong terpisah"),
                ("Sukabumi - Gunung Puyuh","Jumat","07:00","10:00","B3","Armada khusus B3, bungkus rapat & beri label"),
                ("Sukabumi - Warudoyong","Selasa, Jumat","06:00","09:00","Organik","Truk hijau, pisahkan dari anorganik"),
                ("Sukabumi - Warudoyong","Senin, Kamis","06:00","09:00","Anorganik","Truk kuning, siapkan dalam kantong terpisah"),
                ("Sukabumi - Warudoyong","Sabtu","07:30","10:30","B3","Armada khusus B3, bungkus rapat & beri label"),
                ("Sukabumi - Citamiang","Senin, Rabu, Sabtu","06:00","09:00","Organik","Truk hijau, pisahkan dari anorganik"),
                ("Sukabumi - Citamiang","Selasa, Kamis","06:00","09:00","Anorganik","Truk kuning, siapkan dalam kantong terpisah"),
                ("Sukabumi - Citamiang","Jumat","07:00","10:00","B3","Armada khusus B3, bungkus rapat & beri label"),
                ("Sukabumi - Baros","Rabu, Sabtu","05:30","08:30","Organik","Truk hijau, pisahkan dari anorganik"),
                ("Sukabumi - Baros","Senin, Jumat","05:30","08:30","Anorganik","Truk kuning, siapkan dalam kantong terpisah"),
                ("Sukabumi - Baros","Kamis","07:00","10:00","B3","Armada khusus B3, bungkus rapat & beri label"),
                ("Sukabumi - Lembursitu","Senin, Kamis","06:00","09:00","Organik","Truk hijau, pisahkan dari anorganik"),
                ("Sukabumi - Lembursitu","Selasa, Jumat","06:00","09:00","Anorganik","Truk kuning, siapkan dalam kantong terpisah"),
                ("Sukabumi - Lembursitu","Sabtu","07:30","10:30","B3","Armada khusus B3, bungkus rapat & beri label"),
                ("Sukabumi - Cibeureum","Selasa, Jumat","05:30","08:30","Organik","Truk hijau, pisahkan dari anorganik"),
                ("Sukabumi - Cibeureum","Senin, Rabu","05:30","08:30","Anorganik","Truk kuning, siapkan dalam kantong terpisah"),
                ("Sukabumi - Cibeureum","Sabtu","07:00","10:00","B3","Armada khusus B3, bungkus rapat & beri label"),
                ("Jakarta Pusat","Senin, Rabu, Jumat","06:00","09:00","Organik","Truk hijau, pisahkan dari anorganik"),
                ("Jakarta Pusat","Selasa, Kamis","06:00","09:00","Anorganik","Truk kuning, siapkan dalam kantong terpisah"),
                ("Jakarta Pusat","Sabtu","07:00","11:00","B3","Armada khusus B3, bungkus rapat & beri label"),
                ("Jakarta Selatan","Senin, Kamis","05:30","08:30","Organik","Truk hijau, pisahkan dari anorganik"),
                ("Jakarta Selatan","Selasa, Jumat","05:30","08:30","Anorganik","Truk kuning, siapkan dalam kantong terpisah"),
                ("Jakarta Selatan","Rabu","07:00","10:00","B3","Armada khusus B3, bungkus rapat & beri label"),
                ("Bandung","Senin, Rabu, Jumat","05:00","08:00","Organik","Truk hijau, pisahkan dari anorganik"),
                ("Bandung","Selasa, Kamis","05:00","08:00","Anorganik","Truk kuning, siapkan dalam kantong terpisah"),
                ("Bandung","Sabtu","06:00","10:00","B3","Armada khusus B3, bungkus rapat & beri label"),
                ("Surabaya","Senin, Kamis","05:30","08:30","Organik","Truk hijau, pisahkan dari anorganik"),
                ("Surabaya","Rabu, Sabtu","05:30","08:30","Anorganik","Truk kuning, siapkan dalam kantong terpisah"),
                ("Surabaya","Jumat","07:00","10:00","B3","Armada khusus B3, bungkus rapat & beri label"),
                ("Medan","Selasa, Jumat","06:00","09:00","Organik","Truk hijau, pisahkan dari anorganik"),
                ("Medan","Senin, Kamis","06:00","09:00","Anorganik","Truk kuning, siapkan dalam kantong terpisah"),
                ("Medan","Sabtu","07:00","10:00","B3","Armada khusus B3, bungkus rapat & beri label"),
                ("Yogyakarta","Senin, Rabu, Jumat","06:00","09:00","Organik","Truk hijau, pisahkan dari anorganik"),
                ("Yogyakarta","Selasa, Kamis","06:00","09:00","Anorganik","Truk kuning, siapkan dalam kantong terpisah"),
                ("Yogyakarta","Sabtu","07:00","11:00","B3","Armada khusus B3, bungkus rapat & beri label"),
            ]
            conn.executemany(
                "INSERT INTO schedule (wilayah,hari,jam_mulai,jam_selesai,jenis,keterangan) VALUES(?,?,?,?,?,?)",
                seed)
            conn.commit()
        conn.close()

    def get_all_wilayah(self):
        conn = self._get_connection()
        rows = conn.execute("SELECT DISTINCT wilayah FROM schedule").fetchall()
        conn.close()
        wl = [r[0] for r in rows]
        sukabumi = sorted(w for w in wl if w.startswith("Sukabumi"))
        lainnya  = sorted(w for w in wl if not w.startswith("Sukabumi"))
        return sukabumi + lainnya

    def get_schedule(self, wilayah: str):
        conn = self._get_connection()
        rows = conn.execute("SELECT * FROM schedule WHERE wilayah=? ORDER BY jenis,hari",(wilayah,)).fetchall()
        conn.close()
        return [dict(r) for r in rows]

    def _init_pickup(self):
        conn = self._get_connection()
        conn.execute("""
            CREATE TABLE IF NOT EXISTS pickup_requests (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                nama TEXT NOT NULL, alamat TEXT NOT NULL,
                nomor_telepon TEXT NOT NULL, jenis_sampah TEXT NOT NULL,
                jadwal_penjemputan TEXT NOT NULL,
                status TEXT NOT NULL DEFAULT 'Menunggu Konfirmasi',
                user_id INTEGER DEFAULT 0,
                created_at TEXT NOT NULL
            )""")
        conn.commit(); conn.close()

    def save_pickup_request(self, pickup_obj: PickupRequest) -> int:
        conn = self._get_connection()
        cursor = conn.execute(
            """INSERT INTO pickup_requests
               (nama,alamat,nomor_telepon,jenis_sampah,jadwal_penjemputan,status,user_id,created_at)
               VALUES(?,?,?,?,?,?,?,?)""",
            (pickup_obj.get_nama(), pickup_obj.get_alamat(), pickup_obj.get_nomor_telepon(),
             pickup_obj.get_jenis_sampah(), pickup_obj.get_jadwal(), pickup_obj.get_status(),
             pickup_obj.get_user_id(), datetime.now().strftime("%Y-%m-%d %H:%M:%S")),
        )
        conn.commit(); new_id = cursor.lastrowid; conn.close()
        return new_id

    def get_pickup_request(self, request_id: int) -> dict:
        conn = self._get_connection()
        row  = conn.execute("SELECT * FROM pickup_requests WHERE id=?",(request_id,)).fetchone()
        conn.close()
        return dict(row) if row else {}

    def get_all_pickup_requests(self, limit=50):
        conn = self._get_connection()
        rows = conn.execute("SELECT * FROM pickup_requests ORDER BY id DESC LIMIT ?",(limit,)).fetchall()
        conn.close()
        return [dict(r) for r in rows]

    def get_pickup_requests_by_user(self, user_id: int):
        conn = self._get_connection()
        rows = conn.execute(
            "SELECT * FROM pickup_requests WHERE user_id=? ORDER BY id DESC",(user_id,)
        ).fetchall()
        conn.close()
        return [dict(r) for r in rows]

    def update_pickup_status(self, request_id: int, new_status: str) -> bool:
        valid = {"Menunggu Konfirmasi","Dikonfirmasi","Dalam Penjemputan","Selesai","Dibatalkan"}
        if new_status not in valid: return False
        conn = self._get_connection()
        conn.execute("UPDATE pickup_requests SET status=? WHERE id=?",(new_status,request_id))
        conn.commit(); conn.close()
        return True
