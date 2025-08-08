<!-- src/components/Table.svelte -->
<script>
  import { onMount } from "svelte";
  import { writable } from "svelte/store";
  import GlassCard from "./GlassCard.svelte";
  import NotificationModal from "./NotificationModal.svelte";
  import { modalStore } from "./store.js";
  import Pagination from "./Pagination.svelte";
  import toast from "svelte-french-toast";
  import { detectionRefresh } from "./store.js";
  import { SERVER_IP } from "./store.js";
  

  const detectionRecords = writable([]);
  let currentPage = 1;
  const recordsPerPage = 3;
  let totalRecords = 0;

  $: totalPages = Math.ceil(totalRecords / recordsPerPage);
  $: pageNumbers = (() => {
    if (!totalPages) return [];
    const max = 5;
    let start = Math.max(1, currentPage - Math.floor(max / 2));
    let end = Math.min(totalPages, start + max - 1);
    if (end - start + 1 < max) start = Math.max(1, end - max + 1);
    return Array.from({ length: end - start + 1 }, (_, i) => start + i);
  })();

  const fetchDetectionRecords = async () => {
    const skip = (currentPage - 1) * recordsPerPage;
    try {
      const res = await fetch(
        `${SERVER_IP}:8000/detection-sessions?skip=${skip}&limit=${recordsPerPage}`,
      );
      if (!res.ok) throw new Error(res.statusText);
      const data = await res.json();
      console.log("[Table] Gelen veri:", data);
      detectionRecords.set(data.records);
      totalRecords = data.total;
    } catch (e) {
      console.error("Veri alınamadı:", e);
    }
  };

  onMount(fetchDetectionRecords);
  $: currentPage, fetchDetectionRecords();
  // refresh tetiklenirse tabloyu yeniden yükle
  let refreshValue = 0;

  detectionRefresh.subscribe((value) => {
    console.log("[Table] detectionRefresh değişti:", value);
    if (value > refreshValue) {
      fetchDetectionRecords();
    }
    refreshValue = value;
  });

  const openImages = (rec) => {
    modalStore.set({
      isOpen: true,
      component: NotificationModal,
      props: {
        sessionId: rec._id,
      },
    });
  };

  const deleteSession = async (id) => {
    const confirmed = window.confirm(
      "Bu oturumu ve ilişkili tüm bildirimleri silmek istediğinize emin misiniz?",
    );
    if (!confirmed) {
      toast.dismiss();
      toast.error("Oturum silme işlemi iptal edildi.", {
        duration: 3000,
        position: "top-right",
      });
      return;
    }
    try {
      const res = await fetch(`${SERVER_IP}:8000/detection-sessions/${id}`, {
        method: "DELETE",
      });
      if (!res.ok) throw new Error(res.statusText);
      fetchDetectionRecords();
    } catch (e) {
      console.error("Silme hatası:", e);
      toast.dismiss();
      toast.error("Kayıt silinemedi.", {
        duration: 3000,
        position: "top-right",
      });
    }
  };

  const goToPage = (p) => {
    if (p >= 1 && p <= totalPages) currentPage = p;
  };

  const fmt = (iso, type = "date") => {
    const d = new Date(iso);
    return d.toLocaleString("tr-TR", {
      year: "numeric",
      month: "2-digit",
      day: "2-digit",
      hour: "2-digit",
      minute: "2-digit",
      second: "2-digit",
      hour12: false,
    });
  };

  let showModal = false;
  let modalSessionId = null;
  const closeModal = () => {
    showModal = false;
    modalSessionId = null;
  };

  const nextPage = () => goToPage(currentPage + 1);
  const prevPage = () => goToPage(currentPage - 1);
</script>

