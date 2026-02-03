<script>
  import { onMount, createEventDispatcher } from "svelte";
  import { writable, get } from "svelte/store";
  import { SERVER_IP } from "./store.js";
  import GlassCard from "./GlassCard.svelte";
  import toast, { Toaster } from "svelte-french-toast";

  export let onCameraAdded = null;

  const dispatch = createEventDispatcher();
  const cameraList = writable([]);
  let camera = { id: "", ip: "" };
  const showAdd = writable(true);

  // Kameraları getir
  const fetchCameras = async () => {
    try {
      const res = await fetch(SERVER_IP + ":8000/cameras/get-cameras");
      if (res.ok) cameraList.set(await res.json());
    } catch (e) {
      console.error(e);
    }
  };

  const addCamera = async () => {
    if (!camera.id || !camera.ip) {
      toast.dismiss();
      toast.error("Lütfen kamera ID ve IP adresini girin.", {
        duration: 3000,
        position: "top-right",
      });
      return;
    }

    try {
      const res = await fetch(SERVER_IP + ":8000/cameras/add", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify(camera),
      });

      if (res.ok) {
        const cameraId = camera.id;
        camera = { id: "", ip: "" };
        await fetchCameras();
        toast.dismiss();
        toast.success(`Kamera "${cameraId}" başarıyla eklendi!`, {
          duration: 3000,
          position: "top-right",
        });

        // Modal'ı kapat
        if (onCameraAdded) onCameraAdded();
        dispatch("close");
      } else {
        const error = await res.text();
        toast.dismiss();
        toast.error(`Kamera ekleme hatası: ${error}`, {
          duration: 3000,
          position: "top-right",
        });
      }
    } catch (e) {
      console.error("Kamera ekleme hatası:", e);
      toast.dismiss();
      toast.error("Kamera eklenirken bir hata oluştu.", {
        duration: 3000,
        position: "top-right",
      });
    }
  };

  const deleteCamera = async (id) => {
    const confirmation = confirm(
      "Bu kamerayı silmek istediğinizden emin misiniz?",
    );
    if (!confirmation) return;

    await fetch(SERVER_IP + `:8000/cameras/${id}`, {
      method: "DELETE",
    });
    fetchCameras();
  };

  onMount(fetchCameras);
</script>

