<script>
  import GlassCard from "./GlassCard.svelte";
  import { writable } from "svelte/store";
  import { modalStore, SERVER_IP } from "./store.js";
  import { onMount } from "svelte";
  import toast, { Toaster } from "svelte-french-toast";

  let cameraList = writable([]);
  let selectedCamera = writable(null);
  const defaultStreamUrl = SERVER_IP + ":8000/cameras/video";
  let videoSrc = "";
  let loading = true;

  const fetchCameras = async () => {
    try {
      const response = await fetch(SERVER_IP + ":8000/cameras/get-cameras");
      if (response.ok) {
        const cams = await response.json();
        cameraList.set(cams);
        if (cams.length > 0) selectedCamera.set(cams[0]);
      }
    } catch (e) {
      console.error("Kameralar alınırken hata:", e);
    }
  };

  const setVideoSrc = () => {
    const cam = $selectedCamera;
    videoSrc = cam
      ? `${SERVER_IP}:8000/cameras/video/${cam.id}?t=${Date.now()}`
      : defaultStreamUrl;
    loading = true;
  };

  $: $selectedCamera, setVideoSrc();

  const handleError = () => {
    loading = true;
    console.warn("Akış koptu. Yeniden bağlanılıyor...");
    setTimeout(setVideoSrc, 3000);
  };

  const handleLoad = () => {
    loading = false;
  };

  const toggleFullscreen = () => {
    modalStore.set({
      isOpen: true,
      component: "fullscreen-image",
      props: {
        imageSrc: videoSrc,
        altText: $selectedCamera?.name || "IP Kamera Tam Ekran",
        onError: handleError,
      },
    });
  };

  const selectCamera = (cam) => selectedCamera.set(cam);

  // We no longer manage cameras here (add/delete), it's done in CameraPanel via Sidebar.

  fetchCameras();
</script>

<GlassCard className="mx-auto p-0 overflow-hidden">
  <div class="flex">
    <!-- Controls Sidebar -->
    <div class="flex flex-col gap-4 p-4">
      {#each $cameraList as cam}
        <div class="relative group">
          <button
            on:click={() => selectCamera(cam)}
            class={`p-3 rounded-full transition shadow-md ${
              $selectedCamera?.id === cam.id
                ? "bg-blue-600 text-white border-2 border-blue-400 shadow-blue-500/50"
                : "bg-slate-100/90 dark:bg-slate-600/80 text-slate-700 dark:text-slate-200 border-2 border-slate-300 dark:border-slate-500 hover:bg-slate-200/90 dark:hover:bg-slate-500/80 hover:border-slate-400 dark:hover:border-slate-400 hover:shadow-lg"
            }`}
            title={`${cam.name || cam.id} - ${cam.ip}`}
          >
            <svg
              xmlns="http://www.w3.org/2000/svg"
              class="w-6 h-6"
              fill="none"
              viewBox="0 0 24 24"
              stroke="currentColor"
            >
              <path
                stroke-linecap="round"
                stroke-linejoin="round"
                stroke-width="2"
                d="M15 10l4.553-2.276A1 1 0 0121 8.618v6.764a1 1 0 01-1.447.894L15 14M5 18h8a2 2 0 002-2V8a2 2 0 00-2-2H5a2 2 0 00-2 2v8a2 2 0 002 2z"
              />
            </svg>
          </button>
        </div>
      {/each}
    </div>

    <!-- Video Display -->
    <div
      class="flex-1 relative border border-white/30 rounded-xl overflow-hidden"
    >
      <h4
        class="absolute top-2 left-2 bg-blue-500/50 text-white text-sm font-semibold px-2 py-1 rounded-md z-10"
      >
        {$selectedCamera?.name || `Kamera ${$selectedCamera?.id}`}
      </h4>
      {#if loading}
        <div
          class="absolute inset-0 flex items-center justify-center bg-white/70 z-20"
        >
          <svg class="animate-spin-slow h-16 w-16" viewBox="0 0 50 50">
            <defs>
              <linearGradient
                id="spinner-gradient"
                x1="0%"
                y1="0%"
                x2="100%"
                y2="100%"
              >
                <stop offset="0%" stop-color="#3b82f6" />
                <stop offset="100%" stop-color="#06b6d4" />
              </linearGradient>
            </defs>
            <circle
              cx="25"
              cy="25"
              r="20"
              fill="none"
              stroke="url(#spinner-gradient)"
              stroke-width="6"
              stroke-linecap="round"
              stroke-dasharray="90 60"
              stroke-dashoffset="0"
              style="filter: blur(0.5px); opacity: 0.9;"
            />
          </svg>
        </div>
      {/if}
      <img
        src={videoSrc}
        alt="IP Kamera Canlı Yayını"
        class="w-full h-auto aspect-video object-cover cursor-pointer transition-transform duration-200 hover:scale-[1.01]"
        on:click={toggleFullscreen}
        on:error={handleError}
        on:load={handleLoad}
        style="display: block;"
      />
    </div>
  </div>
</GlassCard>

<!-- Modal artık global Modal.svelte tarafından yönetiliyor -->

<style>
  @keyframes spin-slow {
    100% {
      transform: rotate(360deg);
    }
  }
  .animate-spin-slow {
    animation: spin-slow 1.2s linear infinite;
  }
</style>
