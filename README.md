# ☕ Project Cafe — ระบบจัดการร้านกาแฟ

ระบบจัดการร้านกาแฟที่พัฒนาด้วย Django และ Microsoft SQL Server รองรับทั้งฝั่ง Staff/Admin และลูกค้า

---

## 📋 สิ่งที่ต้องติดตั้งก่อน

| โปรแกรม | ดาวน์โหลด |
|---|---|
| Python 3.12+ | https://www.python.org/downloads/ |
| SQL Server Express | https://www.microsoft.com/en-us/sql-server/sql-server-downloads |
| ODBC Driver 17 for SQL Server | https://learn.microsoft.com/en-us/sql/connect/odbc/download-odbc-driver-for-sql-server |
| SSMS (SQL Server Management Studio) | https://learn.microsoft.com/en-us/sql/ssms/download-sql-server-management-studio-ssms |
| Git | https://git-scm.com/downloads |

---

## 🚀 วิธีติดตั้งและรัน

### ขั้นที่ 1 — Clone โปรเจกต์

```bash
git clone https://github.com/<your-username>/Project-Cafe.git
cd Project-Cafe
```

---

### ขั้นที่ 2 — สร้าง Virtual Environment

```bash
python -m venv venv
```

**Activate venv:**

- Windows:
```bash
venv\Scripts\activate
```
- Mac/Linux:
```bash
source venv/bin/activate
```

พอ activate สำเร็จ terminal จะขึ้นแบบนี้:
```
(venv) ...>
```

---

### ขั้นที่ 3 — ติดตั้ง Dependencies

```bash
pip install -r requirements.txt
```

---

### ขั้นที่ 4 — ตั้งค่า Database

1. เปิด **SSMS** แล้วเชื่อมต่อกับ `localhost\SQLEXPRESS`
2. สร้าง Database ใหม่:
```sql
CREATE DATABASE CafeDB;
```
3. เปิดไฟล์ `CafeDB_Full.sql` ใน SSMS แล้วกด **Execute (F5)** เพื่อ import ข้อมูลทั้งหมด

---

### ขั้นที่ 5 — แก้ไข settings.py

เปิดไฟล์ `cafe/settings.py` แล้วแก้ password ให้ตรงกับที่ตั้งตอนติดตั้ง SQL Server:

```python
DATABASES = {
    'default': {
        'ENGINE': 'mssql',
        'NAME': 'CafeDB',
        'HOST': 'localhost\\SQLEXPRESS',
        'PORT': '',
        'USER': 'sa',
        'PASSWORD': 'your_password',  # ← แก้ตรงนี้
        'OPTIONS': {
            'driver': 'ODBC Driver 17 for SQL Server',
        },
    }
}
```

> ถ้าใช้ Windows Authentication แทน ให้เปลี่ยนเป็น:
> ```python
> 'OPTIONS': {
>     'driver': 'ODBC Driver 17 for SQL Server',
>     'trusted_connection': 'yes',
> },
> ```
> แล้วลบ `USER` และ `PASSWORD` ออก

---

### ขั้นที่ 6 — Copy รูปภาพเมนู

copy folder `Picture` ไปวางไว้ใน `media/menu_images/` ให้ครบ เพื่อให้รูปเมนูแสดงได้ถูกต้อง

```
Project Cafe/
└── media/
    └── menu_images/
        ├── Latte.jpg
        ├── Cappuccino.jpg
        └── ...
```

---

### ขั้นที่ 7 — Migrate และสร้าง Superuser

```bash
python manage.py migrate
python manage.py createsuperuser
```

---

### ขั้นที่ 8 — รัน Server

```bash
python manage.py runserver
```

เปิด browser แล้วไปที่ `http://127.0.0.1:8000`

---

## 🔑 URL หลักของระบบ

| URL | หน้า |
|---|---|
| `/` | Dashboard (Staff/Admin) |
| `/login/` | หน้า Login Staff |
| `/menu/` | จัดการเมนู |
| `/ingredients/` | จัดการวัตถุดิบ |
| `/orders/` | รายการออเดอร์ |
| `/queue/` | จัดการคิว |
| `/customer/login/` | หน้า Login ลูกค้า |
| `/customer/` | หน้าเมนูสำหรับลูกค้า |
| `/admin/` | Django Admin Panel |

---

## 🗄️ โครงสร้างโปรเจกต์

```
Project Cafe/
├── cafe/               # Django settings, urls, wsgi
├── cafe_app/           # Main app (models, views, templates)
│   └── templates/
│       └── cafe_app/   # HTML templates ทั้งหมด
├── media/              # รูปภาพที่ upload
├── venv/               # Virtual environment (ไม่ต้อง push Git)
├── CafeDB_Full.sql     # SQL script สร้าง database
├── trg_ReduceStock.sql     # Trigger ตัด stock เมื่อสั่งอาหาร
├── trg_RestoreStock.sql    # Trigger คืน stock เมื่อยกเลิก order
├── trg_UpdateTotalPrice.sql # Trigger อัปเดตราคารวม
├── manage.py
└── requirements.txt
```

---

## ⚙️ Triggers ที่ใช้ใน Database

| Trigger | ทำงานเมื่อ | หน้าที่ |
|---|---|---|
| `trg_ReduceStock` | INSERT ORDER_ITEM | ตัด stock วัตถุดิบตาม recipe อัตโนมัติ |
| `trg_RestoreStock` | DELETE ORDER_ITEM | คืน stock เมื่อ order ถูกยกเลิก |
| `trg_UpdateTotalPrice` | INSERT ORDER_ITEM | คำนวณและอัปเดตราคารวมของ order |

---

## ❗ หมายเหตุ

- `venv/` และ `media/` ไม่ถูก push ขึ้น Git ตาม `.gitignore` — ต้องสร้างใหม่ทุกครั้งที่ clone
- SQL Server ต้องรันอยู่ก่อนเสมอถึงจะ start server ได้
- Default password ใน `settings.py` คือ `123` — ควรเปลี่ยนก่อนใช้งานจริง
