<!-- src/components/Modal.svelte -->
<script>
  import { modalStore } from "./store.js";
  import { onDestroy } from "svelte";
  import { SERVER_IP } from "./store.js";

  // Manuel abonelik (eğer template içinde direkt $modalStore kullanmak istemezseniz)
  let modalValue;
  const unsubscribe = modalStore.subscribe((value) => {
    modalValue = value;
  });
  onDestroy(unsubscribe);

  function closeModal() {
    modalStore.set({ isOpen: false, component: null, props: {} });
  }

  // Image navigation için
  function navigateImage(direction) {
    if (
      modalValue.component !== "imageViewer" ||
      !modalValue.props.notifications
    )
      return;

    const notifications = modalValue.props.notifications;
    const currentId = modalValue.props.currentNotificationId;
    const currentIdx = notifications.findIndex((n) => n._id === currentId);

    if (currentIdx < 0) return;

    let newIdx = currentIdx + direction;
    if (newIdx < 0) newIdx = notifications.length - 1;
    if (newIdx >= notifications.length) newIdx = 0;

    const newNotification = notifications[newIdx];
    if (newNotification) {
      modalStore.set({
        isOpen: true,
        component: "imageViewer",
        props: {
          imageUrl: `${SERVER_IP}:8000/cameras/output/${newNotification.image_url}`,
          notifications: notifications,
          currentNotificationId: newNotification._id,
        },
      });
    }
  }

  // ESC tuşu ile modalı kapat
  function handleKeydown(event) {
    if (event.key === "Escape" && modalValue.isOpen) {
      closeModal();
    } else if (modalValue.component === "imageViewer" && modalValue.isOpen) {
      if (event.key === "ArrowLeft") {
        navigateImage(-1);
      } else if (event.key === "ArrowRight") {
        navigateImage(1);
      }
    }
  }
</script>

<svelte:window on:keydown={handleKeydown} />

