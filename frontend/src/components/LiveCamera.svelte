<script>
    import { cameraUrls } from "./store";

    let urls;
    cameraUrls.subscribe((value) => {
        urls = value;
    });

    const videoStreamUrl = "http://localhost:8000/video";

    let isFullscreen = false;

    const toggleFullscreen = () => {
        isFullscreen = !isFullscreen;
    };
</script>

<div class="bg-gray-100 p-2 rounded-lg shadow-lg  mx-auto mt-2">
    <!-- svelte-ignore a11y-click-events-have-key-events -->
    <div class="camera-container" class:isFullscreen>
        <h4>Cam - 2</h4>
        <img
            class="camera-view"
            src={`${videoStreamUrl}`}
            alt="IP Kamera Canlı Yayını"
            on:click={toggleFullscreen}
        />
        {#if isFullscreen}
            <div class="fullscreen-overlay" on:click={toggleFullscreen}>
                <img
                    class="fullscreen-video"
                    src={`${videoStreamUrl}`}
                    alt="IP Kamera Tam Ekran"
                />
                <button class="close-btn" on:click={toggleFullscreen}>✕</button>
            </div>
        {/if}
    </div>
</div>

<style>
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
    }

    .close-btn:hover {
        background: rgba(255, 255, 255, 1);
    }
</style>
