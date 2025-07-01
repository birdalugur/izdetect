<!-- src/components/NotificationModal.svelte -->
<script>
  import { onMount, createEventDispatcher } from 'svelte';
  import Pagination from './Pagination.svelte';
  import LabelTag from './LabelTag.svelte';

  export let filterParams = null;
  export let sessionId = null;

  const dispatch = createEventDispatcher();

  let notifications = [];
  let selectedImage = null;
  let selectedNotificationId = null;
  let loading = true;
  let error = null;

  const perPage = 12;
  let currentPage = 1;

  $: totalPages = Math.ceil(notifications.length / perPage);
  $: paged = notifications.slice(
    (currentPage - 1) * perPage,
    currentPage * perPage
  );

  async function fetchNotifications() {
    loading = true;
    error = null;
    
    try {
      let url;
      
      if (sessionId) {
        // Session ID'ye göre notification'ları getir - doğru endpoint
        url = `http://localhost:8000/notifications/by_session/${sessionId}`;
        console.log('Session ID ile API çağrısı:', url);
      } else if (filterParams) {
        // Filtre parametrelerine göre notification'ları getir - doğru endpoint
        const params = new URLSearchParams();
        
        // Tarih filtreleri (API'nin beklediği format)
        if (filterParams.startDate) {
          let startDateTime = filterParams.startDate;
          if (filterParams.startTime) {
            startDateTime += `T${filterParams.startTime}:00`;
          } else {
            startDateTime += 'T00:00:00';
          }
          params.append('start_date', startDateTime);
        }
        
        if (filterParams.endDate) {
          let endDateTime = filterParams.endDate;
          if (filterParams.endTime) {
            endDateTime += `T${filterParams.endTime}:59`;
          } else {
            endDateTime += 'T23:59:59';
          }
          params.append('end_date', endDateTime);
        }
        
        // Seçili etiketleri ekle - API integer bekliyor (label_map'e göre)
        const selectedLabels = Object.entries(filterParams.selectedLabels || {})
          .filter(([key, val]) => val === true)
          .map(([key, val]) => key);
          
        console.log('Seçili etiketler:', selectedLabels);
        
        // Label mapping: Config.LABEL_MAP'e göre (1: "insan", 2: "arac", 3: "hayvan")
        const labelMap = { 'insan': 1, 'arac': 2, 'hayvan': 3 };
        const labelIds = selectedLabels
          .map(label => labelMap[label])
          .filter(id => id !== undefined);
          
        if (labelIds.length > 0) {
          params.append('labels', labelIds.join(','));
        }
        
        // Pagination parametreleri
        params.append('skip', '0');
        params.append('limit', '100'); // Daha fazla sonuç için
        
        url = `http://localhost:8000/notifications/by_date?${params.toString()}`;
        console.log('Filtre ile API çağrısı:', url);
      } else {
        // Varsayılan olarak tüm notification'ları getir
        url = 'http://localhost:8000/notifications';
      }

      const res = await fetch(url);
      if (!res.ok) throw new Error(`HTTP ${res.status}: ${res.statusText}`);
      
      const data = await res.json();
      notifications = Array.isArray(data) ? data.reverse() : [];
      currentPage = 1;
      
      console.log(`${notifications.length} bildirim yüklendi:`, notifications);
    } catch (e) {
      console.error('Notification yükleme hatası:', e);
      error = e.message;
      notifications = [];
    } finally {
      loading = false;
    }
  }

  onMount(fetchNotifications);

  function showImage(url, id) {
    selectedNotificationId = id;
    selectedImage = `http://localhost:8000/cameras/output/${url}`;
  }

  function closeImage() {
    selectedImage = null;
    selectedNotificationId = null;
  }

  function showNextImage() {
    const idx = notifications.findIndex(n => n._id === selectedNotificationId);
    if (idx < 0) return;
    const next = notifications[idx + 1];
    if (next) showImage(next.image_url, next._id);
  }

  function showPreviousImage() {
    const idx = notifications.findIndex(n => n._id === selectedNotificationId);
    if (idx < 0) return;
    const prev = notifications[idx - 1];
    if (prev) showImage(prev.image_url, prev._id);
  }

  function closeModal() {
    dispatch('close');
  }

  // ESC tuşu ile modalı kapat
  function handleKeydown(event) {
    if (event.key === 'Escape') {
      if (selectedImage) {
        closeImage();
      } else {
        closeModal();
      }
    }
  }
</script>

<svelte:window on:keydown={handleKeydown} />

