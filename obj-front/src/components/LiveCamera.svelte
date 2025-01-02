<script>
    import { cameraUrls } from "./store";
    let urls;
    cameraUrls.subscribe((value) => {
        urls = value;
    });
    
</script>

<!-- <div class="camera-container">
    <h4>Cam - 1</h4>
    <iframe
        src={cameraUrl}
        frameborder="0"
        allow="autoplay; encrypted-media"
        allowfullscreen
        title="cam1"
    ></iframe>
</div> -->

<div class="camera-container">
    <h4>Cam - 1</h4>
    <!-- <img class="camera-view" src={urls.cameraUrl1} alt="IP Kamera Canlı Yayını" /> -->

    <video src={urls.cameraUrl1} autoplay controls>
        <track kind="captions" />
    </video>
</div>

<div class="camera-container">
    <h4>Cam - 2</h4>
    <img
        class="camera-view"
        src={urls.cameraUrl2}
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

    .camera-container video {
        width: 100%;
    }

    .camera-container h4 {
        margin: 1px;
        background-color: rgb(187, 201, 211);
        border-radius: 5px;
    }

    /* iframe {
        width: 100%;
        height: 400px;
    } */

    .camera-view {
        width: 100%;
        max-width: 1280px;
        border-radius: 8px;
        margin: 0 auto;
    }
</style>
