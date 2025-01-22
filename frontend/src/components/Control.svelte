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

<div class="bg-gray-100 p-6 rounded-lg shadow-lg max-w-md mx-auto mt-10">
    <h2 class="text-2xl font-bold text-gray-800 mb-4">Real-Time Detection</h2>
    <div class="space-y-4">
        <div>
            <label for="memory" class="block text-gray-600 font-medium mb-1"
                >Memory Value: {memoryValue}</label
            >
            <input
                type="range"
                bind:value={memoryValue}
                min="1"
                max="100"
                class="w-full h-2 bg-gray-200 rounded-lg appearance-none cursor-pointer"
            />
        </div>

        <div>
            <label
                for="sensitivityValue"
                class="block text-gray-600 font-medium mb-1"
                >Sensitivity: {sensitivityValue}</label
            >
            <input
                type="range"
                bind:value={sensitivityValue}
                step="0.1"
                min="0.1"
                max="0.9"
                class="w-full h-2 bg-gray-200 rounded-lg appearance-none cursor-pointer"
            />
        </div>

        <button
            on:click={startRealTimeDetection}
            disabled={isStarting}
            class={`w-full py-2 px-4 text-white font-semibold rounded-lg shadow-md transition 
            ${isStarting ? "bg-gray-400 cursor-not-allowed" : "bg-blue-500 hover:bg-blue-600"}`}
        >
            {isStarting ? "Starting..." : "Start Detection"}
        </button>

        <button
            on:click={stopRealTimeDetection}
            disabled={isStopping}
            class={`w-full py-2 px-4 text-white font-semibold rounded-lg shadow-md transition 
            ${isStopping ? "bg-gray-400 cursor-not-allowed" : "bg-red-500 hover:bg-red-600"}`}
        >
            {isStopping ? "Stopping..." : "Stop Detection"}
        </button>
    </div>
</div>
