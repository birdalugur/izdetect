from fastapi import APIRouter, HTTPException
from datetime import datetime, timedelta
from typing import Dict, List, Optional
from pymongo import MongoClient
from config import Config
from db import notifications_collection, detection_sessions_collection

router = APIRouter(prefix="/stats", tags=["Statistics"])


def get_date_range(period: str = "today"):
    """
    Farklı zaman periyotları için başlangıç ve bitiş tarihlerini döner.
    
    Args:
        period: "today", "yesterday", "week", "last_week", "month", "last_month"
    
    Returns:
        Tuple of (start_date, end_date) as datetime objects
    """
    now = datetime.now()
    
    if period == "today":
        start = now.replace(hour=0, minute=0, second=0, microsecond=0)
        end = now.replace(hour=23, minute=59, second=59, microsecond=999999)
    elif period == "yesterday":
        yesterday = now - timedelta(days=1)
        start = yesterday.replace(hour=0, minute=0, second=0, microsecond=0)
        end = yesterday.replace(hour=23, minute=59, second=59, microsecond=999999)
    elif period == "week":
        # Bu hafta (pazartesi - pazar)
        start = now - timedelta(days=now.weekday())
        start = start.replace(hour=0, minute=0, second=0, microsecond=0)
        end = now.replace(hour=23, minute=59, second=59, microsecond=999999)
    elif period == "last_week":
        # Geçen hafta
        end = now - timedelta(days=now.weekday() + 1)
        end = end.replace(hour=23, minute=59, second=59, microsecond=999999)
        start = end - timedelta(days=6)
        start = start.replace(hour=0, minute=0, second=0, microsecond=0)
    elif period == "month":
        # Bu ay
        start = now.replace(day=1, hour=0, minute=0, second=0, microsecond=0)
        end = now.replace(hour=23, minute=59, second=59, microsecond=999999)
    elif period == "last_month":
        # Geçen ay
        end = now.replace(day=1, hour=0, minute=0, second=0, microsecond=0) - timedelta(seconds=1)
        start = end.replace(day=1, hour=0, minute=0, second=0, microsecond=0)
    else:
        # Default to today
        start = now.replace(hour=0, minute=0, second=0, microsecond=0)
        end = now.replace(hour=23, minute=59, second=59, microsecond=999999)
    
    return start, end


