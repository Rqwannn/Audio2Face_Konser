# Audio2Face: AI Identity & Animation Engine

![Python](https://img.shields.io/badge/Python-3.11%2B-blue?style=for-the-badge&logo=python)
![FastAPI](https://img.shields.io/badge/FastAPI-High_Performance-009688?style=for-the-badge&logo=fastapi)
![OpenCV](https://img.shields.io/badge/OpenCV-Computer_Vision-5C3EE8?style=for-the-badge&logo=opencv)
![ONNX](https://img.shields.io/badge/ONNX-Runtime-005CED?style=for-the-badge&logo=onnx)
![AWS S3](https://img.shields.io/badge/AWS-S3_Storage-FF9900?style=for-the-badge&logo=amazonaws)

> **Generative AI Backend** untuk menciptakan avatar digital yang personal. Menggabungkan teknologi *Face Swapping* dan *Audio-Driven Animation*.

Service ini bertindak sebagai **"Visual Engine"**, yang mengubah identitas wajah pada avatar 3D/2D menggunakan foto asli pengguna (berdasarkan NIK), lalu menghidupkannya agar bisa berbicara sesuai input audio.

---

## Fitur Utama

### Core AI Pipelines
* **Deep Face Swapping:** Mengganti wajah pada avatar target dengan wajah pengguna menggunakan model **Inswapper_128**. Mempertahankan identitas visual pengguna pada karakter fiksi.
* **Smart Resize Protection:** Dilengkapi mekanisme *Safety Resize* otomatis (Max 1280px). Mencegah server *crash* atau *Out Of Memory (OOM)* saat pengguna mengupload foto beresolusi sangat tinggi (misal: 32MP+).
* **Cloud-Native Integration:** Mengambil data wajah sumber (*Enrollment Photo*) langsung dari **Object Storage (S3)** secara aman, melakukan validasi integritas file sebelum diproses.
* **Audio-Driven Animation (WIP):** untuk menggerakkan bibir dan ekspresi avatar secara sinkron dengan file audio.

### Development Tools
* **Visual Debugger:** Fitur *pop-up window* (OpenCV) untuk memantau hasil *swapping* secara real-time di sisi server selama tahap development.
* **GPU Acceleration:** Mendukung akselerasi CUDA/NVIDIA untuk inferensi model Face Analysis & Swapping yang instan (< 2 detik).

---

## Tech Stack

| Komponen | Teknologi | Deskripsi |
| :--- | :--- | :--- |
| **API Framework** | **FastAPI** | High-performance async framework untuk handling request generate. |
| **Face Analysis** | **CNN** | Mendeteksi *landmark* wajah (mata, hidung, mulut). |
| **Face Swap** | **Inswapper (ONNX)** | Model Deepfake one-shot untuk memindahkan identitas wajah ke avatar. |
| **Storage** | **AWS S3 / MinIO** | Penyimpanan aman untuk foto user dan hasil generate sementara. |
| **Database** | **PostgreSQL** | Menyimpan metadata user dan link file wajah. |

---

## Prasyarat (Prerequisites)

Sebelum menjalankan sistem, pastikan environment Anda memenuhi syarat berikut:

1.  **Python 3.11+** (Disarankan menggunakan Virtual Environment / Conda).
2.  **NVIDIA GPU + CUDA Toolkit** (Sangat disarankan untuk performa optimal, meski bisa berjalan lambat di CPU).
3.  **PostgreSQL Database** (Service Data Diri harus sudah berjalan).
4.  **Akses Internet** (Untuk mendownload model awal dan akses S3).

---

## Cara Install & Setup

### 1. Clone Repository
```bash
git clone [URL_REPO]
cd AUDIO2FACE
```

### 2. Setup Environment
Install seluruh dependencies Python yang dibutuhkan:

```bash
pip install -r requirements.txt
```

### 3. Konfigurasi .env
Buat file `.env` di root folder dan sesuaikan dengan kredensial Anda:

```env
# Database Configuration
DB_URL=postgresql+asyncpg://user:password@localhost:5432/concert_db

# Object Storage (S3) Configuration
ACCESS_KEY_BUCKET_PROD=your_access_key
PRIVATE_KEY_BUCKET_PROD=your_secret_key
REGION_BUCKET_PROD=ap-southeast-1
S3_BUCKET_PROD=your_bucket_name
SERVER_BUCKET_PROD=[https://s3.endpoint.com](https://s3.endpoint.com)
```

---

## Download Model AI (Wajib)

Repository ini **tidak menyertakan file model AI** (Inswapper & InsightFace Models) karena ukurannya yang besar (>500MB). Tanpa file ini, service akan error saat dijalankan.

Kami telah menyediakan script otomatis untuk mengunduh dan menyusun folder `assets` dengan struktur yang benar.

### Windows (Recommended)
Buka terminal (CMD/PowerShell) di folder project, lalu jalankan:

```cmd
setup_models.bat
```

### Mac / Linux
Buka terminal di folder project, berikan izin eksekusi, lalu jalankan:

```bash
chmod +x setup_models.sh
./setup_models.sh
```

> **Catatan:** Script ini akan otomatis mendownload `inswapper_128.onnx`, `buffalo_l.zip`, dan meletakkannya di folder `assets/models`.

---

## Menjalankan Server

Jalankan server menggunakan **Uvicorn** (Mode Development):

```bash
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

---

## API Documentation

### Generate / Change Face
Mengubah wajah avatar target menjadi wajah pengguna berdasarkan NIK.

* **URL:** `/api/v1/face_generate/change_face`
* **Method:** `POST`
* **Content-Type:** `application/x-www-form-urlencoded`

**Parameters:**

| Parameter | Tipe | Deskripsi |
| :--- | :--- | :--- |
| `nik` | String | Nomor Induk Kependudukan (Wajib). Digunakan untuk lookup foto di DB/S3. |

**Contoh Response Sukses (201 Created):**

```json
{
    "status": "ENROLLMENT_SUCCESS",
    "data": {
        "status": 200,
        "data": {
            "status": "processed",
            "mock_result": "EchoMimic implementation pending",
            "source_image_used": "temp/swapped_1234567890.jpg"
        }
    }
}
```

**Kemungkinan Error:**
* `400 Bad Request`: NIK tidak ditemukan atau Foto wajah tidak terdeteksi.
* `500 Internal Server Error`: Gagal download S3, Model Crash, atau Error Server.