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

    const addCamera = () => {
        if (camera.ip && camera.port && camera.username && camera.password) {
            cameraList.update((cameras) => [...cameras, { ...camera }]);
            camera = { ip: "", port: "", username: "", password: "" };
        }
    };

    const sendCamerasToServer = async () => {
        const response = await fetch("http://localhost:8000/set-cameras", {
            method: "POST",
            headers: { "Content-Type": "application/json" },
            body: JSON.stringify($cameraList),
        });

        if (response.ok) {
            alert("Kamera bilgileri başarıyla gönderildi!");
        } else {
            alert("Hata oluştu!");
        }
    };
</script>

<div class="bg-gray-100 p-6 rounded-lg shadow-lg flex flex-col gap-2">
    <h2 class="text-lg font-bold">Kamera Ekle</h2>
    <input
        type="text"
        placeholder="IP Adresi"
        bind:value={camera.ip}
        class="p-2 border rounded"
    />
    <input
        type="text"
        placeholder="Port"
        bind:value={camera.port}
        class="p-2 border rounded"
    />
    <input
        type="text"
        placeholder="Kullanıcı Adı"
        bind:value={camera.username}
        class="p-2 border rounded"
    />
    <input
        type="password"
        placeholder="Şifre"
        bind:value={camera.password}
        class="p-2 border rounded"
    />
    <button on:click={addCamera} class="bg-blue-500 text-white p-2 rounded-lg shadow-md"
        >Ekle</button
    >
    <button
        on:click={sendCamerasToServer}
        class="bg-green-500 text-white p-2 rounded-lg shadow-md mt-2"
    >
        Kaydet ve Güncelle
    </button>
    <h3 class="text-md font-bold mt-4">Kayıtlı Kameralar</h3>
    <ul>
        {#each $cameraList as cam, index}
            <li class="border p-2 my-1 rounded bg-gray-100">
                {cam.ip}:{cam.port} - {cam.username}
            </li>
        {/each}
    </ul>
</div>
