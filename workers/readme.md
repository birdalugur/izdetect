# Object Detection Services

Bu dizin, nesne tespiti yapan sistemin **worker / inference katmanını** içerir.  
Amaç; kamera akışlarından gelen görüntüler üzerinde **yüksek performanslı nesne tespiti ve takibi** yapmaktır.

---

## 🧱 Teknoloji Yığını

- **Python 3.11**
- **PyTorch 2.7 (CUDA destekli)**
- **Transformers (DETR)**
- **OpenCV**
- **Redis**
- **MongoDB**
- **SORT (Kalman Filter)**
- **Multiprocessing / Threading**

---

## 📁 Dizin Yapısı

```

services/
├── main.py                 # Redis dinleyici ve lifecycle yönetimi
├── pipeline.py             # Kamera bazlı pipeline tanımı
├── model.py                # DETR model yükleme ve inference
├── core/
│   ├── base.py             # Service abstract class
│   ├── db.py               # MongoDB erişimi
│   ├── sort.py             # SORT tracking algoritması
│   ├── service_runner.py   # Process / Thread yöneticisi
│   └── utils.py            # Görüntü ve çizim yardımcıları
├── processors/
│   ├── frame_producer.py   # Kamera frame üretimi
│   ├── inference.py        # Model inference
│   ├── detection_processor.py # Tracking + filtreleme
│   ├── notify_processor.py # Notification üretimi
│   └── image_processor.py
├── Dockerfile
├── requirements.txt

```

---

## 🔄 Pipeline Akışı

```

RTSP Kamera
↓
FrameProducer (Redis queue)
↓
Inference (DETR)
↓
DetectionProcessor (SORT)
↓
NotifyProcessor
↓
MongoDB + Redis Event

````

---

## 🚀 Çalıştırma

### Lokal

```bash
pip install -r requirements.txt
python main.py
````

### Docker

```bash
docker build -t detection-services .
docker run --gpus all detection-services
```

---

## 🧠 Kamera Pipeline Mantığı

* Her kamera için:

  * Ayrı frame kuyruğu
  * Ayrı inference çıktısı
  * Ayrı tracking state
  * Ayrı detection session

Session başlangıç ve bitişleri MongoDB’de tutulur.

---

## ⚙️ Dinamik Sistem Ayarları

MongoDB `system_settings` koleksiyonundan okunur:

| Alan          | Açıklama                    |
| ------------- | --------------------------- |
| `memory`      | Tracking geçmişi (max_age)  |
| `sensitivity` | IOU ve min_hits hesaplaması |

Bu ayarlar **servis restart edilmeden** uygulanır.

---

## 📡 Redis Kontrol Kanalları

* `task_control`

  * `start`
  * `stop`
  * `disconnected`
* `event_channel`

  * Gerçek zamanlı notification yayını

---

## 📸 Notification Mantığı

* Aynı obje ID için **tek bildirim**
* Seçili label’lar (insan / araç / hayvan)
* Görsel overlay + kayıt
* MongoDB’ye kayıt + Redis publish

---

## ⚠️ Bilinen Sınırlar

* Queue senkronizasyonu bire-bir varsayımına dayanır
* Redis backpressure yönetimi yoktur
* Kamera kopmaları retry ile çözülür

---

## 📌 Not

Bu dizin **yalnızca worker katmanını** temsil eder.
API ve frontend bileşenleri ayrı servislerdir.

