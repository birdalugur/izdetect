<!-- src/components/Control.svelte -->
<script>
  import GlassCard from './GlassCard.svelte';
  import { cameraUrls, clearCameraUrls, darkMode } from './store.js';
  export let addMessage;

  let memoryValue = 5;
  let sensitivityValue = 0.2;
  let isActive = false;
  let isLoading = false;

  // Reactive values for display
  $: memoryPercentage = (memoryValue / 100) * 100;
  $: sensitivityPercentage = (sensitivityValue / 0.9) * 100;
  $: getMemoryColor = (val) => {
    if (val < 30) return 'from-emerald-400 to-green-500';
    if (val < 70) return 'from-yellow-400 to-orange-500';
    return 'from-orange-500 to-red-500';
  };
  $: getSensitivityColor = (val) => {
    if (val < 40) return 'from-blue-400 to-blue-500';
    if (val < 70) return 'from-purple-400 to-purple-500';
    return 'from-pink-400 to-pink-500';
  };

  const updateSettings = async () => {
    try {
      await fetch('http://localhost:8000/system/update-settings', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ memory: memoryValue, sensitivity: sensitivityValue }),
      });
    } catch (err) {
      console.error('Settings update error:', err);
    }
  };

  const toggleDetection = async () => {
    isLoading = true;
    if (!isActive) {
      addMessage('Gerçek zamanlı işleme başlatılıyor…');
      await updateSettings();
      try {
        const res = await fetch(
          'http://localhost:8000/cameras/start-detection',
          {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ memory: memoryValue, sensitivity: sensitivityValue })
          }
        );
        const data = await res.json();
        if (res.ok) {
          cameraUrls.set({ cameraUrl2: data.default_camera_url });
          isActive = true;
          addMessage(data.message);
        } else {
          addMessage(`Başlatılamadı: ${data.error || res.statusText}`);
        }
      } catch (err) {
        addMessage(`Hata: ${err.message}`);
      }
    } else {
      addMessage('İşleme durduruluyor…');
      try {
        const res = await fetch(
          'http://localhost:8000/cameras/stop-detection',
          { method: 'POST' }
        );
        const data = await res.json();
        if (res.ok) {
          clearCameraUrls();
          isActive = false;
          addMessage(data.message);
        } else {
          addMessage(`Durdurulamadı: ${data.error || res.statusText}`);
        }
      } catch (err) {
        addMessage(`Hata: ${err.message}`);
      }
    }
    isLoading = false;
  };
</script>

