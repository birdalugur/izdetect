<!-- src/components/NotificationModal.svelte -->
<script>
  import { onMount, createEventDispatcher } from 'svelte';
  import Pagination from './Pagination.svelte';
  import LabelTag from './LabelTag.svelte';
  import toast, { Toaster } from 'svelte-french-toast';

  export let filterParams = null;
  export let sessionId = null;
  export let notificationId = null;  // Yeni prop: tek bir bildirimi göstermek için

  const dispatch = createEventDispatcher();

  let notifications = [];
  let selectedImage = null;
  let selectedNotificationId = null;
  let loading = true;
  let error = null;

  let currentPage = 1;
  let pageSize = 12;
  let totalNotifications = 0;

  $: totalPages = Math.ceil(totalNotifications / pageSize);

  // Modal'in kaynağını belirle
  $: isFromTable = sessionId !== null;
  $: isFromFilter = filterParams !== null;
  $: isFromNotification = notificationId !== null;

  onMount(() => {
    if (isFromTable) {
      fetchNotificationsBySession(1);
      // Her 5 saniyede bir güncelle (sadece mevcut sayfa değilse)
      const interval = setInterval(() => {
        if (isFromTable && currentPage === 1) {
          fetchNotificationsBySession(currentPage, false);
        }
      }, 5000);
      return () => clearInterval(interval);
    } else if (isFromFilter) {
      fetchNotificationsByDate(1);
    } else if (isFromNotification) {
      fetchSingleNotification();
    }
  });

  // Yeni fonksiyon: Tek bir bildirimi getir
  const fetchSingleNotification = async () => {
    if (!notificationId) {
      toast.error("Bildirim ID bulunamadı.", { duration: 3000, position: 'top-right' });
      return;
    }
    loading = true;
    error = null;

    try {
      const response = await fetch(`http://localhost:8000/notifications/${notificationId}`);
      if (!response.ok) {
        throw new Error(`HTTP error! status: ${response.status}`);
      }
      const data = await response.json();
      notifications = [data];  // Tek bildirimi dizi içinde sakla
      totalNotifications = 1;
      currentPage = 1;
      
      // Resmi otomatik göster
      if (data.image_url) {
        selectedImage = `http://localhost:8000/cameras/output/${data.image_url}`;
        selectedNotificationId = data._id;
      }
    } catch (error) {
      console.error("Bildirim getirme hatası:", error);
      error = error.message;
      notifications = [];
      toast.error("Bildirim bulunamadı.", { duration: 3000, position: 'top-right' });
    } finally {
      loading = false;
    }
  };

  const fetchNotificationsBySession = async (page = 1, updateLoading = true) => {
    if (!sessionId) {
      toast.error("Session ID bulunamadı.", { duration: 3000, position: 'top-right' });
      return;
    }
    if (updateLoading) {
      loading = true;
    }
    error = null;

    try {
      // Önce session bilgisini al ve toplam kayıt sayısını öğren
      const sessionResponse = await fetch(
        `http://localhost:8000/detection-sessions/${sessionId}`,
      );
      if (sessionResponse.ok) {
        const sessionData = await sessionResponse.json();
        totalNotifications = sessionData.record_count || 0;
      }

      // Sonra bildirimleri al
      const skip = (page - 1) * pageSize;
      const response = await fetch(
        `http://localhost:8000/notifications/by_session/${sessionId}?skip=${skip}&limit=${pageSize}`,
      );
      if (!response.ok) {
        throw new Error(`HTTP error! status: ${response.status}`);
      }
      const data = await response.json();
      notifications = data;
      currentPage = page;
    } catch (error) {
      error = error.message;
      notifications = [];
    } finally {
      if (updateLoading) {
        loading = false;
      }
    }
  };

  const fetchNotificationsByDate = async (page = 1) => {
    if (!filterParams || !filterParams.startDate || !filterParams.endDate) {
      return;
    }
    loading = true;
    error = null;
    const { startDate, endDate, startTime, endTime, selectedLabels } = filterParams;
    
    // Tarih formatını düzelt
    let startDateTime = startDate;
    let endDateTime = endDate;
    
    if (startTime) {
      startDateTime = `${startDate}T${startTime}`;
    } else {
      startDateTime = `${startDate}T00:00:00`;
    }
    
    if (endTime) {
      endDateTime = `${endDate}T${endTime}`;
    } else {
      endDateTime = `${endDate}T23:59:59`;
    }
    
    let labelsParam = "";
    const selectedLabelIds = [];
    if (selectedLabels.insan) selectedLabelIds.push("1");
    if (selectedLabels.arac) selectedLabelIds.push("2");
    if (selectedLabels.hayvan) selectedLabelIds.push("3");
    if (selectedLabelIds.length > 0) {
      labelsParam = selectedLabelIds.join(",");
    }
    
    try {
      const skip = (page - 1) * pageSize;
      let url = `http://localhost:8000/notifications/by_date?start_date=${encodeURIComponent(startDateTime)}&end_date=${encodeURIComponent(endDateTime)}&skip=${skip}&limit=${pageSize}`;
      let record_count_url = `http://localhost:8000/notifications/record_count?start_time=${encodeURIComponent(startDateTime)}&end_time=${encodeURIComponent(endDateTime)}`;
      // Sadece labels varsa URL'e ekle
      if (labelsParam) {
        url += `&labels=${labelsParam}`;
        record_count_url += `&labels=${labelsParam}`;
      }
      
      console.log('Fetching notifications with URL:', url);
      
      const response = await fetch(url);
      const count = await fetch(record_count_url)
      if (!response.ok) {
        throw new Error(`HTTP error! status: ${response.status}`);
      }
      const data = await response.json();
      const record_count = await count.json()
      // notifications = data.notifications;
      notifications = data;
      totalNotifications = record_count.count;
      currentPage = page;
    } catch (error) {
      console.error("Tarih filtreleme hatası:", error);
      error = error.message;
      notifications = [];
    } finally {
      loading = false;
    }
  };

  const nextPage = async () => {
    if (currentPage < totalPages) {
      if (isFromTable) {
        await fetchNotificationsBySession(currentPage + 1);
      } else if (isFromFilter) {
        await fetchNotificationsByDate(currentPage + 1);
      }
    }
  };

  const previousPage = async () => {
    if (currentPage > 1) {
      if (isFromTable) {
        await fetchNotificationsBySession(currentPage - 1);
      } else if (isFromFilter) {
        await fetchNotificationsByDate(currentPage - 1);
      }
    }
  };

  function showImage(url, id) {
    selectedNotificationId = id;
    selectedImage = `http://localhost:8000/cameras/output/${url}`;
  }

  function closeImage() {
    selectedImage = null;
    selectedNotificationId = null;
  }

  function showNextImage() {
    if (isFromTable || isFromFilter) {
      const idx = notifications.findIndex(n => n._id === selectedNotificationId);
      if (idx < 0) return;
      const next = notifications[idx + 1];
      if (next) showImage(next.image_url, next._id);
      else if (idx === notifications.length - 1 && currentPage < totalPages) {
        nextPage().then(() => {
          if (notifications.length > 0) {
            const nextNotification = notifications[0];
            showImage(nextNotification.image_url, nextNotification._id);
          }
        });
      }
    } else if (isFromNotification) {
      // Tek bildirim görüntülerken bir sonraki bildirimi getir
      fetchNextNotification();
    }
  }

  function showPreviousImage() {
    if (isFromTable || isFromFilter) {
      const idx = notifications.findIndex(n => n._id === selectedNotificationId);
      if (idx > 0) {
        const previousNotification = notifications[idx - 1];
        showImage(previousNotification.image_url, previousNotification._id);
      } else if (idx === 0 && currentPage > 1) {
        previousPage().then(() => {
          if (notifications.length > 0) {
            const previousNotification = notifications[notifications.length - 1];
            showImage(previousNotification.image_url, previousNotification._id);
          }
        });
      }
    } else if (isFromNotification) {
      // Tek bildirim görüntülerken bir önceki bildirimi getir
      fetchPreviousNotification();
    }
  }

  // Yeni fonksiyonlar: Bir sonraki/önceki bildirimi getir
  const fetchNextNotification = async () => {
    if (!selectedNotificationId) return;
    
    try {
      const response = await fetch(`http://localhost:8000/notifications/${selectedNotificationId}/around?limit=3`);
      if (!response.ok) throw new Error(`HTTP error! status: ${response.status}`);
      const aroundNotifications = await response.json();
      
      // Şu anki bildirimin indexini bul
      const currentIndex = aroundNotifications.findIndex(n => n._id === selectedNotificationId);
      if (currentIndex === -1 || currentIndex === aroundNotifications.length - 1) {
        toast.error("Son bildirim.", { duration: 2000, position: 'top-right' });
        return;
      }

      // Bir sonraki bildirimi al
      const nextNotification = aroundNotifications[currentIndex + 1];
      notifications = [nextNotification];
      totalNotifications = 1;
      currentPage = 1;
      
      // Resmi göster
      if (nextNotification.image_url) {
        selectedImage = `http://localhost:8000/cameras/output/${nextNotification.image_url}`;
        selectedNotificationId = nextNotification._id;
      }
    } catch (error) {
      console.error("Bildirim getirme hatası:", error);
      toast.error("Sonraki bildirim yüklenemedi.", { duration: 3000, position: 'top-right' });
    }
  };

  const fetchPreviousNotification = async () => {
    if (!selectedNotificationId) return;
    
    try {
      const response = await fetch(`http://localhost:8000/notifications/${selectedNotificationId}/around?limit=3`);
      if (!response.ok) throw new Error(`HTTP error! status: ${response.status}`);
      const aroundNotifications = await response.json();
      
      // Şu anki bildirimin indexini bul
      const currentIndex = aroundNotifications.findIndex(n => n._id === selectedNotificationId);
      if (currentIndex <= 0) {
        toast.error("İlk bildirim.", { duration: 2000, position: 'top-right' });
        return;
      }

      // Bir önceki bildirimi al
      const previousNotification = aroundNotifications[currentIndex - 1];
      notifications = [previousNotification];
      totalNotifications = 1;
      currentPage = 1;
      
      // Resmi göster
      if (previousNotification.image_url) {
        selectedImage = `http://localhost:8000/cameras/output/${previousNotification.image_url}`;
        selectedNotificationId = previousNotification._id;
      }
    } catch (error) {
      console.error("Bildirim getirme hatası:", error);
      toast.error("Önceki bildirim yüklenemedi.", { duration: 3000, position: 'top-right' });
    }
  };

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

  const deleteNotification = async (id) => {
    try {
      await fetch(`http://localhost:8000/notifications/${id}`, {
        method: "DELETE",
      });
      notifications = notifications.filter((n) => n._id !== id);
      totalNotifications = Math.max(0, totalNotifications - 1);
      toast.success('Bildirim silindi.', { duration: 3000, position: 'top-right' });
    } catch (error) {
      console.error("Bildirim silinemedi:", error);
      toast.error("Bildirim silinemedi.", { duration: 3000, position: 'top-right' });
    }
  };

  const deleteAllNotifications = async () => {
    if (isFromTable) {
      // Session'a göre tüm bildirimleri sil
      if (!sessionId) {
        toast.error("Session ID bulunamadı.", { duration: 3000, position: 'top-right' });
        return;
      }

      try {
        const response = await fetch(
          `http://localhost:8000/detection-sessions/${sessionId}`,
          {
            method: "DELETE",
          },
        );
        if (!response.ok) {
          throw new Error(`HTTP error! status: ${response.status}`);
        }
        const result = await response.json();
        toast.success("Session ve tüm bildirimleri silindi.", { duration: 3000, position: 'top-right' });
        notifications = [];
        totalNotifications = 0;
      } catch (error) {
        console.error("Session silinemedi:", error);
        toast.error("Session silinemedi.", { duration: 3000, position: 'top-right' });
      }
    } else if (isFromFilter) {
      if (!filterParams || !filterParams.startDate || !filterParams.endDate) {
        return;
      }

      const { startDate, endDate, startTime, endTime } = filterParams;

      const startDateTime = startTime
        ? `${startDate}T${startTime}`
        : startDate;
      const endDateTime = endTime ? `${endDate}T${endTime}` : endDate;

      try {
        const response = await fetch(
          `http://localhost:8000/notifications/by_date?start_date=${startDateTime}&end_date=${endDateTime}`,
          {
            method: "DELETE",
          },
        );
        if (!response.ok) {
          throw new Error(`HTTP error! status: ${response.status}`);
        }
        const result = await response.json();
        toast.success(result.message, { duration: 3000, position: 'top-right' });
        notifications = [];
        totalNotifications = 0;
      } catch (error) {
        console.error("Bildirimler silinemedi:", error);
        toast.error("Bildirimler silinemedi.", { duration: 3000, position: 'top-right' });
      }
    }
  };

  const deleteCurrentPageNotifications = async () => {
    if (notifications.length === 0) {
      toast.error("Silinecek bildirim yok.", { duration: 3000, position: 'top-right' });
      return;
    }

    try {
      const notificationIds = notifications.map((n) => n._id);
      const response = await fetch(
        "http://localhost:8000/notifications/batch_delete",
        {
          method: "DELETE",
          headers: {
            "Content-Type": "application/json",
          },
          body: JSON.stringify({ notification_ids: notificationIds }),
        },
      );
      if (!response.ok) {
        throw new Error(`HTTP error! status: ${response.status}`);
      }
      const result = await response.json();
      toast.success(result.message, { duration: 3000, position: 'top-right' });
      notifications = [];
      totalNotifications = Math.max(0, totalNotifications - notificationIds.length);
    } catch (error) {
      console.error("Bildirimler silinemedi:", error);
      toast.error("Bildirimler silinemedi.", { duration: 3000, position: 'top-right' });
    }
  };

  // Sayfa değiştiğinde tüm kayıtları yenile
  const goToPage = async (page) => {
    if (isFromTable) {
      await fetchNotificationsBySession(page);
    } else if (isFromFilter) {
      await fetchNotificationsByDate(page);
    }
  };
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
      {:else if notificationId}
        Bildirim Detayı
      {:else}
        Tüm Bildirimler
      {/if}
    </h2>
    <p class="text-gray-600">
      {loading ? 'Yükleniyor...' : `${totalNotifications} bildirim listelendi`}
    </p>
  </div>

  {#if loading && notifications.length === 0}
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
      {#each notifications as n}
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
    <div class="flex justify-between items-center mt-6">
      <button
        on:click={deleteAllNotifications}
        class="px-4 py-2 bg-red-500 hover:bg-red-600 text-white rounded-lg transition-colors"
      >
        Tümünü Sil
      </button>
      {#if totalNotifications > pageSize && !isFromNotification}
        <Pagination {currentPage} {totalPages} onPageChange={goToPage} />
      {/if}
    </div>
  {/if}
</div>

{#if selectedImage}
  <!-- Büyük Görüntü Modalı -->
  <div class="fixed inset-0 bg-black/20 backdrop-blur-sm z-[60] flex items-center justify-center p-4">
    <div class="relative bg-white/30 backdrop-blur-md rounded-2xl border border-white/30 shadow-xl max-w-[90vw] max-h-[90vh] overflow-hidden">
      <!-- Modal Header -->
      <div class="absolute top-0 left-0 right-0 p-4 flex justify-between items-center z-10 bg-gradient-to-b from-black/50 to-transparent">
        <h3 class="text-white text-lg font-medium">Bildirim Detayı</h3>
        <button
          on:click={closeImage}
          class="p-2 hover:bg-white/20 rounded-full transition-colors"
        >
          <svg xmlns="http://www.w3.org/2000/svg" class="h-6 w-6 text-white" fill="none" viewBox="0 0 24 24" stroke="currentColor">
            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M6 18L18 6M6 6l12 12" />
          </svg>
        </button>
      </div>

      <!-- Image Container -->
      <div class="relative flex items-center justify-center">
        <img
          src={selectedImage}
          alt="Detected frame detail"
          class="max-w-full max-h-[90vh] object-contain"
        />

        <!-- Navigation Buttons -->
        <button
          on:click={showPreviousImage}
          class="absolute left-4 top-1/2 -translate-y-1/2 p-3 bg-white/20 hover:bg-white/30 text-white rounded-full backdrop-blur-sm transition-all duration-200 group"
        >
          <svg xmlns="http://www.w3.org/2000/svg" class="w-6 h-6 group-hover:scale-110 transition-transform" fill="none" viewBox="0 0 24 24" stroke="currentColor">
            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M15 19l-7-7 7-7" />
          </svg>
        </button>

        <button
          on:click={showNextImage}
          class="absolute right-4 top-1/2 -translate-y-1/2 p-3 bg-white/20 hover:bg-white/30 text-white rounded-full backdrop-blur-sm transition-all duration-200 group"
        >
          <svg xmlns="http://www.w3.org/2000/svg" class="w-6 h-6 group-hover:scale-110 transition-transform" fill="none" viewBox="0 0 24 24" stroke="currentColor">
            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M9 5l7 7-7 7" />
          </svg>
        </button>
      </div>
    </div>
  </div>
{/if}

<style>
  /* Add any additional styles here */
</style>
