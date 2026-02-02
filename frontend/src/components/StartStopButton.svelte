<script>
  import { onMount } from "svelte";
  import { SERVER_IP, cameraUrls, clearCameraUrls } from "./store.js";
  import { detectionRefresh } from "./store.js";
  import toast from "svelte-french-toast";

  export let addMessage = () => {};

  let isActive = false;
  let isStarting = false;
  let isStopping = false;

  // Check if system is running
  const checkSystemState = async () => {
    try {
      const response = await fetch(SERVER_IP + ":8000/cameras/isrunning");
      const data = await response.json();
      if (response.ok) {
        isActive = data.is_running;
        if (isActive) {
          // If system is running, get the camera URLs
          const cameras = await fetch(SERVER_IP + ":8000/cameras/get-cameras");
          const camerasData = await cameras.json();
          if (cameras.ok && camerasData.length > 0) {
            cameraUrls.set({
              cameraUrl2: `${SERVER_IP}:8000/cameras/video/${camerasData[0].id}`,
            });
          }
        }
      }
    } catch (error) {
      console.error("Error checking system state:", error);
    }
  };

  onMount(() => {
    checkSystemState();
  });

  const startRealTimeDetection = async () => {
    isStarting = true;
    const startMessage = "Starting real-time video processing...";
    addMessage(startMessage);
    try {
      const response = await fetch(
        SERVER_IP + ":8000/cameras/start-detection",
        {
          method: "POST",
          headers: { "Content-Type": "application/json" },
          body: JSON.stringify({
            memory: 50,
            sensitivity: 0.5,
          }),
        },
      );
      const data = await response.json();
      const message = response.ok
        ? data.message
        : `Could not start: ${data.error || response.statusText}`;
      if (response.ok) {
        const stateResponse = await fetch(
          SERVER_IP + ":8000/cameras/isrunning",
        );
        const stateData = await stateResponse.json();
        isActive = stateData.is_running;
        if (isActive) {
          cameraUrls.set({ cameraUrl2: data.default_camera_url });
        }
      }
      addMessage(message);
    } catch (error) {
      addMessage(`Error: ${error.message}`);
    } finally {
      isStarting = false;
      detectionRefresh.update((n) => n + 1);
    }
  };

  const stopRealTimeDetection = async () => {
    isStopping = true;
    const stopMessage = "Stopping frame producer...";
    addMessage(stopMessage);
    try {
      const response = await fetch(SERVER_IP + ":8000/cameras/stop-detection", {
        method: "POST",
      });
      const data = await response.json();
      const message = response.ok
        ? data.message
        : `Could not stop: ${data.error || response.statusText}`;
      if (response.ok) {
        const stateResponse = await fetch(
          SERVER_IP + ":8000/cameras/isrunning",
        );
        const stateData = await stateResponse.json();
        isActive = stateData.is_running;
        if (!isActive) {
          clearCameraUrls();
        }
      }
      addMessage(message);
    } catch (error) {
      addMessage(`Error: ${error.message}`);
    } finally {
      isStopping = false;
      detectionRefresh.update((n) => n + 1);
    }
  };
</script>

<div class="flex justify-center">
  <button
    type="button"
    on:click={isActive ? stopRealTimeDetection : startRealTimeDetection}
    disabled={isStarting || isStopping}
    aria-pressed={isActive}
    aria-label={isActive ? "Durdur" : "Başlat"}
    class="p-3 rounded-full transition-all duration-200 shadow-md border-2 flex items-center justify-center
    {isStarting || isStopping ? 'bg-gray-300 border-gray-400 text-gray-600 dark:bg-gray-600 dark:border-gray-500 dark:text-gray-400 cursor-not-allowed' : 
    isActive ? 'bg-red-500 hover:bg-red-600 text-white border-red-600 hover:border-red-700 dark:bg-red-600 dark:hover:bg-red-700 dark:border-red-700 dark:hover:border-red-800 hover:shadow-lg' : 
    'bg-green-500 hover:bg-green-600 text-white border-green-600 hover:border-green-700 dark:bg-green-600 dark:hover:bg-green-700 dark:border-green-700 dark:hover:border-green-800 hover:shadow-lg'}"
    title={isActive ? "Sistemi Durdur" : "Sistemi Başlat"}
  >
    {#if isStarting || isStopping}
      <!-- Dönen yükleme spineri -->
      <svg
        xmlns="http://www.w3.org/2000/svg"
        class="w-5 h-5 animate-spin"
        fill="none"
        viewBox="0 0 24 24"
        stroke="currentColor"
      >
        <circle
          cx="12"
          cy="12"
          r="10"
          stroke="currentColor"
          stroke-width="4"
          stroke-opacity="0.2"
        />
        <path
          d="M4 12a8 8 0 018-8"
          stroke="currentColor"
          stroke-width="4"
          stroke-linecap="round"
        />
      </svg>
    {:else if isActive}
      <!-- Durdurma ikonu - Kare (Stop) -->
      <svg
        xmlns="http://www.w3.org/2000/svg"
        class="w-5 h-5"
        fill="currentColor"
        viewBox="0 0 24 24"
      >
        <rect x="6" y="6" width="12" height="12" rx="1" />
      </svg>
    {:else}
      <!-- Başlatma ikonu - Play (Üçgen) -->
      <svg
        xmlns="http://www.w3.org/2000/svg"
        class="w-5 h-5"
        fill="currentColor"
        viewBox="0 0 24 24"
      >
        <path d="M8 5l11 7-11 7z" />
      </svg>
    {/if}
  </button>
</div>
