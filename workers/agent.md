# Services Agent (Detection Worker)

Bu agent, nesne tespiti yapan sistemin **yüksek işlem gücü gerektiren worker katmanını** temsil eder.  
Kamera akışlarından görüntü alır, yapay zekâ modeli ile inference yapar, nesne takibi uygular ve sonuçları Redis + MongoDB üzerinden sisteme yayınlar.

## Temel Sorumluluklar

- RTSP / video kaynaklarından kare üretimi
- Görüntülerin Redis üzerinden pipeline’a aktarılması
- DETR tabanlı nesne tespiti (inference)
- SORT algoritması ile nesne takibi (tracking)
- Tespit sonuçlarının filtrelenmesi (memory & sensitivity)
- Notification üretimi ve MongoDB’ye kayıt
- Gerçek zamanlı event yayınlama (Redis Pub/Sub)

## Mimari Rol

Bu agent:
- **CPU / GPU yoğun** işlemleri üstlenir
- API katmanından **bağımsız** çalışır
- Redis üzerinden **komut (start / stop)** dinler
- Birden fazla kamerayı **paralel** şekilde işler

## Çalışma Modeli

- Her kamera için ayrı bir **CameraPipeline** oluşturulur
- Pipeline aşağıdaki bileşenlerden oluşur:

FrameProducer → Inference → DetectionProcessor → NotifyProcessor


- İşlem türüne göre:
  - **Process**: IO + CPU yoğun işler
  - **Thread**: GPU inference

## Etkileşimde Olduğu Sistemler

- **Redis**
  - Frame queue’ları
  - Detection queue’ları
  - Task control (`task_control`)
  - Event yayınları (`event_channel`)
- **MongoDB**
  - Detection sessions
  - Notifications
  - Sistem ayarları (memory, sensitivity)
- **GPU / CUDA (opsiyonel)**

## Veri Sorumlulukları

Agent aşağıdaki verilerin **üreticisidir**:
- Detection sonuçları (boxes, labels, scores)
- Takiplenmiş obje ID’leri
- Notification görselleri
- Session bazlı metadata

## Yapay Zekâ ve Algoritmalar

- **Model**: `facebook/detr-resnet-50`
- **Inference**: PyTorch (FP16)
- **Tracking**: SORT + Kalman Filter
- **Label Mapping**:
  - İnsan
  - Araç
  - Hayvan

## Çalışma Varsayımları

- Redis ve MongoDB erişilebilir durumdadır
- Kamera URL’leri MongoDB’den alınır
- GPU varsa otomatik kullanılır
- Output dizinleri (`data/`, `output/`) yazılabilir durumdadır

## Güvenlik ve Sınırlar

- Authentication / authorization yoktur
- Ağ izolasyonu ve erişim kontrolü dış sistemlere bırakılmıştır
- Agent sadece **worker** rolündedir, HTTP endpoint sunmaz

## Agent Sınırları

Bu agent:
- Frontend render işlemi yapmaz
- API endpoint sağlamaz
- Kullanıcı etkileşimi içermez

Sadece **nesne tespiti pipeline’ının yürütülmesinden** sorumludur.