{#if modalValue.isOpen}
  <div
    class="fixed inset-0 z-50 bg-black/50 backdrop-blur-sm"
    on:click={closeModal}
    on:keydown={(e) => e.key === "Escape" && closeModal()}
    tabindex="0"
    role="button"
    aria-label="Modal kapatmak için tıklayın"
  >
    {#if modalValue.component === "fullscreen-image"}
      <!-- Tam ekran görüntü modalı -->
      <div
        class="fixed inset-0 bg-black/90 flex justify-center items-center animate-fade-in"
        on:click|stopPropagation
        on:keydown={(e) => e.key === "Escape" && closeModal()}
        tabindex="0"
        role="dialog"
        aria-label="Resim görüntüleyici"
      >
        <img
          src={modalValue.props.imageSrc}
          alt={modalValue.props.altText}
          class="max-w-full max-h-full object-contain"
          on:error={modalValue.props.onError}
        />
        <button
          class="absolute top-4 right-4 z-[70] w-12 h-12 flex items-center justify-center bg-white/80 hover:bg-white text-black rounded-full shadow-2xl hover:scale-110 transition-all duration-200"
          on:click={closeModal}
          aria-label="Modalı Kapat (ESC)"
          title="Modalı Kapat (ESC tuşu)"
        >
          <svg
            xmlns="http://www.w3.org/2000/svg"
            class="h-6 w-6"
            fill="none"
            viewBox="0 0 24 24"
            stroke="currentColor"
            stroke-width="2.5"
          >
            <path
              stroke-linecap="round"
              stroke-linejoin="round"
              d="M6 18L18 6M6 6l12 12"
            />
          </svg>
        </button>
      </div>
    {:else if modalValue.component === "imageViewer"}
      <!-- Notification Image Viewer modalı -->
      <div
        class="fixed inset-0 bg-black/90 flex justify-center items-center animate-fade-in"
        on:click|stopPropagation
        on:keydown={(e) => e.key === "Escape" && closeModal()}
        tabindex="0"
        role="dialog"
        aria-label="Bildirim resim görüntüleyici"
      >
        <div class="relative">
          <!-- Kapat butonu -->
          <button
            class="absolute top-4 right-4 z-[70] w-12 h-12 flex items-center justify-center bg-white/80 hover:bg-white text-black rounded-full shadow-2xl hover:scale-110 transition-all duration-200"
            on:click={closeModal}
            aria-label="Modalı Kapat (ESC)"
            title="Modalı Kapat (ESC tuşu)"
          >
            <svg
              xmlns="http://www.w3.org/2000/svg"
              class="h-6 w-6"
              fill="none"
              viewBox="0 0 24 24"
              stroke="currentColor"
              stroke-width="2.5"
            >
              <path
                stroke-linecap="round"
                stroke-linejoin="round"
                d="M6 18L18 6M6 6l12 12"
              />
            </svg>
          </button>

          <!-- Önceki resim butonu -->
          <button
            class="absolute left-4 top-1/2 -translate-y-1/2 z-[70] w-12 h-12 flex items-center justify-center bg-white/80 hover:bg-white text-black rounded-full shadow-2xl hover:scale-110 transition-all duration-200"
            on:click={() => navigateImage(-1)}
            aria-label="Önceki Resim"
            title="Önceki Resim"
          >
            <svg
              xmlns="http://www.w3.org/2000/svg"
              class="h-6 w-6"
              fill="none"
              viewBox="0 0 24 24"
              stroke="currentColor"
              stroke-width="2.5"
            >
              <path
                stroke-linecap="round"
                stroke-linejoin="round"
                d="M15 19l-7-7 7-7"
              />
            </svg>
          </button>

          <!-- Ana resim -->
          <img
            src={modalValue.props.imageUrl}
            alt="Detection frame"
            class="max-w-full max-h-[90vh] object-contain rounded-lg shadow-2xl"
          />

          <!-- Sonraki resim butonu -->
          <button
            class="absolute right-4 top-1/2 -translate-y-1/2 z-[70] w-12 h-12 flex items-center justify-center bg-white/80 hover:bg-white text-black rounded-full shadow-2xl hover:scale-110 transition-all duration-200"
            on:click={() => navigateImage(1)}
            aria-label="Sonraki Resim"
            title="Sonraki Resim"
          >
            <svg
              xmlns="http://www.w3.org/2000/svg"
              class="h-6 w-6"
              fill="none"
              viewBox="0 0 24 24"
              stroke="currentColor"
              stroke-width="2.5"
            >
              <path
                stroke-linecap="round"
                stroke-linejoin="round"
                d="M9 5l7 7-7 7"
              />
            </svg>
          </button>
        </div>
      </div>
    {:else if modalValue.isSmallModal}
      <!-- Küçük modal (CamForm için) -->
      <div
        class="fixed inset-0 flex items-center justify-center p-4 animate-fade-in"
        on:click|stopPropagation
        on:keydown={(e) => e.key === "Escape" && closeModal()}
        tabindex="0"
        role="dialog"
        aria-label="Küçük modal"
      >
        <div
          class="bg-white/95 backdrop-blur-md rounded-2xl shadow-2xl border border-white/30 w-full max-w-2xl max-h-[80vh] overflow-auto relative"
        >
          <button
            class="absolute top-4 right-4 z-[70] w-10 h-10 flex items-center justify-center bg-red-500 hover:bg-red-600 text-white rounded-full shadow-lg hover:scale-110 transition-all duration-200"
            on:click={closeModal}
            aria-label="Modalı Kapat (ESC)"
            title="Modalı Kapat (ESC tuşu)"
          >
            <svg
              xmlns="http://www.w3.org/2000/svg"
              class="h-5 w-5"
              fill="none"
              viewBox="0 0 24 24"
              stroke="currentColor"
              stroke-width="2.5"
            >
              <path
                stroke-linecap="round"
                stroke-linejoin="round"
                d="M6 18L18 6M6 6l12 12"
              />
            </svg>
          </button>

          <div class="p-6">
            {#if modalValue.component}
              <svelte:component
                this={modalValue.component}
                {...modalValue.props}
                on:close={closeModal}
              />
            {/if}
          </div>
        </div>
      </div>
    {:else}
      <!-- Tam ekran modal (diğer modallar için) -->
      <div
        class="fixed inset-0 bg-white overflow-auto animate-fade-in"
        on:click|stopPropagation
        on:keydown={(e) => e.key === "Escape" && closeModal()}
        tabindex="0"
        role="dialog"
        aria-label="Tam ekran modal"
      >
        <button
          class="fixed top-6 right-6 z-[70] w-14 h-14 flex items-center justify-center bg-red-500 hover:bg-red-600 text-white rounded-full shadow-2xl hover:scale-110 transition-all duration-200"
          on:click={closeModal}
          aria-label="Modalı Kapat (ESC)"
          title="Modalı Kapat (ESC tuşu)"
        >
          <svg
            xmlns="http://www.w3.org/2000/svg"
            class="h-8 w-8"
            fill="none"
            viewBox="0 0 24 24"
            stroke="currentColor"
            stroke-width="2.5"
          >
            <path
              stroke-linecap="round"
              stroke-linejoin="round"
              d="M6 18L18 6M6 6l12 12"
            />
          </svg>
        </button>

        {#if modalValue.component}
          <div class="w-full h-full">
            <svelte:component
              this={modalValue.component}
              {...modalValue.props}
              on:close={closeModal}
            />
          </div>
        {/if}
      </div>
    {/if}
  </div>
{/if}

<style>
  .animate-fade-in {
    animation: fadeIn 0.2s ease-out forwards;
  }
  @keyframes fadeIn {
    from {
      opacity: 0;
      transform: scale(0.98);
    }
    to {
      opacity: 1;
      transform: scale(1);
    }
  }
</style>