<div class="w-full">
  <!-- Tab Butonları -->
  <div class="flex mb-6 bg-gray-100 rounded-lg p-1">
    <button
      on:click={() => showAdd.set(true)}
      class={`flex-1 py-2 px-4 rounded-md transition-all duration-200 flex items-center justify-center gap-2 ${
        $showAdd
          ? "bg-white shadow-sm text-blue-600 font-medium"
          : "text-gray-600 hover:text-gray-800"
      }`}
    >
      <svg
        xmlns="http://www.w3.org/2000/svg"
        class="w-5 h-5"
        fill="none"
        viewBox="0 0 24 24"
        stroke="currentColor"
      >
        <path
          stroke-linecap="round"
          stroke-linejoin="round"
          stroke-width="2"
          d="M12 4v16m8-8H4"
        />
      </svg>
      Kamera Ekle
    </button>

    <button
      on:click={() => showAdd.set(false)}
      class={`flex-1 py-2 px-4 rounded-md transition-all duration-200 flex items-center justify-center gap-2 ${
        !$showAdd
          ? "bg-white shadow-sm text-blue-600 font-medium"
          : "text-gray-600 hover:text-gray-800"
      }`}
    >
      <svg
        xmlns="http://www.w3.org/2000/svg"
        class="w-5 h-5"
        fill="none"
        viewBox="0 0 24 24"
        stroke="currentColor"
      >
        <path
          stroke-linecap="round"
          stroke-linejoin="round"
          stroke-width="2"
          d="M3 7h4l3-3h4l3 3h4v13H3V7z"
        />
        <circle cx="12" cy="13" r="3" />
      </svg>
      Kameraları Listele
    </button>
  </div>

  <!-- İçerik -->
  <div class="bg-gray-50 rounded-lg p-4 min-h-[300px]">
    {#if $showAdd}
      <!-- Kamera Ekle Formu -->
      <div class="space-y-4">
        <div>
          <label
            class="block text-sm font-medium text-gray-700 dark:text-slate-300 mb-2"
            >Kamera ID</label
          >
          <input
            type="text"
            placeholder="Örn: cam001"
            bind:value={camera.id}
            class="w-full p-3 border border-blue-400 dark:border-slate-600 bg-white dark:bg-slate-700 text-slate-700 dark:text-slate-200 rounded-lg focus:ring-2 focus:ring-blue-500 dark:focus:ring-slate-400 focus:border-blue-500 dark:focus:border-slate-400 transition-colors"
          />
        </div>

        <div>
          <label
            class="block text-sm font-medium text-gray-700 dark:text-slate-300 mb-2"
            >IP Adresi</label
          >
          <input
            type="text"
            placeholder="Örn: 192.168.1.100"
            bind:value={camera.ip}
            class="w-full p-3 border border-blue-400 dark:border-slate-600 bg-white dark:bg-slate-700 text-slate-700 dark:text-slate-200 rounded-lg focus:ring-2 focus:ring-blue-500 dark:focus:ring-slate-400 focus:border-blue-500 dark:focus:border-slate-400 transition-colors"
          />
        </div>

        <button
          on:click={addCamera}
          class="w-full py-3 bg-gradient-to-r from-blue-500 to-blue-600 text-white font-semibold rounded-lg hover:from-blue-600 hover:to-blue-700 transform hover:scale-[1.02] transition-all duration-200 shadow-md"
        >
          Kamerayı Kaydet
        </button>
      </div>
    {:else}
      <!-- Kayıtlı Kameralar Listesi -->
      <div>
        <h3 class="text-lg font-semibold text-gray-800 mb-4">
          Kayıtlı Kameralar ({$cameraList.length})
        </h3>
        {#if $cameraList.length === 0}
          <div class="text-center py-8 text-gray-500">
            <svg
              xmlns="http://www.w3.org/2000/svg"
              class="w-12 h-12 mx-auto mb-3 opacity-50"
              fill="none"
              viewBox="0 0 24 24"
              stroke="currentColor"
            >
              <path
                stroke-linecap="round"
                stroke-linejoin="round"
                stroke-width="2"
                d="M3 7h4l3-3h4l3 3h4v13H3V7z"
              />
              <circle cx="12" cy="13" r="3" />
            </svg>
            <p>Henüz kayıtlı kamera bulunmuyor.</p>
          </div>
        {:else}
          <div class="space-y-2 max-h-60 overflow-y-auto">
            {#each $cameraList as cam}
              <div
                class="flex justify-between items-center bg-white dark:bg-slate-700 p-3 rounded-lg border border-blue-200 dark:border-slate-600 hover:shadow-md transition-shadow"
              >
                <div class="flex items-center gap-3">
                  <div
                    class="w-10 h-10 bg-blue-100 rounded-full flex items-center justify-center"
                  >
                    <svg
                      xmlns="http://www.w3.org/2000/svg"
                      class="w-5 h-5 text-blue-600"
                      fill="none"
                      viewBox="0 0 24 24"
                      stroke="currentColor"
                    >
                      <path
                        stroke-linecap="round"
                        stroke-linejoin="round"
                        stroke-width="2"
                        d="M3 7h4l3-3h4l3 3h4v13H3V7z"
                      />
                      <circle cx="12" cy="13" r="3" />
                    </svg>
                  </div>
                  <div>
                    <div class="font-medium text-gray-800 dark:text-slate-200">
                      {cam.id}
                    </div>
                    <div class="text-sm text-gray-500 dark:text-slate-400">
                      {cam.ip}
                    </div>
                  </div>
                </div>
                <button
                  on:click={() => deleteCamera(cam.id)}
                  class="p-2 text-red-500 hover:text-red-700 hover:bg-red-50 rounded-lg transition-colors"
                  title="Kamerayı sil"
                >
                  <svg
                    xmlns="http://www.w3.org/2000/svg"
                    class="w-5 h-5"
                    fill="none"
                    viewBox="0 0 24 24"
                    stroke="currentColor"
                  >
                    <path
                      stroke-linecap="round"
                      stroke-linejoin="round"
                      stroke-width="2"
                      d="M19 7l-.867 12.142A2 2 0 0116.138 21H7.862a2 2 0 01-1.995-1.858L5 7m5 4v6m4-6v6m1-10V4a1 1 0 00-1-1h-4a1 1 0 00-1 1v3M4 7h16"
                    />
                  </svg>
                </button>
              </div>
            {/each}
          </div>
        {/if}
      </div>
    {/if}
  </div>
</div>
