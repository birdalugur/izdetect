<script>
    import { cameraUrls, clearCameraUrls } from "./store";

    export let addMessage;

    let isStarting = false;
    let startMessage = "";
    let isStopping = false;
    let stopMessage = "";

    let memoryValue = 5;
    let sensitivityValue = 0.2;

    const startRealTimeDetection = async () => {
        await updateSettings();
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

    const stopRealTimeDetection = async () => {
        isStopping = true;
        stopMessage = "Stopping frame producer...";
        addMessage(stopMessage);

        try {
            const response = await fetch(
                "http://localhost:8000/stop-detection",
                {
                    method: "POST",
                },
            );
            const data = await response.json();
            if (response.ok) {
                stopMessage = data.message;
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

    const updateSettings = async () => {
        try {
            const response = await fetch(
                "http://localhost:8000/update-settings",
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

            if (!response.ok) {
                throw new Error(
                    `Failed to update settings: ${response.statusText}`,
                );
            }

            const data = await response.json();
            console.log(data.message);
        } catch (error) {
            console.error("Error updating settings:", error);
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
        class="button stop-frame-producer"
        on:click={stopRealTimeDetection}
        disabled={isStopping}
    >
        {isStopping ? "Stopping..." : "Stop Detection"}
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

    .stop-frame-producer {
        background-color: #d9534f;
        color: white;
    }
    .stop-frame-producer:disabled {
        background-color: #6c757d;
        cursor: not-allowed;
    }
</style>
