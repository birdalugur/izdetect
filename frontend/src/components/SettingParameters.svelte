<script>
  import { onMount } from "svelte";
  import GlassCard from "./GlassCard.svelte";
  import { SERVER_IP } from "./store";
  import { darkMode } from "./store.js";

  export let addMessage;
  export let open = true;

  let memoryValue = 5;
  let sensitivityValue = 0.2;
  let retentionValue = 3;

  // Reactive values for display
  $: memoryPercentage = (memoryValue / 100) * 100;
  $: sensitivityPercentage = (sensitivityValue / 0.9) * 100;
  $: retentionPercentage = (retentionValue / 30) * 100;

  $: getMemoryColor = (val) => {
    if (val < 30) return "from-emerald-400 to-green-500";
    if (val < 70) return "from-yellow-400 to-orange-500";
    return "from-orange-500 to-red-500";
  };
  $: getSensitivityColor = (val) => {
    if (val < 40) return "from-blue-400 to-blue-500";
    if (val < 70) return "from-purple-400 to-purple-500";
    return "from-pink-400 to-pink-500";
  };
  $: getRetentionColor = (val) => {
    return "from-cyan-400 to-blue-500";
  };

  // Fetch settings from backend on mount
  onMount(async () => {
    try {
      const res = await fetch(SERVER_IP + ":8000/system/get-settings");
      const data = await res.json();
      if (res.ok) {
        memoryValue = data.memory ?? memoryValue;
        sensitivityValue = data.sensitivity ?? sensitivityValue;
        retentionValue = data.retention_days ?? retentionValue;
      } else {
        console.error("Failed to fetch settings:", data.detail);
      }
    } catch (err) {
      console.error("Fetch error:", err);
    }
  });

  const updateSettings = async () => {
    try {
      const response = await fetch(SERVER_IP + ":8000/system/update-settings", {
        method: "POST",
        headers: {
          "Content-Type": "application/json",
        },
        body: JSON.stringify({
          memory: memoryValue,
          sensitivity: sensitivityValue,
          retention_days: retentionValue,
        }),
      });
      if (!response.ok) {
        throw new Error(`Failed to update settings: ${response.statusText}`);
      }
      const data = await response.json();
      console.log(data.message);
    } catch (error) {
      console.error("Error updating settings:", error);
    }
  };
</script>

