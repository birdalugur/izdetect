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

<div class="bg-gray-100 p-2 rounded-lg shadow-lg mx-auto mt-2">
    <!-- svelte-ignore a11y-click-events-have-key-events -->
    <div class="relative w-full max-w-3xl border-2 border-gray-300 rounded-lg overflow-hidden text-center m-px z-[1]">
        <h4 class="m-1 bg-blue-100 rounded px-2 py-1 text-sm font-semibold">Cam - 2</h4>
        <img
            class="w-full max-w-5xl rounded-lg mx-auto cursor-pointer"
            src={$selectedCamera
                ? `http://localhost:8000/cameras/video/${$selectedCamera.id}`
                : defaultStreamUrl}
            alt="IP Kamera Canli Yayini"
            on:click={toggleFullscreen}
        />

        {#if isFullscreen}
            <div class="fixed inset-0 bg-black bg-opacity-80 flex justify-center items-center z-[100]" on:click={toggleFullscreen}>
                <img
                    class="max-w-[90%] max-h-[90%] rounded-lg"
                    src={`http://localhost:8000/cameras/video/${$selectedCamera.id}`}
                    alt="IP Kamera Tam Ekran"
                />
                <button
                    class="absolute top-5 right-5 bg-white/80 hover:bg-white text-black rounded-full px-3 py-2 text-lg font-bold transition-all duration-300"
                    on:click={toggleFullscreen}
                >
                    ✕
                </button>
            </div>
        {/if}
    </div>

    <div class="flex justify-center gap-2 mt-3 flex-wrap">
        {#each $cameraList as cam}
            <button
                class={`px-4 py-2 border-2 rounded-lg transition-all duration-300 font-medium shadow-md 
                ${$selectedCamera?.id === cam.id
                    ? 'bg-blue-500 text-white border-blue-700 transform -translate-y-0.5'
                    : 'bg-gray-100 text-blue-600 border-blue-500 hover:bg-blue-500 hover:text-white hover:border-blue-700 hover:-translate-y-0.5'}
                focus:outline-none focus:ring-2 focus:ring-blue-400`}
                on:click={() => selectCamera(cam)}
            >
                {cam.id}
            </button>
        {/each}

        <button
            class="ml-auto px-4 py-2 border-2 border-blue-500 bg-gray-100 text-blue-600 rounded-lg font-medium shadow-md hover:bg-blue-500 hover:text-white transition-all duration-300"
            on:click={toggleCameraForm}
        >
            Kamera Yönetimi
        </button>
    </div>

    {#if $showCameraForm}
        <!-- svelte-ignore a11y-click-events-have-key-events -->
        <div class="modal-overlay fixed inset-0 bg-black bg-opacity-50 flex justify-center items-center z-[100]" on:click={closeCameraForm}>
            <div class="bg-white p-5 rounded-lg w-[400px] max-w-[90%] shadow-lg" on:click|stopPropagation>
                <CamForm />
            </div>
        </div>
    {/if}
</div>
