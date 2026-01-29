# Sistem Mimarisi (Architecture)

Bu doküman, `services` dizini altında yer alan tüm bileşenleri kapsayan **üst seviye sistem mimarisini** tanımlar. Amaç; veri akışını, bileşen sorumluluklarını, süreç modelini ve altyapı bağımlılıklarını net ve sürdürülebilir bir şekilde ortaya koymaktır.

---

## 1. Genel Bakış

Sistem; çoklu kamera kaynaklarından gerçek zamanlı görüntü alımı, nesne tespiti (Object Detection), nesne takibi (Tracking), olay üretimi (Notification) ve kalıcı kayıt (MongoDB) işlemlerini **dağıtık ve ölçeklenebilir** bir mimari ile gerçekleştirir.

Temel mimari prensipler:

* **Pipeline-based processing** (kamera başına izole hat)
* **Process + Thread hibrit modeli**
* **Redis tabanlı mesajlaşma / kuyruklama**
* **Stateless worker + stateful tracker yaklaşımı**

---

## 2. Yüksek Seviyeli Bileşenler

```
+-------------+      +-------------+      +----------------+
|  Camera(s)  | ---> | FrameProducer| ---> |   Inference    |
+-------------+      +-------------+      +----------------+
                                                  |
                                                  v
                                           +----------------+
                                           | DetectionProc  |
                                                  |
                                                  v
                                           +----------------+
                                           | NotifyProcessor|
                                                  |
                                                  v
                                            MongoDB / Redis
```

Her kamera için bu yapı **bağımsız bir CameraPipeline** olarak çalışır.

---

## 3. Ana Süreç: `main.py`

### Sorumluluklar

* Redis üzerinden **start / stop / reconnect** komutlarını dinlemek
* Kamera listelerini MongoDB’den almak
* Kamera başına pipeline oluşturmak
* Process ve Thread runner’ları yönetmek

### Kontrol Mekanizması

* Redis channel: `task_control`
* Komutlar:

  * `start` → tüm pipeline’ları başlatır
  * `stop` → tüm pipeline’ları durdurur
  * `disconnected` → kontrollü restart

---

## 4. Pipeline Mimarisi (`CameraPipeline`)

Her kamera için aşağıdaki bileşenler oluşturulur:

| Bileşen            | Çalışma Modeli | Görev                 |
| ------------------ | -------------- | --------------------- |
| FrameProducer      | Process        | Kameradan frame okuma |
| Inference          | Thread         | Model inference (GPU) |
| DetectionProcessor | Process        | Tracking + filtreleme |
| NotifyProcessor    | Process        | Event & DB kaydı      |

Pipeline başlatıldığında:

1. MongoDB’de detection session açılır
2. Redis queue isimleri oluşturulur
3. Bileşenler runner’lara eklenir

---

## 5. İşleme Bileşenleri

### 5.1 FrameProducer

**Amaç:**

* RTSP / video kaynağından frame almak
* Frame’leri Redis kuyruğuna yazmak

**Özellikler:**

* Otomatik reconnect
* Timeout kontrollü OpenCV capture
* Binary JPEG encoding

Redis Queue:

* `camera{N}`

---

### 5.2 Inference

**Amaç:**

* Frame’leri alıp DETR modeli ile nesne tespiti yapmak

**Özellikler:**

* GPU destekli (CUDA varsa)
* Batch inference desteği
* Half precision (FP16)

Giriş:

* `camera{N}`

Çıkış:

* Detection sonucu → `inference{N}`
* Orijinal image → `camera{N}_inf`

---

### 5.3 DetectionProcessor

**Amaç:**

* Detection sonuçları üzerinde **SORT tabanlı tracking** yapmak
* Gürültüyü azaltmak

**Dinamik Konfigürasyon:**

* MongoDB `system_settings` koleksiyonu

  * `memory` → tracker max_age
  * `sensitivity` → min_hits & IOU threshold

Çıkış:

* `[x1, y1, x2, y2, object_id, label]`

Redis Queue:

* `tracking{N}`

---

### 5.4 NotifyProcessor

**Amaç:**

* Yeni ve anlamlı nesneler için event üretmek
* Görüntü kaydı almak
* MongoDB’ye notification yazmak

**Öne Çıkan Mantık:**

* Aynı `object_id` için tek sefer bildirim
* Label bazlı filtreleme
* Frame–Detection senkronizasyonu

Kalıcı Çıktılar:

* `data/*.jpg`
* MongoDB `notifications`

Redis:

* `event_channel` (publish)

---

## 6. Veri Katmanı

### MongoDB

Koleksiyonlar:

* `cameras` → kamera IP listesi
* `detection_sessions` → oturum bazlı metadata
* `notifications` → olay kayıtları
* `system_settings` → runtime tuning

### Redis

Roller:

* Queue (LPUSH / RPOP / BRPOP)
* Pub/Sub (event, control)
* Stateless servisler arası glue

---

## 7. Süreç ve Thread Modeli

```
Main Process
 ├─ Process: FrameProducer (per camera)
 ├─ Process: DetectionProcessor (per camera)
 ├─ Process: NotifyProcessor (per camera)
 └─ Thread : Inference (per camera)
```

**Neden?**

* CPU-bound işler process
* GPU inference thread (memory paylaşımı)

---

## 8. Dayanıklılık ve Hata Toleransı

* Kamera bağlantı kopması → reconnect
* Redis empty queue → non-blocking wait
* Graceful stop → session kapanışı
* Forced stop → process terminate

---

## 9. Ölçeklenebilirlik

* Kamera sayısı lineer ölçeklenir
* Her kamera izole pipeline
* Redis & Mongo yatay ölçeklenebilir
* GPU kapasitesine göre batch tuning

---

## 10. Docker & Deployment

* Python 3.11 tabanlı Docker image
* GPU destekli (CUDA runtime gerekli)
* Environment variable ile config

Açık Portlar:

* `8000` → API
* `6379` → Redis
* `8080` → UI / servisler

---

## 11. Özet

Bu mimari;

* Gerçek zamanlı,
* Modüler,
* İzole pipeline’lar ile güvenli,
* GPU-dostu,
* Üretim ortamına uygun

bir **video analytics platformu** sunar.

---

> Bu doküman, sistem genişledikçe (API, auth, multi-GPU, load balancing) referans mimari olarak kullanılmalıdır.