<div class="w-full h-full p-6 bg-gradient-to-br from-blue-50 to-white overflow-auto">
  <!-- Başlık -->
  <div class="mb-6">
    <h2 class="text-3xl font-bold text-gray-800 mb-2">
      {#if sessionId}
        Oturum Bildirimleri
      {:else if filterParams}
        Filtrelenmiş Bildirimler
      {:else}
        Tüm Bildirimler
      {/if}
    </h2>
    <p class="text-gray-600">
      {loading ? 'Yükleniyor...' : `Toplam ${notifications.length} bildirim bulundu`}
    </p>
  </div>

  {#if loading}
    <div class="flex justify-center items-center h-64">
      <div class="animate-spin rounded-full h-16 w-16 border-b-2 border-blue-600"></div>
    </div>
  {:else if error}
    <div class="bg-red-100 border border-red-400 text-red-700 px-4 py-3 rounded">
      <strong>Hata:</strong> {error}
    </div>
  {:else if notifications.length === 0}
    <div class="text-center py-16">
      <div class="text-gray-400 mb-4">
        <svg xmlns="http://www.w3.org/2000/svg" class="w-24 h-24 mx-auto" fill="none" viewBox="0 0 24 24" stroke="currentColor">
          <path stroke-linecap="round" stroke-linejoin="round" stroke-width="1" d="M20 13V6a2 2 0 00-2-2H6a2 2 0 00-2 2v7m16 0v5a2 2 0 01-2 2H6a2 2 0 01-2-2v-5m16 0h-2M4 13h2m13-4h-2M7 9h2" />
        </svg>
      </div>
      <h3 class="text-xl text-gray-600 mb-2">Bildirim Bulunamadı</h3>
      <p class="text-gray-500">Belirtilen kriterlere uygun bildirim bulunmuyor.</p>
    </div>
  {:else}
    <!-- Grid -->
    <div class="grid grid-cols-1 sm:grid-cols-2 md:grid-cols-3 lg:grid-cols-4 gap-6 mb-8">
      {#each paged as n}
        <div class="bg-white rounded-xl shadow-lg overflow-hidden hover:shadow-xl transition-shadow duration-300">
          <!-- Resim -->
          <div class="relative">
            <img
              src={"http://localhost:8000/cameras/output/" + n.image_url}
              alt="Detection thumbnail"
              class="w-full h-48 object-cover cursor-pointer hover:scale-105 transition-transform duration-300"
              on:click={() => showImage(n.image_url, n._id)}
            />
            <div class="absolute top-2 right-2">
              <span class="bg-blue-600 text-white px-2 py-1 rounded-full text-xs font-medium">
                {n.camera_id || 'Kamera'}
              </span>
            </div>
          </div>

          <!-- İçerik -->
          <div class="p-4">
            <!-- Etiketler -->
            <div class="flex flex-wrap gap-2 mb-3">
              {#each n.labels || [] as label}
                {#each Object.entries(label) as [key, val]}
                  <LabelTag labelKey={key} labelValue={val} size="sm" />
                {/each}
              {/each}
            </div>

            <!-- Zaman -->
            <p class="text-gray-600 text-sm">
              <svg xmlns="http://www.w3.org/2000/svg" class="w-4 h-4 inline mr-1" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 8v4l3 3m6-3a9 9 0 11-18 0 9 9 0 0118 0z" />
              </svg>
              {new Date(n.time).toLocaleString('tr-TR')}
            </p>
          </div>
        </div>
      {/each}
    </div>

    <!-- Pagination -->
    {#if totalPages > 1}
      <Pagination {currentPage} {totalPages} onPageChange={p => currentPage = p} />
    {/if}
  {/if}
</div>

{#if selectedImage}
  <!-- Büyük Görüntü Modalı -->
  <div class="fixed inset-0 bg-black/90 flex items-center justify-center z-[60]" on:click={closeImage}>
    <div class="relative max-w-[95vw] max-h-[95vh]" on:click|stopPropagation>
      <!-- Kapat Butonu -->
      <button
        on:click={closeImage}
        class="absolute -top-12 right-0 bg-white/20 hover:bg-white/30 text-white p-2 rounded-full backdrop-blur-md transition-all duration-200"
        aria-label="Resmi Kapat"
      >
        <svg xmlns="http://www.w3.org/2000/svg" class="w-6 h-6" fill="none" viewBox="0 0 24 24" stroke="currentColor">
          <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M6 18L18 6M6 6l12 12" />
        </svg>
      </button>

      <!-- Önceki Butonu -->
      <button
        on:click={showPreviousImage}
        class="absolute left-4 top-1/2 -translate-y-1/2 bg-white/20 hover:bg-white/30 text-white p-3 rounded-full backdrop-blur-md transition-all duration-200"
        aria-label="Önceki Resim"
      >
        <svg xmlns="http://www.w3.org/2000/svg" class="w-6 h-6" fill="none" viewBox="0 0 24 24" stroke="currentColor">
          <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M15 19l-7-7 7-7" />
        </svg>
      </button>

      <!-- Resim -->
      <img
        src={selectedImage}
        alt="Detected frame detail"
        class="max-w-full max-h-[95vh] rounded-lg shadow-2xl"
      />

      <!-- Sonraki Butonu -->
      <button
        on:click={showNextImage}
        class="absolute right-4 top-1/2 -translate-y-1/2 bg-white/20 hover:bg-white/30 text-white p-3 rounded-full backdrop-blur-md transition-all duration-200"
        aria-label="Sonraki Resim"
      >
        <svg xmlns="http://www.w3.org/2000/svg" class="w-6 h-6" fill="none" viewBox="0 0 24 24" stroke="currentColor">
          <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M9 5l7 7-7 7" />
        </svg>
      </button>
    </div>
  </div>
{/if}
