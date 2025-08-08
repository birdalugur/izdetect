<!-- src/components/Notifications.svelte -->
<script>
  import { onMount } from "svelte";
  import GlassCard from "./GlassCard.svelte";
  import LabelTag from "./LabelTag.svelte";
  import { modalStore, SERVER_IP } from "./store.js";
  import toast from "svelte-french-toast";
  import NotificationModal from "./NotificationModal.svelte";

  let notifications = [];
  const MAX_NOTIFICATIONS = 48;

  // Bildirimleri fetch et
  async function fetchNotifications() {
    const res = await fetch(SERVER_IP + ":8000/notifications");
    const data = await res.json();
    notifications = data.reverse().slice(0, MAX_NOTIFICATIONS);
  }

  // SSE ile canlı bildirim ve ses
  const notificationSound = new Audio("/sounds/notification.mp3");
  function setupEventSource() {
    const eventSource = new EventSource(SERVER_IP + ":8000/cameras/events");
    eventSource.onmessage = (event) => {
      try {
        const data = JSON.parse(event.data);
        notifications = [data, ...notifications].slice(0, MAX_NOTIFICATIONS);
        notificationSound.play();
      } catch (e) {
        console.error("Hata: Gelen veri JSON formatında değil!", e);
      }
    };
    eventSource.onerror = (err) => {
      console.error("SSE bağlantı hatası!", err);
      eventSource.close();
      setTimeout(setupEventSource, 3000);
    };
  }

  onMount(() => {
    fetchNotifications();
    setupEventSource();
  });

  async function removeAll() {
    const confirmed = window.confirm(
      "Tüm bildirimleri silmek istediğinize emin misiniz?",
    );
    if (!confirmed) {
      toast.dismiss();
      toast.error("Tüm bildirimleri silme işlemi iptal edildi.", {
        duration: 3000,
        position: "top-right",
      });
      return;
    }
    await fetch(`${SERVER_IP}:8000/notifications/clear-all`, {
      method: "POST",
    });

    notifications = [];
  }

  async function removeOne(id) {
    await fetch(`${SERVER_IP}:8000/notifications/${id}`, {
      method: "DELETE",
    });
    notifications = notifications.filter((n) => n._id !== id);
  }

  // Resim görüntüleme modalını aç
  function showImage(url, id) {
    modalStore.set({
      isOpen: true,
      component: NotificationModal,
      props: {
        notificationId: id,
      },
    });
  }
</script>

<GlassCard className="flex flex-col">
  <!-- Başlık ve Tümünü Sil -->
  <div class="flex justify-between items-center mb-4">
    <h3 class="text-xl font-semibold text-white-800 dark:text-black-200">
      Bildirimler
    </h3>
    <button
      on:click={removeAll}
      class="flex items-center gap-2 px-4 py-2 rounded-lg font-semibold transition-all duration-200 hover:scale-105 shadow-md
             bg-gradient-to-r from-red-500 to-red-600 hover:from-red-600 hover:to-red-700
             dark:from-red-600 dark:to-red-700 dark:hover:from-red-700 dark:hover:to-red-800
             text-white border border-red-300 dark:border-red-500"
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
          d="M19 7l-.867 12.142A2 2 0 0116.138 21H7.862a2 2 0 01-1.995-1.858L5 7m5 4v6m4-6v6M1 7h22"
        />
      </svg>
      <span>Tümünü Sil</span>
    </button>
  </div>

  <!-- Grid -->
  <div class="max-h-[calc(100vh-200px)] overflow-y-auto glass-scroll">
    <div class="grid grid-cols-1 sm:grid-cols-2 gap-4 p-1">
      {#if notifications.length === 0}
        <p class="col-span-full text-center text-gray-500 mt-8">
          Gösterilecek bildirim yok.
        </p>
      {:else}
        {#each notifications as n}
          <div
            class="relative bg-[rgba(255,255,255,0.5)] backdrop-blur rounded-lg p-3 shadow hover:scale-[1.02] transition"
          >
            <!-- Sil butonu -->
            <button
              on:click={() => removeOne(n._id)}
              class="absolute top-2 right-2 text-red-600 hover:text-white hover:bg-red-600 p-1 rounded-full transition"
              aria-label="Sil"
            >
              <svg
                xmlns="http://www.w3.org/2000/svg"
                class="w-5 h-5"
                fill="none"
                viewBox="0 0 24 24"
                stroke="currentColor"
                stroke-width="2"
              >
                <path
                  stroke-linecap="round"
                  stroke-linejoin="round"
                  d="M6 18L18 6M6 6l12 12"
                />
              </svg>
            </button>

            <!-- Etiketler -->
            <div class="flex flex-wrap gap-2 mb-2">
              {#each n.labels as label}
                {#each Object.entries(label) as [key, val]}
                  <LabelTag labelKey={key} labelValue={val} size="sm" />
                {/each}
              {/each}
            </div>

            <!-- Küçük resim -->
            <img
              src={`${SERVER_IP}:8000/cameras/output/${n.image_url}`}
              alt="Thumbnail"
              class="w-full rounded-md mb-2 cursor-pointer"
              on:click={() => showImage(n.image_url, n._id)}
              on:keydown={(e) =>
                e.key === "Enter" && showImage(n.image_url, n._id)}
              tabindex="0"
              role="button"
            />

            <!-- Zaman -->
            <p class="text-gray-600 text-xs text-center">
              {n.time.split(".")[0]}
            </p>
          </div>
        {/each}
      {/if}
    </div>
  </div>
</GlassCard>

<style>
  .glass-btn {
    background: rgba(255, 255, 255, 0.35);
    backdrop-filter: blur(12px) saturate(180%);
    -webkit-backdrop-filter: blur(12px) saturate(180%);
    border-radius: 9999px;
    box-shadow: 0 4px 24px 0 rgba(31, 38, 135, 0.18);
    border: 1.5px solid rgba(255, 255, 255, 0.35);
    transition:
      background 0.2s,
      box-shadow 0.2s,
      color 0.2s;
  }
  .glass-btn:hover {
    background: rgba(239, 68, 68, 0.7);
    color: #fff;
  }
  .glass-scroll::-webkit-scrollbar {
    width: 8px;
    height: 8px;
    background: transparent;
  }
  .glass-scroll::-webkit-scrollbar-thumb {
    background: rgba(31, 38, 135, 0.12);
    border-radius: 8px;
  }
  .glass-scroll::-webkit-scrollbar-track {
    background: rgba(255, 255, 255, 0.1);
    border-radius: 8px;
  }
</style>
