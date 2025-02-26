Aşağıdaki svelte kodlarını gözden geçirmeniz ve belirtilen talimatlara göre düzenlemeniz gerekmektedir.

### Mevcut Kodlar:
    
#### CamForm.svelte:
```
<script>
    import { writable, get } from "svelte/store";

    export const cameraList = writable([]);
    let camera = { ip: "", port: "", username: "", password: "" };
    let showAddCamera = writable(true);

    const fetchCameras = async () => {
        try {
            const response = await fetch("http://localhost:8000/get-cameras");
            if (response.ok) {
                const cameras = await response.json();
                cameraList.set(
                    cameras.map((cam) => ({
                        id: cam.id,
                        ip: cam.ip,
                    })),
                );
            }
        } catch (error) {
            console.error("Kameralar alinirken hata oluştu:", error);
        }
    };

    const addCamera = async () => {
        if (camera.ip && camera.id) {
            cameraList.update((cameras) => [...cameras, { ...camera }]);

            const response = await fetch("http://localhost:8000/set-cameras", {
                method: "POST",
                headers: { "Content-Type": "application/json" },
                body: JSON.stringify(get(cameraList)),
            });

            if (response.ok) {
                alert("Kamera bilgileri başarıyla eklendi ve kaydedildi!");
                fetchCameras();
            } else {
                alert("Hata oluştu!");
            }

            camera = { id: "", ip: "" };
        }
    };

    const deleteCamera = async (index) => {
        const confirmation = confirm(
            "Bu kamerayı silmek istediğinizden emin misiniz?",
        );
        if (confirmation) {
            cameraList.update((cameras) => {
                cameras.splice(index, 1);
                return cameras;
            });

            const response = await fetch("http://localhost:8000/set-cameras", {
                method: "POST",
                headers: { "Content-Type": "application/json" },
                body: JSON.stringify(get(cameraList)),
            });

            if (response.ok) {
                fetchCameras();
            } else {
                alert("Silme işlemi sırasında hata oluştu!");
            }
        }
    };

    fetchCameras();
</script>

<div class="bg-gray-100 p-6 rounded-lg shadow-lg flex flex-col gap-4">
    <h2 class="text-lg font-bold text-center">Kamera Yönetimi</h2>

    <!-- Switch Bileşeni -->
    <div class="flex items-center justify-center gap-4">
        <span class="text-gray-700 font-medium">Listele</span>
        <label class="relative inline-flex items-center cursor-pointer">
            <input
                type="checkbox"
                bind:checked={$showAddCamera}
                class="sr-only peer"
            />
            <div
                class="w-14 h-7 bg-gray-300 peer-focus:ring-4 peer-focus:ring-blue-300 rounded-full peer-checked:bg-blue-600 after:content-[''] after:absolute after:top-1 after:left-1 after:bg-white after:border after:rounded-full after:h-5 after:w-5 after:transition-all peer-checked:after:translate-x-7"
            ></div>
        </label>
        <span class="text-gray-700 font-medium">Ekle</span>
    </div>

    {#if $showAddCamera}
        <div>
            <h3 class="text-sm font-semibold">Kamera Ekle</h3>
            <input
                type="text"
                placeholder="ID"
                bind:value={camera.id}
                class="p-1 border rounded w-full mt-2 text-sm"
            />
            <input
                type="text"
                placeholder="IP Adresi"
                bind:value={camera.ip}
                class="p-1 border rounded w-full mt-2 text-sm"
            />

            <button
                on:click={addCamera}
                class="bg-blue-500 text-white p-2 rounded-lg shadow-md w-full mt-3 text-sm"
                >Ekle ve Kaydet</button
            >
        </div>
    {:else}
        <div>
            <h3 class="text-md font-bold">Kayıtlı Kameralar</h3>
            <ul>
                {#each $cameraList as cam, index}
                    <li
                        class="border p-2 my-2 rounded bg-white flex justify-between items-center"
                    >
                        <div>
                            <span class="font-semibold">{cam.ip.slice(5,20)}</span>
                            - {cam.id}
                        </div>
                        <button
                            on:click={() => deleteCamera(index)}
                            class="text-red-500 hover:text-red-700 p-1 rounded"
                        >
                            Sil
                        </button>
                    </li>
                {/each}
            </ul>
        </div>
    {/if}
</div>

```
#### LiveCamera.svelte:
```
<script>
    import { onMount } from "svelte";
    import { writable } from "svelte/store";

    let cameraList = writable([]);
    let selectedCamera = writable(null);
    const defaultStreamUrl = "http://localhost:8000/video";

    let isFullscreen = false;

    const toggleFullscreen = () => {
        isFullscreen = !isFullscreen;
    };

    const fetchCameras = async () => {
        try {
            const response = await fetch("http://localhost:8000/get-cameras");
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

    onMount(fetchCameras);
</script>

<div class="bg-gray-100 p-2 rounded-lg shadow-lg mx-auto mt-2">
    <!-- svelte-ignore a11y-click-events-have-key-events -->
    <div class="camera-container" class:isFullscreen>
        <h4>Cam - 2</h4>
        <img
            class="camera-view"
            src={$selectedCamera
                ? `http://localhost:8000/video/${$selectedCamera.id}`
                : defaultStreamUrl}
            alt="IP Kamera Canli Yayini"
            on:click={toggleFullscreen}
        />
        {#if isFullscreen}
            <div class="fullscreen-overlay" on:click={toggleFullscreen}>
                <img
                    class="fullscreen-video"
                    src={`http://localhost:8000/video/${$selectedCamera.id}`}
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
        transition: all 0.3s;
    }

    .camera-selector {
        display: flex;
        justify-content: center;
        gap: 10px;
        margin-top: 10px;
    }

    .camera-button {
        padding: 8px 12px;
        border: 2px solid #007bff;
        background-color: #f8f9fa;
        border-radius: 5px;
        cursor: pointer;
        transition: all 0.3s;
    }

    .camera-button.active,
    .camera-button:hover {
        background-color: #007bff;
        color: white;
    }

    .close-btn:hover {
        background: rgba(255, 255, 255, 1);
    }
