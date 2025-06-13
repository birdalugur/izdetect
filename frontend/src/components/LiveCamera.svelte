<script>
    import { onMount } from "svelte";
    import { writable } from "svelte/store";
    import CamForm from "./CamForm.svelte";

    let cameraList = writable([]);
    let selectedCamera = writable(null);
    let showCameraForm = writable(false);
    const defaultStreamUrl = "http://localhost:8000/cameras/video";
    let isFullscreen = false;

    const toggleFullscreen = () => {
        isFullscreen = !isFullscreen;
    };

    const fetchCameras = async () => {
        try {
            const response = await fetch("http://localhost:8000/cameras/get-cameras");
            if (response.ok) {
                const cameras = await response.json();
                cameraList.set(cameras);
                if (cameras.length > 0) {
                    selectedCamera.set(cameras[0]);
                }
            }
        } catch (error) {
            console.error("Kameralar alinirken hata oluştu:", error);
        }
    };

    const selectCamera = (camera) => {
        selectedCamera.set(camera);
    };

    const toggleCameraForm = () => {
        showCameraForm.set(!$showCameraForm);
    };

    const closeCameraForm = (event) => {
        if (event.target.classList.contains("modal-overlay")) {
            showCameraForm.set(false);
        }
    };

    onMount(fetchCameras);
</script>

<div class="bg-gradient-to-b bg-gray-100 p-1 rounded-2xl mx-auto max-w-4xl border border-gray-300 relative overflow-hidden">
    <!-- Üst gradient gölge efekti -->
    <div class="absolute top-0 left-0 w-full h-4 bg-gradient-to-b from-gray-300 via-transparent to-transparent rounded-t-2xl z-0"></div>

    <!-- Video Görüntüsü -->
    <div class="relative border border-gray-300 rounded-xl overflow-hidden z-10">
        <h4 class="absolute top-2 left-2 bg-blue-100 text-blue-800 text-xs font-semibold px-2 py-1 rounded-md z-10">
            {$selectedCamera?.name || 'Cam - 2'}
        </h4>

        <!-- svelte-ignore a11y-click-events-have-key-events -->
        <img
            class="w-full h-auto aspect-video object-cover cursor-pointer transition-transform duration-200 hover:scale-[1.01]"
            src={$selectedCamera
                ? `http://localhost:8000/cameras/video/${$selectedCamera.id}`
                : defaultStreamUrl}
            alt="IP Kamera Canli Yayini"
            on:click={toggleFullscreen}
        />

        {#if isFullscreen}
            <!-- svelte-ignore a11y-click-events-have-key-events -->
            <div class="fixed inset-0 bg-black bg-opacity-90 flex justify-center items-center z-[100]" on:click={toggleFullscreen}>
                <img
                    class="max-w-[90%] max-h-[90%] rounded-xl"
                    src={`http://localhost:8000/cameras/video/${$selectedCamera.id}`}
                    alt="IP Kamera Tam Ekran"
                />
                <button
                    class="absolute top-6 right-6 bg-white/80 hover:bg-white text-black rounded-full px-3 py-1.5 text-lg font-bold  transition-all duration-300"
                    on:click={toggleFullscreen}
                >
                    ✕
                </button>
            </div>
        {/if}
    </div>

    <!-- Kamera seçim butonları -->
    <div class="flex flex-wrap justify-center gap-2">
        {#each $cameraList as cam}
            <button
                class={`px-3 py-1.5 text-xs rounded-full font-medium border transition-all duration-300 shadow 
                ${$selectedCamera?.id === cam.id
                    ? 'bg-blue-600 text-white border-blue-700 scale-105'
                    : 'bg-gray-100 text-blue-600 border-blue-400 hover:bg-blue-500 hover:text-white hover:border-blue-700 hover:scale-105'}
                focus:outline-none focus:ring-1 focus:ring-blue-400`}
                on:click={() => selectCamera(cam)}
            >
                {cam.name || `Kamera ${cam.id}`}
            </button>
        {/each}

        <!-- Kamera Yönetimi Butonu -->
        <button
            class="px-3 py-1.5 text-xs border border-blue-500 bg-white text-blue-600 rounded-full font-medium shadow hover:bg-blue-500 hover:text-white transition-all duration-300"
            on:click={toggleCameraForm}
        >
            Kamera Yönetimi
        </button>
    </div>

    <!-- svelte-ignore a11y-click-events-have-key-events -->
    {#if $showCameraForm}
        <div class="modal-overlay fixed inset-0 bg-black/50 flex justify-center items-center z-[100]" on:click={closeCameraForm}>
            <div class="bg-white p-5 rounded-2xl w-[400px] max-w-[90%] shadow-2xl border border-gray-200" on:click|stopPropagation>
                <CamForm />
            </div>
        </div>
    {/if}
</div>