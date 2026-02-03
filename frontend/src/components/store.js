import { writable, derived } from "svelte/store";
import { API_CONFIG } from "./api-config.js";

export const cameraUrls = writable({ cameraUrl1: "", cameraUrl2: "" });

// Dinamik olarak SERVER_IP'yi belirle
// API_CONFIG ile kontrol edilebilir: mode: 'auto' (localhost) veya mode: 'custom' (belirtilen IP)
const getServerUrl = () => {
  if (API_CONFIG.mode === 'auto' && typeof window !== 'undefined') {
    return `http://${window.location.hostname}`;
  }
  return API_CONFIG.customApiUrl || "http://localhost";
};

export const SERVER_IP = getServerUrl();

// Dark mode store
export const darkMode = writable(false);
export const detectionRefresh = writable(0);
export const modalStore = writable({
  isOpen: false,
  component: null,
  props: {}
});

// Modal yönetimi için yardımcı fonksiyonlar
modalStore.openModal = function (component, props = {}, isSmallModal = false) {
  modalStore.set({
    isOpen: true,
    component: component,
    props: props,
    isSmallModal: isSmallModal
  });
};

modalStore.closeModal = function () {
  modalStore.set({
    isOpen: false,
    component: null,
    props: {}
  });
};

export function clearCameraUrls() {
  cameraUrls.set({ cameraUrl1: "", cameraUrl2: "" });
}

// Statistics Store
export const statsStore = writable({
  period: "today",
  loading: false,
  error: null,
  summary: null,
  byLabel: [],
  byCamera: [],
  timeline: [],
  comparison: null,
  lastUpdated: null
});

let statsUpdateInterval = null;

/**
 * İstatistikleri API'den alır
 */
export async function fetchStats(period = "today") {
  statsStore.update(store => ({
    ...store,
    loading: true,
    error: null
  }));

  try {
    const apiUrl = `${SERVER_IP}:8000/stats/dashboard?period=${period}`;
    console.log("📊 İstatistik isteniyor:", apiUrl);
    
    const response = await fetch(apiUrl);
    
    if (!response.ok) {
      throw new Error(`API error: ${response.statusText}`);
    }

    const data = await response.json();
    console.log("✅ İstatistikler başarıyla yüklendi:", data);

    statsStore.update(store => ({
      ...store,
      period: period,
      summary: data.summary,
      byLabel: data.by_label || [],
      byCamera: data.by_camera || [],
      timeline: data.timeline || [],
      comparison: data.comparisons || null,
      lastUpdated: new Date(),
      loading: false
    }));
  } catch (error) {
    console.error("❌ İstatistik yükleme hatası:", error);
    console.error("🔍 Kullanılan URL:", `${SERVER_IP}:8000/stats/dashboard?period=${period}`);
    console.error("💡 API_CONFIG modunuz:", API_CONFIG.mode);
    console.error("💡 API sunucusu:", API_CONFIG.mode === 'auto' ? `otomatik (${window.location.hostname})` : API_CONFIG.customApiUrl);
    
    statsStore.update(store => ({
      ...store,
      loading: false,
      error: error.message
    }));
  }
}

/**
 * Periyodik güncelleme başlat (30 saniyede bir)
 */
export function startStatsPolling(interval = 30000) {
  // Mevcut interval'i temizle
  if (statsUpdateInterval) {
    clearInterval(statsUpdateInterval);
  }

  // İlk kez hemen çalıştır
  let currentPeriod = "today";
  statsStore.subscribe(store => {
    currentPeriod = store.period;
  })();

  fetchStats(currentPeriod);

  // Sonra düzenli olarak güncelle
  statsUpdateInterval = setInterval(async () => {
    let period = "today";
    statsStore.subscribe(store => {
      period = store.period;
    })();
    
    fetchStats(period);
  }, interval);
}

/**
 * Periyodik güncellemeyi durdur
 */
export function stopStatsPolling() {
  if (statsUpdateInterval) {
    clearInterval(statsUpdateInterval);
    statsUpdateInterval = null;
  }
}

/**
 * İstatistik dönemini değiştir
 */
export async function changeStatsPeriod(period) {
  statsStore.update(store => ({
    ...store,
    period: period
  }));
  await fetchStats(period);
}