</style>

```
#### App.svelte:
```
<script>
    import Control from "./components/Control.svelte";
    import Notifications from "./components/Notifications.svelte";
    import CamForm from "./components/CamForm.svelte";
    import LiveCamera from "./components/LiveCamera.svelte";
    import Ram from "./components/Ram.svelte";
    // import Calender from "./components/Calender.svelte";

    let messages = [];

    const addMessage = (message) => {
        messages = [message, ...messages].slice(0, 5); // Prepend new message and keep only the last 5
    };
</script>

<main class="flex h-[99vh] bg-gray-100">
    <div class="w-1/5 bg-white p-5 flex flex-col gap-5 overflow-y-auto">
        <Control {addMessage} />
        <Ram />
        <CamForm />        
        <!-- <Messages {messages} /> -->
        <!-- <Timeline /> -->
    </div>
    <div class="w-2/5 p-2 bg-white">
        <LiveCamera />
        <!-- <Calender /> -->
    </div>
    <div class="w-2/5 p-5 bg-gray-50 overflow-y-auto flex flex-col gap-2.5">
        <Notifications />
    </div>
</main>

```
### Talimatlar:
- LiveCamera.svelte'de bulunan camera-selector kısmında kamera yönetim butonu ekle.
- kamera yönetim butonuna tıklanıldığında CamForm.svelte küçük bir pencerede açılsın.
- CamForm.svelte dışında bir yere tıklanıldığında CamForm.svelte penceresi kapansın.

Lütfen gerekli değişiklikleri yaparak düzenlenmiş veya yeni eklenmiş kodu döndürün.