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
    <div class="camera-container" class:isFullscreen>
        <h4>Cam - 2</h4>
        <img
            class="camera-view"
            src={$selectedCamera
                ? `http://localhost:8000/cameras/video/${$selectedCamera.id}`
                : defaultStreamUrl}
            alt="IP Kamera Canli Yayini"
            on:click={toggleFullscreen}
        />
        {#if isFullscreen}
            <div class="fullscreen-overlay" on:click={toggleFullscreen}>
                <img
                    class="fullscreen-video"
                    src={`http://localhost:8000/cameras/video/${$selectedCamera.id}`}
                    alt="IP Kamera Tam Ekran"
                />
                <button class="close-btn" on:click={toggleFullscreen}>✕</button>
            </div>
        {/if}
    </div>

    <div class="camera-selector">
        {#each $cameraList as cam}
            <button
                class="camera-button {$selectedCamera?.id === cam.id
                    ? 'active'
                    : ''}"
                on:click={() => selectCamera(cam)}
            >
                {cam.id}
            </button>
        {/each}
        <button
            class="camera-button ml-auto"
            on:click={toggleCameraForm}>Kamera Yönetimi</button
        >
    </div>

    {#if $showCameraForm}
        <!-- svelte-ignore a11y-click-events-have-key-events -->
        <div class="modal-overlay" on:click={closeCameraForm}>
            <div class="modal-content" on:click|stopPropagation>
                <CamForm />
            </div>
        </div>
    {/if}
</div>

<style>
    .modal-overlay {
        position: fixed;
        top: 0;
        left: 0;
        width: 100vw;
        height: 100vh;
        background: rgba(0, 0, 0, 0.5);
        display: flex;
        justify-content: center;
        align-items: center;
        z-index: 100;
    }

    .modal-content {
        background: white;
        padding: 20px;
        border-radius: 8px;
        width: 400px;
        max-width: 90%;
        box-shadow: 0px 4px 6px rgba(0, 0, 0, 0.1);
    }

    .camera-container {
        position: relative;
        width: 100%;
        height: 50%;
        max-width: 800px;
        border: 2px solid #ddd;
        border-radius: 8px;
        overflow: hidden;
        text-align: center;
        padding: 0%;
        margin: 1px;
        z-index: 1;
    }

    .camera-container h4 {
        margin: 1px;
        background-color: rgb(187, 201, 211);
        border-radius: 5px;
    }

    .camera-view {
        width: 100%;
        max-width: 1280px;
        border-radius: 8px;
        margin: 0 auto;
        cursor: pointer;
    }

    .fullscreen-overlay {
        position: fixed;
        top: 0;
        left: 0;
        width: 100vw;
        height: 100vh;
        background: rgba(0, 0, 0, 0.8);
        display: flex;
        justify-content: center;
        align-items: center;
        z-index: 100;
    }

    .fullscreen-video {
        max-width: 90%;
        max-height: 90%;
        border-radius: 8px;
    }

    .close-btn {
        position: absolute;
        top: 20px;
        right: 20px;
        background: rgba(255, 255, 255, 0.8);
        border: none;
        padding: 10px 15px;
        border-radius: 50%;
        font-size: 18px;
        cursor: pointer;
        transition: all 0.3s;
    }

    .camera-selector {
        display: flex;
        justify-content: center;
        gap: 10px;
        margin-top: 10px;
    }

    .camera-button {
    padding: 10px 15px; 
    border: 2px solid #007bff; 
    background-color: #f8f9fa; 
    border-radius: 8px;
    cursor: pointer; 
    transition: all 0.3s ease; 
    font-size: 16px; 
    font-weight: 500; 
    color: #007bff; 
    box-shadow: 0 4px 6px rgba(0, 0, 0, 0.1); 
}

.camera-button:hover {
    background-color: #007bff; 
    color: #ffffff; 
    border-color: #0056b3; 
    box-shadow: 0 6px 8px rgba(0, 0, 0, 0.15); 
    transform: translateY(-2px); 
}

.camera-button:focus {
    outline: none; 
    box-shadow: 0 0 0 3px rgba(0, 123, 255, 0.5); 
}

.camera-button:active {
    background-color: #0056b3; 
    transform: translateY(1px); 
}


    .close-btn:hover {
        background: rgba(255, 255, 255, 1);
    }
</style>