<GlassCard className="w-full h-auto p-4 flex flex-col">
  <!-- Başlık -->
  <div class="flex justify-between items-center mb-4">
    <h2 class="text-xl font-semibold text-black-900">Algılama Geçmişi</h2>
    <span class="text-sm text-gray-700">Toplam: {totalRecords}</span>
  </div>

  <!-- Tablo - Flex-1 ile kalan alanı kapla -->
  <div class="flex-1 flex flex-col min-h-0">
    <div class="overflow-hidden flex-1">
      <table class="w-full table-fixed">
        <thead>
          <tr class="bg-white/30 dark:bg-white-700/50">
            <th
              class="w-[15%] px-3 py-2 text-left text-white-900 dark:text-white-200 font-medium text-sm border-b border-white-300 dark:border-white-600"
              >Kamera ID</th
            >
            <th
              class="w-[25%] px-3 py-2 text-left text-white-900 dark:text-white-200 font-medium text-sm border-b border-white-300 dark:border-white-600"
              >Başlangıç Zamanı</th
            >
            <th
              class="w-[25%] px-3 py-2 text-left text-white-900 dark:text-white-200 font-medium text-sm border-b border-white-300 dark:border-white-600"
              >Bitiş Zamanı</th
            >
            <th
              class="w-[15%] px-3 py-2 text-left text-white-900 dark:text-white-200 font-medium text-sm border-b border-white-300 dark:border-white-600"
              >Kayıt Sayısı</th
            >
            <th
              class="w-[10%] px-3 py-2 text-center text-white-900 dark:text-white-200 font-medium text-sm border-b border-white-300 dark:border-white-600"
              >Görüntüle</th
            >
            <th
              class="w-[10%] px-3 py-2 text-center text-white-900 dark:text-white-200 font-medium text-sm border-b border-white-300 dark:border-white-600"
              >Sil</th
            >
          </tr>
        </thead>
        <tbody class="divide-y divide-white/20 dark:divide-slate-600/40">
          {#each $detectionRecords as rec}
            <tr
              class="h-16 hover:bg-white/20 dark:hover:bg-slate-700/30 transition-colors"
            >
              <td
                class="px-3 py-2 text-sm truncate text-white-700 dark:text-white-300"
                >{rec.camera_id}</td
              >
              <td class="px-3 py-2 text-sm text-white-700 dark:text-white-300">
                {rec.start ? fmt(rec.start) : "-"}
              </td>
              <td class="px-3 py-2 text-sm text-white-700 dark:text-white-300">
                {rec.end ? fmt(rec.end) : "Devam Ediyor"}
              </td>
              <td
                class="px-3 py-2 text-sm text-center text-white-700 dark:text-white-300"
              >
                {rec.record_count != null ? rec.record_count : "-"}
              </td>
              <td class="px-3 py-2 text-center">
                <button
                  on:click={() => openImages(rec)}
                  disabled={!rec.start || !rec.end}
                  class={`p-2 rounded-full transition-colors
                    ${rec.start && rec.end ? "bg-indigo-100 hover:bg-indigo-200 text-indigo-800" : "bg-gray-200 text-gray-400 cursor-not-allowed"}`}
                  aria-label="Görüntüle"
                  title={rec.end
                    ? "Bildirimleri Görüntüle"
                    : "Henüz tamamlanmamış"}
                >
                  <svg
                    xmlns="http://www.w3.org/2000/svg"
                    class="w-4 h-4"
                    fill="none"
                    viewBox="0 0 24 24"
                    stroke="currentColor"
                    stroke-width="2"
                  >
                    <path
                      stroke-linecap="round"
                      stroke-linejoin="round"
                      d="M15 12a3 3 0 11-6 0 3 3 0 016 0z"
                    />
                    <path
                      stroke-linecap="round"
                      stroke-linejoin="round"
                      d="M2.458 12C3.732 7.943 7.523 5 12 5s8.268
                             2.943 9.542 7c-1.274 4.057-5.065 7-9.542
                             7s-8.268-2.943-9.542-7z"
                    />
                  </svg>
                </button>
              </td>
              <td class="px-3 py-2 text-center">
                <button
                  on:click={() => deleteSession(rec._id)}
                  class="p-2 rounded-full bg-red-100 hover:bg-red-200 text-red-700 transition-colors"
                  aria-label="Sil"
                  title="Oturumu Sil"
                >
                  <svg
                    xmlns="http://www.w3.org/2000/svg"
                    class="w-4 h-4"
                    fill="none"
                    viewBox="0 0 24 24"
                    stroke="currentColor"
                    stroke-width="2"
                  >
                    <path
                      stroke-linecap="round"
                      stroke-linejoin="round"
                      d="M19 7l-.867 12.142A2 2 0 0116.138
                             21H7.862a2 2 0 01-1.995-1.858L5
                             7m5 4v6m4-6v6M1 7h22"
                    />
                  </svg>
                </button>
              </td>
            </tr>
          {/each}

          <!-- Boş satırlar ekleyerek tablonun yüksekliğini sabit tutuyoruz -->
          {#each Array(Math.max(0, 3 - $detectionRecords.length)) as _}
            <tr class="h-16">
              <td
                colspan="6"
                class="px-3 py-2 text-center text-gray-400 dark:text-slate-500"
              >
                {#if $detectionRecords.length === 0}
                  Kayıt bulunamadı.
                {:else}
                  &nbsp;
                {/if}
              </td>
            </tr>
          {/each}
        </tbody>
      </table>
    </div>
  </div>

  <!-- Pagination - Alt kısımda sabit -->
  <div class="mt-4 pt-4 border-t border-white-200 dark:border-slate-600/40">
    <Pagination {currentPage} {totalPages} onPageChange={goToPage} />
  </div>
</GlassCard>
