<script>
    import { writable } from "svelte/store";

    // Kamera bilgilerini saklamak için store
    export const cameraList = writable([]);

    let camera = {
        ip: "",
        port: "",
        username: "",
        password: "",
    };

    let showAddCamera = writable(true);

    const addCamera = async () => {
        if (camera.ip && camera.port && camera.username && camera.password) {
            cameraList.update((cameras) => [...cameras, { ...camera }]);
            camera = { ip: "", port: "", username: "", password: "" };

            const response = await fetch("http://localhost:8000/set-cameras", {
                method: "POST",
                headers: { "Content-Type": "application/json" },
                body: JSON.stringify($cameraList),
            });

            if (response.ok) {
                alert("Kamera bilgileri başarıyla eklendi ve kaydedildi!");
            } else {
                alert("Hata oluştu!");
            }
        }
    };
</script>

<div class="bg-gray-100 p-6 rounded-lg shadow-lg flex flex-col gap-2">
    <div class="flex items-center justify-between">
        <h2 class="text-lg font-bold">Kamera Yönetimi</h2>
        <label class="relative inline-flex items-center cursor-pointer">
            <input
                type="checkbox"
                bind:checked={$showAddCamera}
                class="sr-only peer"
            />
            <div
                class="w-11 h-6 bg-gray-300 peer-focus:ring-4 peer-focus:ring-blue-300 rounded-full peer-checked:bg-blue-600 after:content-[''] after:absolute after:top-0.5 after:left-1 after:bg-white after:border after:rounded-full after:h-5 after:w-5 after:transition-all peer-checked:translate-x-5"
            ></div>
        </label>
    </div>

    {#if $showAddCamera}
        <div>
            <h3 class="text-md font-bold">Kamera Ekle</h3>
            <input
                type="text"
                placeholder="IP Adresi"
                bind:value={camera.ip}
                class="p-2 border rounded w-full"
            />
            <input
                type="text"
                placeholder="Port"
                bind:value={camera.port}
                class="p-2 border rounded w-full"
            />
            <input
                type="text"
                placeholder="Kullanıcı Adı"
                bind:value={camera.username}
                class="p-2 border rounded w-full"
            />
            <input
                type="password"
                placeholder="Şifre"
                bind:value={camera.password}
                class="p-2 border rounded w-full"
            />
            <button
                on:click={addCamera}
                class="bg-blue-500 text-white p-2 rounded-lg shadow-md w-full mt-2"
                >Ekle ve Kaydet</button
            >
        </div>
    {:else}
        <div>
            <h3 class="text-md font-bold">Kayıtlı Kameralar</h3>
            <ul>
                {#each $cameraList as cam, index}
                    <li class="border p-2 my-1 rounded bg-gray-100">
                        {cam.ip}:{cam.port} - {cam.username}
                    </li>
                {/each}
            </ul>
        </div>
    {/if}
</div>
