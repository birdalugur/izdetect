<script>
    import { cameraUrls, clearCameraUrls } from "./store";

    export let addMessage;

    let videoFile = null;
    let isUploading = false;
    let uploadMessage = "";
    let isStarting = false;
    let startMessage = "";
    let isStopping = false;
    let stopMessage = "";

    let memoryValue = 5;
    let sensitivityValue = 0.2;

    const handleFileChange = (event) => {
        videoFile = event.target.files[0];
        uploadMessage = "";
    };

    const startRealTimeDetection = async () => {
        isStarting = true;
        startMessage = "Starting real-time video processing...";
        addMessage(startMessage);

        try {
            const response = await fetch(
                "http://localhost:8000/start-detection",
                {
                    method: "POST",
                    headers: {
                        "Content-Type": "application/json",
                    },
                    body: JSON.stringify({
                        memory: memoryValue,
                        sensitivity: sensitivityValue,
                    }),
                },
            );
            const data = await response.json();
            if (response.ok) {
                startMessage = data.message;
                cameraUrls.set({
                    cameraUrl2: data.default_camera_url,
                });
            } else {
                startMessage = `Could not start: ${data.error || response.statusText}`;
            }
        } catch (error) {
            startMessage = `Error: ${error.message}`;
        } finally {
            isStarting = false;
            addMessage(startMessage);
        }
    };

    const showCamera = async () => {
        startMessage = "";
        try {
            const response = await fetch("http://localhost:8000/camurl", {
                method: "GET",
                headers: {
                    "Content-Type": "application/json",
                },
            });
            const data = await response.json();
            if (response.ok) {
                cameraUrls.set({
                    cameraUrl2: data.url,
                });
                startMessage = "Camera URL retrieved successfully.";
            } else {
                startMessage = `Could not retrieve camera URL: ${data.error || response.statusText}`;
            }
        } catch (error) {
            startMessage = `Error: ${error.message}`;
        } finally {
            isStarting = false;
            addMessage(startMessage);
        }
    };

    const stopRealTimeVideo = async () => {
        isStopping = true;
        stopMessage = "Stopping real-time video processing...";
        addMessage(stopMessage);

        try {
            const response = await fetch("http://localhost:8000/stop-video", {
                method: "POST",
            });
            const data = await response.json();
            if (response.ok) {
                stopMessage = data.message;
                clearCameraUrls();
            } else {
                stopMessage = `Could not stop: ${data.error || response.statusText}`;
            }
        } catch (error) {
            stopMessage = `Error: ${error.message}`;
        } finally {
            isStopping = false;
            addMessage(stopMessage);
        }
    };
</script>

<div class="upload-container">
    <div class="config-inputs">
        <label for="memory">Memory Value: {memoryValue}</label>
        <input type="range" bind:value={memoryValue} min="1" max="100" />

        <label for="sensitivityValue">Sensitivity: {sensitivityValue}</label>
        <input
            type="range"
            bind:value={sensitivityValue}
            step="0.1"
            min="0.1"
            max="0.9"
        />
    </div>

    <button
        class="button start-button"
        on:click={startRealTimeDetection}
        disabled={isStarting}
    >
        {isStarting ? "Starting..." : "Start Detection"}
    </button>

    <button
        class="button stop-button"
        on:click={stopRealTimeVideo}
        disabled={isStopping}
    >
        {isStopping ? "Stopping..." : "Stop Camera"}
    </button>
    <button
        class="button show-button"
        on:click={showCamera}
        disabled={isStopping}
    >
        {isStopping ? "Stopping..." : "Show Camera"}
    </button>
</div>

<style>
    .config-inputs {
        margin-top: 20px;
        text-align: left;
    }

    label {
        display: block;
        margin-bottom: 10px;
    }

    input[type="range"] {
        width: 100%;
        margin-bottom: 20px;
    }

    .upload-container {
        text-align: left;
        margin-top: 5px;
    }

    .button {
        display: block;
        width: 100%;
        margin-top: 10px;
        padding: 10px 20px;
        font-size: 16px;
        text-align: center;
        border: none;
        border-radius: 5px;
        cursor: pointer;
    }

    .start-button {
        background-color: #7898dd;
        color: white;
    }

    .start-button:disabled {
        background-color: #6c757d;
        cursor: not-allowed;
    }

    .stop-button {
        background-color: #af3945;
        color: white;
    }

    .show-button {
        background-color: powderblue;
    }

    .stop-button:disabled {
        background-color: #6c757d;
        cursor: not-allowed;
    }
</style>