@router.get("/summary", summary="İstatistik özeti")
async def get_stats_summary(period: str = "today"):
    """
    Belirtilen zaman döneminin istatistik özetini döner.
    
    Args:
        period: "today", "yesterday", "week", "last_week", "month", "last_month"
    
    Returns:
        Toplam bildirim sayısı, aktif oturumlar, kapalı oturumlar vs.
    """
    try:
        start_date, end_date = get_date_range(period)
        
        # Belirtilen dönemde toplam bildirimler
        total_notifications = notifications_collection.count_documents({
            "time": {"$gte": start_date, "$lte": end_date}
        })
        
        # Aktif oturumlar
        active_sessions = detection_sessions_collection.count_documents({"end": None})
        
        # Kapalı oturumlar
        closed_sessions = detection_sessions_collection.count_documents({"end": {"$ne": None}})
        
        # Belirtilen dönemde aktif bildirimlerin sayısı
        active_notifications_count = notifications_collection.count_documents({
            "time": {"$gte": start_date, "$lte": end_date},
            "status": "active"
        })
        
        # Belirtilen dönemde kapalı bildirimlerin sayısı
        closed_notifications_count = notifications_collection.count_documents({
            "time": {"$gte": start_date, "$lte": end_date},
            "status": "closed"
        })
        
        return {
            "period": period,
            "start_date": start_date.isoformat(),
            "end_date": end_date.isoformat(),
            "total_notifications": total_notifications,
            "active_notifications": active_notifications_count,
            "closed_notifications": closed_notifications_count,
            "active_sessions": active_sessions,
            "closed_sessions": closed_sessions,
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/by-label", summary="Etiket türüne göre bildirimler")
async def get_stats_by_label(period: str = "today"):
    """
    Bildirim etiketlerine göre dağılımı döner (insan/arac/hayvan).
    
    Args:
        period: "today", "yesterday", "week", "last_week", "month", "last_month"
    
    Returns:
        Etiket türlerine göre bildirim sayılarının dağılımı
    """
    try:
        start_date, end_date = get_date_range(period)
        
        # Etiketlere göre gruplama yapan aggregation pipeline
        pipeline = [
            {
                "$match": {
                    "time": {"$gte": start_date, "$lte": end_date}
                }
            },
            {
                "$unwind": "$labels"
            },
            {
                "$group": {
                    "_id": {"$objectToArray": "$labels"},
                    "count": {"$sum": 1}
                }
            },
            {
                "$sort": {"count": -1}
            }
        ]
        
        results = list(notifications_collection.aggregate(pipeline))
        
        # Sonuçları format et
        formatted_results = []
        for result in results:
            # labels objesi: [{"k": "1", "v": 5}] şeklinde gelir, onu düzleştir
            if result["_id"] and len(result["_id"]) > 0:
                label_id = result["_id"][0].get("k", "unknown")
                count = result["count"]
                
                # Label ID'sini label adına dönüştür
                label_map = {"1": "insan", "2": "arac", "3": "hayvan", "4": "bisiklet", 
                            "6": "motosiklet", "8": "kedi", "18": "köpek", "19": "kuş", 
                            "20": "balık", "21": "at"}
                label_name = label_map.get(label_id, f"label_{label_id}")
                
                formatted_results.append({
                    "label_id": label_id,
                    "label_name": label_name,
                    "count": count
                })
        
        return {
            "period": period,
            "start_date": start_date.isoformat(),
            "end_date": end_date.isoformat(),
            "data": formatted_results
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/by-camera", summary="Kameraya göre bildirimler")
async def get_stats_by_camera(period: str = "today"):
    """
    Kameralara göre bildirim dağılımını döner.
    
    Args:
        period: "today", "yesterday", "week", "last_week", "month", "last_month"
    
    Returns:
        Her kamera için bildirim sayılarının dağılımı
    """
    try:
        start_date, end_date = get_date_range(period)
        
        # Kameralara göre gruplama
        pipeline = [
            {
                "$match": {
                    "time": {"$gte": start_date, "$lte": end_date}
                }
            },
            {
                "$group": {
                    "_id": "$camera_id",
                    "count": {"$sum": 1}
                }
            },
            {
                "$sort": {"count": -1}
            }
        ]
        
        results = list(notifications_collection.aggregate(pipeline))
        
        formatted_results = [
            {
                "camera_id": result["_id"] or "unknown",
                "count": result["count"]
            }
            for result in results
        ]
        
        return {
            "period": period,
            "start_date": start_date.isoformat(),
            "end_date": end_date.isoformat(),
            "data": formatted_results
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/timeline", summary="Zaman çizelgesi (saatlik/günlük)")
async def get_stats_timeline(period: str = "today", granularity: str = "hourly"):
    """
    Belirtilen dönem için saatlik veya günlük bildirim sayılarını döner.
    
    Args:
        period: "today", "yesterday", "week", "last_week", "month", "last_month"
        granularity: "hourly" veya "daily"
    
    Returns:
        Zaman çizelgesine göre bildirim sayıları
    """
    try:
        start_date, end_date = get_date_range(period)
        
        # Granularite'ye göre date_format belirle
        if granularity == "hourly":
            date_format = "%Y-%m-%d %H:00"
        else:  # daily
            date_format = "%Y-%m-%d"
        
        # Zaman gruplamalaması
        pipeline = [
            {
                "$match": {
                    "time": {"$gte": start_date, "$lte": end_date}
                }
            },
            {
                "$group": {
                    "_id": {
                        "$dateToString": {
                            "format": date_format,
                            "date": "$time"
                        }
                    },
                    "count": {"$sum": 1}
                }
            },
            {
                "$sort": {"_id": 1}
            }
        ]
        
        results = list(notifications_collection.aggregate(pipeline))
        
        # Tüm zaman aralıklarını doldur (boş saatleri 0 olarak)
        filled_timeline = []
        if granularity == "hourly":
            current = start_date.replace(minute=0, second=0, microsecond=0)
            while current <= end_date:
                time_str = current.strftime("%Y-%m-%d %H:00")
                count = next((r["count"] for r in results if r["_id"] == time_str), 0)
                filled_timeline.append({
                    "time": time_str,
                    "count": count
                })
                current += timedelta(hours=1)
        else:  # daily
            current = start_date.replace(hour=0, minute=0, second=0, microsecond=0)
            while current <= end_date:
                time_str = current.strftime("%Y-%m-%d")
                count = next((r["count"] for r in results if r["_id"] == time_str), 0)
                filled_timeline.append({
                    "time": time_str,
                    "count": count
                })
                current += timedelta(days=1)
        
        return {
            "period": period,
            "granularity": granularity,
            "start_date": start_date.isoformat(),
            "end_date": end_date.isoformat(),
            "data": filled_timeline
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/comparison", summary="Dönem karşılaştırması")
async def get_stats_comparison(compare_with: str = "yesterday"):
    """
    Günümüzü dün/geçen hafta/geçen ay ile karşılaştırır.
    
    Args:
        compare_with: "yesterday", "last_week", "last_month"
    
    Returns:
        Cari dönem vs. karşılaştırılan dönem için bildirim sayıları ve fark yüzdesi
    """
    try:
        # Cari dönem (today, this week, this month)
        if compare_with == "yesterday":
            current_period = "today"
        elif compare_with == "last_week":
            current_period = "week"
        else:  # last_month
            current_period = "month"
        
        current_start, current_end = get_date_range(current_period)
        compare_start, compare_end = get_date_range(compare_with)
        
        # Cari dönem için toplam
        current_count = notifications_collection.count_documents({
            "time": {"$gte": current_start, "$lte": current_end}
        })
        
        # Karşılaştırılan dönem için toplam
        compare_count = notifications_collection.count_documents({
            "time": {"$gte": compare_start, "$lte": compare_end}
        })
        
        # Fark yüzdesini hesapla
        if compare_count == 0:
            percent_change = 0 if current_count == 0 else 100
        else:
            percent_change = ((current_count - compare_count) / compare_count) * 100
        
        return {
            "current_period": current_period,
            "compare_with": compare_with,
            "current_count": current_count,
            "compare_count": compare_count,
            "percent_change": round(percent_change, 2),
            "trend": "up" if percent_change > 0 else "down" if percent_change < 0 else "neutral"
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/dashboard", summary="Tüm istatistikleri tek çağrıda getir")
async def get_dashboard_stats(period: str = "today"):
    """
    Dashboard için tüm istatistikleri tek seferde döner (performans için).
    
    Args:
        period: "today", "yesterday", "week", "last_week", "month", "last_month"
    
    Returns:
        Özet, etiket dağılımı, kamera dağılımı ve zaman çizelgesi
    """
    try:
        summary = await get_stats_summary(period)
        by_label = await get_stats_by_label(period)
        by_camera = await get_stats_by_camera(period)
        timeline = await get_stats_timeline(period, "hourly")
        
        # Karşılaştırma verilerini de ekle
        comparison_data = {}
        if period == "today":
            comparison = await get_stats_comparison("yesterday")
            comparison_data = {
                "today_vs_yesterday": comparison
            }
        
        return {
            "period": period,
            "summary": summary,
            "by_label": by_label["data"],
            "by_camera": by_camera["data"],
            "timeline": timeline["data"],
            "comparisons": comparison_data
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
