# Object Detection API

Bu dizin, nesne tespiti yapan bir sistemin **backend API katmanını** içerir.  
API; kamera yönetimi, tespit oturumları, bildirimler ve sistem ayarlarını yönetmekten sorumludur.

---

## 🧱 Teknoloji Yığını

- **Python 3.11**
- **FastAPI**
- **Uvicorn**
- **MongoDB** (kalıcı veri)
- **Redis** (event & kontrol sinyalleri)
- **OpenCV** (video stream)
- **Server-Sent Events (SSE)**

---

## 📁 Dizin Yapısı

```

api/
├── app.py                # FastAPI uygulama girişi
├── config.py             # Ortam ve sistem ayarları
├── db.py                 # MongoDB erişim katmanı
├── routes/               # API endpoint’leri
│   ├── cameras.py
│   ├── notifications.py
│   ├── detection_sessions.py
│   └── system.py
├── services/             # İş mantığı servisleri
│   ├── camera_service.py
│   ├── redis_service.py
│   └── video_service.py
├── utils/                # Yardımcı fonksiyonlar & istisnalar
├── Dockerfile
├── requirements.txt

````

---

## 🚀 Uygulamayı Çalıştırma

### Lokal Ortam

```bash
python -m venv env
source env/bin/activate
pip install -r requirements.txt
uvicorn app:app --reload
````

API varsayılan olarak:

```
http://localhost:8000
```

---

### Docker ile

```bash
docker build -t object-detection-api .
docker run -p 8000:8000 object-detection-api
```

---

## 🔌 Redis Kullanımı

Redis aşağıdaki amaçlarla kullanılır:

* `camera_urls` → RTSP kamera adresleri listesi
* `stop_signal` → Detection worker kontrolü
* `task_control` → start / stop komutları
* `event_channel` → Gerçek zamanlı notification yayını

---

## 🧠 Temel Kavramlar

### Detection Session

Bir tespit sürecinin başlangıç–bitiş zamanını temsil eder.
Bir session altında birden fazla notification bulunur.

### Notification

Bir veya daha fazla nesnenin tespit edilmesi sonucu oluşan kayıttır.

* Zaman bilgisi
* Etiketler (insan, araç, hayvan)
* Görsel çıktı (opsiyonel)
* Durum: `active` / `closed`

### Label Mapping

Sayısal label’lar API çıkışında otomatik olarak isimlendirilir:

```python
{1: "insan", 2: "arac", 3: "hayvan"}
```

---

## 📡 Gerçek Zamanlı Olay Akışı (SSE)

```http
GET /cameras/events
```

* Redis `event_channel` dinlenir
* Bildirimler anlık olarak frontend’e push edilir

---

## 🛠️ Sağlanan API Grupları

* `/cameras`
  Kamera yönetimi, canlı video, detection kontrolü

* `/notifications`
  Bildirim listeleme, filtreleme, silme, kapatma

* `/detection-sessions`
  Oturum listeleme, detay, silme

* `/system`
  Sistem ayarları ve RAM bilgisi

Swagger UI:

```
/docs
```

---

## ⚠️ Bilinen Kapsam Dışı Alanlar

* Authentication / Authorization
* Rate limiting
* Model inference ve AI logic

Bu sorumluluklar API dışındaki servisler tarafından üstlenilir.

---

## 📌 Not

Bu dizin **yalnızca API katmanını** temsil eder.
`services/` (worker / detection logic) ve `frontend/` dizinleri ayrı bileşenlerdir ve bu README kapsamı dışındadır.