<div class="relative flex flex-col flex-1 min-h-0">
  <!-- Panel Content -->
  {#if open}
    <div class="flex flex-col gap-2 overflow-y-auto flex-1 min-h-0">
      <div class="mb-1">
        <GlassCard className="p-3 border-gray-200/40 !bg-gray-100/60 dark:!bg-slate-300/60">
           <div class="flex items-center justify-between">
              <h2 class="text-base font-bold leading-tight transition-colors duration-300" class:text-slate-800={!$darkMode} class:text-slate-100={$darkMode}>
                 Parametreler
              </h2>
           </div>
        </GlassCard>
      </div>

      <!-- Settings Controls -->
      <GlassCard className="p-4 space-y-3 w-full max-w-sm mx-auto">
        <!-- Bellek Değeri Progress Bar -->
        <div class="space-y-3">
          <div class="flex items-center justify-between">
            <span
              class="text-sm font-medium transition-colors duration-300"
              class:text-slate-700={!$darkMode}
              class:text-slate-200={$darkMode}>Bellek Değeri</span
            >
            <span
              class="text-xs transition-colors duration-300"
              class:text-slate-500={!$darkMode}
              class:text-slate-400={$darkMode}>{memoryValue}/100</span
            >
          </div>

          <div class="relative">
            <!-- Arka plan bar -->
            <div
              class="w-full h-6 bg-white/40 backdrop-blur-sm rounded-xl border border-white/30 shadow-inner overflow-hidden"
            >
              <!-- Progress bar -->
              <div
                class="h-full bg-gradient-to-r {getMemoryColor(
                  memoryPercentage,
                )} transition-all duration-500 ease-out relative rounded-xl"
                style="width: {memoryPercentage}%"
              >
                <!-- Parlama efekti -->
                <div
                  class="absolute inset-0 bg-gradient-to-r from-transparent via-white/20 to-transparent animate-pulse"
                ></div>
              </div>

              <!-- Değer barın içinde -->
              <div class="absolute inset-0 flex items-center justify-center">
                <span
                  class="text-xs font-bold drop-shadow-sm transition-colors duration-300"
                  class:text-slate-800={!$darkMode}
                  class:text-white={$darkMode}>{memoryValue}</span
                >
              </div>
            </div>

            <!-- Slider (invisible) -->
            <input
              id="memoryRange"
              type="range"
              bind:value={memoryValue}
              on:input={updateSettings}
              min="1"
              max="100"
              class="absolute inset-0 w-full h-full opacity-0 cursor-pointer"
            />
          </div>
        </div>

        <!-- Saklama Süresi Progress Bar -->
        <div class="space-y-3">
          <div class="flex items-center justify-between">
            <span
              class="text-sm font-medium transition-colors duration-300"
              class:text-slate-700={!$darkMode}
              class:text-slate-200={$darkMode}>Saklama Süresi (Gün)</span
            >
            <span
              class="text-xs transition-colors duration-300"
              class:text-slate-500={!$darkMode}
              class:text-slate-400={$darkMode}>{retentionValue} Gün</span
            >
          </div>

          <div class="relative">
            <!-- Arka plan bar -->
            <div
              class="w-full h-6 bg-white/40 backdrop-blur-sm rounded-xl border border-white/30 shadow-inner overflow-hidden"
            >
              <!-- Progress bar -->
              <div
                class="h-full bg-gradient-to-r {getRetentionColor(
                  retentionPercentage,
                )} transition-all duration-500 ease-out relative rounded-xl"
                style="width: {retentionPercentage}%"
              >
                <!-- Parlama efekti -->
                <div
                  class="absolute inset-0 bg-gradient-to-r from-transparent via-white/20 to-transparent animate-pulse"
                ></div>
              </div>

              <!-- Değer barın içinde -->
              <div class="absolute inset-0 flex items-center justify-center">
                <span
                  class="text-xs font-bold drop-shadow-sm transition-colors duration-300"
                  class:text-slate-800={!$darkMode}
                  class:text-white={$darkMode}>{retentionValue}</span
                >
              </div>
            </div>

            <!-- Slider (invisible) -->
            <input
              id="retentionRange"
              type="range"
              bind:value={retentionValue}
              on:input={updateSettings}
              min="1"
              max="30"
              class="absolute inset-0 w-full h-full opacity-0 cursor-pointer"
            />
          </div>
        </div>

        <!-- Hassasiyet Progress Bar -->
        <div class="space-y-3">
          <div class="flex items-center justify-between">
            <span
              class="text-sm font-medium transition-colors duration-300"
              class:text-slate-700={!$darkMode}
              class:text-slate-200={$darkMode}>Hassasiyet</span
            >
            <span
              class="text-xs transition-colors duration-300"
              class:text-slate-500={!$darkMode}
              class:text-slate-400={$darkMode}>{sensitivityValue}/0.9</span
            >
          </div>

          <div class="relative">
            <!-- Arka plan bar -->
            <div
              class="w-full h-6 bg-white/40 backdrop-blur-sm rounded-xl border border-white/30 shadow-inner overflow-hidden"
            >
              <!-- Progress bar -->
              <div
                class="h-full bg-gradient-to-r {getSensitivityColor(
                  sensitivityPercentage,
                )} transition-all duration-500 ease-out relative rounded-xl"
                style="width: {sensitivityPercentage}%"
              >
                <!-- Parlama efekti -->
                <div
                  class="absolute inset-0 bg-gradient-to-r from-transparent via-white/20 to-transparent animate-pulse"
                ></div>
              </div>

              <!-- Değer barın içinde -->
              <div class="absolute inset-0 flex items-center justify-center">
                <span
                  class="text-xs font-bold drop-shadow-sm transition-colors duration-300"
                  class:text-slate-800={!$darkMode}
                  class:text-white={$darkMode}>{sensitivityValue}</span
                >
              </div>
            </div>

            <!-- Slider (invisible) -->
            <input
              id="sensitivityRange"
              type="range"
              bind:value={sensitivityValue}
              on:input={updateSettings}
              step="0.1"
              min="0.1"
              max="0.9"
              class="absolute inset-0 w-full h-full opacity-0 cursor-pointer"
            />
          </div>
        </div>
      </GlassCard>
    </div>
  {/if}
</div>

<style>
</style>