<GlassCard className="p-4 space-y-3 w-full max-w-sm mx-auto">
  <!-- Bellek Değeri Progress Bar -->
  <div class="space-y-3">
    <div class="flex items-center justify-between">
      <span class="text-sm font-medium transition-colors duration-300" class:text-slate-700={!$darkMode} class:text-slate-200={$darkMode}>Bellek Değeri</span>
      <span class="text-xs transition-colors duration-300" class:text-slate-500={!$darkMode} class:text-slate-400={$darkMode}>{memoryValue}/100</span>
    </div>
    
    <div class="relative">
      <!-- Arka plan bar -->
      <div class="w-full h-6 bg-white/40 backdrop-blur-sm rounded-xl border border-white/30 shadow-inner overflow-hidden">
        <!-- Progress bar -->
        <div
          class="h-full bg-gradient-to-r {getMemoryColor(memoryPercentage)} transition-all duration-500 ease-out relative rounded-xl"
          style="width: {memoryPercentage}%"
        >
          <!-- Parlama efekti -->
          <div class="absolute inset-0 bg-gradient-to-r from-transparent via-white/20 to-transparent animate-pulse"></div>
        </div>
        
        <!-- Değer barın içinde -->
        <div class="absolute inset-0 flex items-center justify-center">
          <span class="text-xs font-bold drop-shadow-sm transition-colors duration-300" class:text-slate-800={!$darkMode} class:text-white={$darkMode}>{memoryValue}</span>
        </div>
      </div>
      
      <!-- Slider (invisible) -->
      <input
        id="memoryRange"
        type="range"
        bind:value={memoryValue}
        on:input={updateSettings}
        min="1" max="100"
        class="absolute inset-0 w-full h-full opacity-0 cursor-pointer"
      />
    </div>
  </div>

  <!-- Hassasiyet Progress Bar -->
  <div class="space-y-3">
    <div class="flex items-center justify-between">
      <span class="text-sm font-medium transition-colors duration-300" class:text-slate-700={!$darkMode} class:text-slate-200={$darkMode}>Hassasiyet</span>
      <span class="text-xs transition-colors duration-300" class:text-slate-500={!$darkMode} class:text-slate-400={$darkMode}>{sensitivityValue}/0.9</span>
    </div>
    
    <div class="relative">
      <!-- Arka plan bar -->
      <div class="w-full h-6 bg-white/40 backdrop-blur-sm rounded-xl border border-white/30 shadow-inner overflow-hidden">
        <!-- Progress bar -->
        <div
          class="h-full bg-gradient-to-r {getSensitivityColor(sensitivityPercentage)} transition-all duration-500 ease-out relative rounded-xl"
          style="width: {sensitivityPercentage}%"
        >
          <!-- Parlama efekti -->
          <div class="absolute inset-0 bg-gradient-to-r from-transparent via-white/20 to-transparent animate-pulse"></div>
        </div>
        
        <!-- Değer barın içinde -->
        <div class="absolute inset-0 flex items-center justify-center">
          <span class="text-xs font-bold drop-shadow-sm transition-colors duration-300" class:text-slate-800={!$darkMode} class:text-white={$darkMode}>{sensitivityValue}</span>
        </div>
      </div>
      
      <!-- Slider (invisible) -->
      <input
        id="sensitivityRange"
        type="range"
        bind:value={sensitivityValue}
        on:input={updateSettings}
        step="0.1" min="0.1" max="0.9"
        class="absolute inset-0 w-full h-full opacity-0 cursor-pointer"
      />
    </div>
  </div>

  <!-- Başlat/Durdur Butonu -->
  <div class="flex justify-center">
    <button
      type="button"
      on:click={toggleDetection}
      disabled={isLoading}
      aria-pressed={isActive}
      aria-label={isActive ? 'Durdur' : 'Başlat'}
      class="glass-btn flex items-center gap-2 px-6 py-3 rounded-full shadow-lg border border-white/30 text-blue-700 hover:text-white bg-white/30 hover:bg-blue-500/80 backdrop-blur-md transition-all duration-200"
    >
      {#if isLoading}
        <!-- Dönen yükleme spineri -->
        <svg xmlns="http://www.w3.org/2000/svg" class="w-6 h-6 animate-spin" fill="none" viewBox="0 0 24 24" stroke="currentColor">
          <circle cx="12" cy="12" r="10" stroke="currentColor" stroke-width="4" stroke-opacity="0.2" />
          <path d="M4 12a8 8 0 018-8" stroke="currentColor" stroke-width="4" stroke-linecap="round" />
        </svg>
      {:else if isActive}
        <!-- Durdurma ikonu -->
        <svg xmlns="http://www.w3.org/2000/svg" class="w-6 h-6" fill="none" viewBox="0 0 24 24" stroke="currentColor" stroke-width="2">
          <path stroke-linecap="round" stroke-linejoin="round" d="M18.364 5.636a9 9 0 11-12.728 0M12 2v4" />
        </svg>
      {:else}
        <!-- Başlatma ikonu -->
        <svg xmlns="http://www.w3.org/2000/svg" class="w-6 h-6" fill="currentColor" viewBox="0 0 24 24">
          <path d="M8 5l11 7-11 7z" />
        </svg>
      {/if}
      <span>{isActive ? 'Durdur' : 'Başlat'}</span>
    </button>
  </div>
</GlassCard>

<style>
  .glass-btn {
    background: rgba(255,255,255,0.35);
    backdrop-filter: blur(12px) saturate(180%);
    -webkit-backdrop-filter: blur(12px) saturate(180%);
    border-radius: 9999px;
    box-shadow: 0 4px 24px 0 rgba(31, 38, 135, 0.18);
    border: 1.5px solid rgba(255,255,255,0.35);
    transition: background 0.2s, box-shadow 0.2s, color 0.2s;
  }
  .glass-btn:hover {
    background: rgba(59,130,246,0.7);
    color: #fff;
  }
</style>
