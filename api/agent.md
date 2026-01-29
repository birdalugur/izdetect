# API Agent Tanımı

Bu agent, nesne tespiti yapan dağıtık bir sistemin **merkezi kontrol ve veri erişim katmanı** olan API bileşenini temsil eder.

## Temel Sorumluluklar

- Kamera yönetimi (ekleme, silme, listeleme)
- Nesne tespit süreçlerinin başlatılması ve durdurulması
- Gerçek zamanlı olayların (notification) yayınlanması
- Tespit oturumlarının (detection sessions) yönetimi
- Bildirimlerin (notifications) filtrelenmesi, kapatılması ve silinmesi
- Sistem ayarlarının (memory, sensitivity) yönetimi
- Sistem kaynak durumunun (RAM) raporlanması

## Mimari Rol

Bu API:
- **FastAPI** tabanlıdır
- **Redis** üzerinden diğer servislerle (özellikle detection worker’ları) haberleşir
- **MongoDB** kullanarak kalıcı veri saklar
- **RTSP kamera akışlarını** MJPEG formatında istemcilere sunar
- **Server-Sent Events (SSE)** ile gerçek zamanlı bildirim yayını yapar

## Etkileşimde Olduğu Sistemler

- Redis  
  - Kamera URL listeleri
  - Start / stop sinyalleri
  - Gerçek zamanlı event yayınları
- MongoDB  
  - Notifications
  - Detection sessions
  - Kamera kayıtları
  - Sistem ayarları
- Video kaynakları (RTSP / MJPEG)

## Veri Sorumlulukları

Agent aşağıdaki veri tiplerinin **tek doğruluk kaynağıdır**:
- Detection session metadata
- Notification kayıtları ve görselleri
- Kamera konfigürasyonları
- Global sistem ayarları

## Çalışma Varsayımları

- Redis ve MongoDB servisleri çalışır durumdadır
- Nesne tespitini yapan worker servisler Redis kanalını dinler
- Kamera IP / RTSP adresleri geçerlidir
- Görsel çıktılar `Config.OUTPUT_FOLDER` altında saklanır

## Güvenlik ve Erişim

- CORS tüm origin’lere açıktır (geliştirme odaklı yapı)
- Kimlik doğrulama ve yetkilendirme bu katmanda uygulanmamıştır
- API, iç ağ veya güvenli bir gateway arkasında çalışacak şekilde tasarlanmıştır

## Agent Sınırları

Bu agent:
- Nesne tespit algoritmalarını **çalıştırmaz**
- Model eğitimi veya inference yapmaz
- Frontend render işlemlerini üstlenmez

Sadece **kontrol, orkestrasyon ve veri sunumu** görevlerini yürütür.
