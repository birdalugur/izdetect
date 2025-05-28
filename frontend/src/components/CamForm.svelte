<script>
    import { writable, get } from "svelte/store";

    export const cameraList = writable([]);
    let camera = { ip: "", port: "", username: "", password: "" };
    let showAddCamera = writable(true);

    const fetchCameras = async () => {
        try {
            const response = await fetch("http://localhost:8000/cameras/get-cameras");
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

            const response = await fetch("http://localhost:8000/cameras/set-cameras", {
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

            const response = await fetch("http://localhost:8000/cameras/set-cameras", {
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
