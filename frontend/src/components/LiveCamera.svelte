<script>
    import { cameraUrls } from "./store";
    let urls;
    cameraUrls.subscribe((value) => {
        urls = value;
    });

    const videoStreamUrl = "http://localhost:8000/video";
</script>

<div class="camera-container">
    <h4>Cam - 2</h4>
    <img
        class="camera-view"
        src={`${videoStreamUrl}`}
        alt="IP Kamera Canlı Yayını"
    />
</div>

<style>
    .camera-container {
        width: 100%;
        height: 50%;
        max-width: 800px;
        border: 2px solid #ddd;
        border-radius: 8px;
        overflow: hidden;
        text-align: center;
        padding: 0%;
        margin: 1px;
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
    }
</style>
