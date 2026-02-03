<script>
  import { darkMode } from './store.js';

  // activePanel: 'settings' | 'filter' | 'camera' | 'stats' | null
  export let activePanel = 'settings';

  function setActive(panel) {
    if (activePanel === panel) {
      activePanel = null;
    } else {
      activePanel = panel;
    }
  }
</script>

<div
  class="md:h-full md:w-16 w-full h-16 flex md:flex-col flex-row items-center justify-start md:py-4 px-4 md:px-0 gap-4 transition-all duration-300 z-50 rounded-xl border border-white/20 shadow-lg"
  class:bg-white-80={!$darkMode}
  class:bg-slate-900-80={$darkMode}
  style="background: {$darkMode ? 'rgba(30, 41, 59, 0.7)' : 'rgba(255, 255, 255, 0.6)'}; backdrop-filter: blur(12px);"
>
  <!-- Settings/Parameters Panel Button -->
  <button
    class="p-3 rounded-xl transition-all duration-200 hover:scale-105"
    class:text-slate-700={!$darkMode}
    class:text-slate-200={$darkMode}
    class:hover:bg-slate-200-50={!$darkMode}
    class:hover:bg-slate-700-50={$darkMode}
    class:bg-blue-100={activePanel === 'settings' && !$darkMode}
    class:bg-blue-900={activePanel === 'settings' && $darkMode}
    style="background: {activePanel === 'settings'
      ? ($darkMode ? 'rgba(30, 58, 138, 0.6)' : 'rgba(219, 234, 254, 0.8)')
      : ($darkMode ? 'rgba(51, 65, 85, 0.5)' : 'rgba(255, 255, 255, 0.5)')}"
    on:click={() => setActive('settings')}
    aria-label="Toggle settings Panel"
    title="Ayarlar"
  >
    <!-- Grid/Dashboard Icon -->
    <svg xmlns="http://www.w3.org/2000/svg" class="w-6 h-6" fill="none" viewBox="0 0 24 24" stroke="currentColor">
      <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M4 6a2 2 0 012-2h2a2 2 0 012 2v2a2 2 0 01-2 2H6a2 2 0 01-2-2V6zM14 6a2 2 0 012-2h2a2 2 0 012 2v2a2 2 0 01-2 2h-2a2 2 0 01-2-2V6zM4 16a2 2 0 012-2h2a2 2 0 012 2v2a2 2 0 01-2 2H6a2 2 0 01-2-2v-2zM14 16a2 2 0 012-2h2a2 2 0 012 2v2a2 2 0 01-2 2h-2a2 2 0 01-2-2v-2z" />
    </svg>
  </button>

  <!-- Filter Button -->
  <button
    class="p-3 rounded-xl transition-all duration-200 hover:scale-105"
    class:text-slate-700={!$darkMode}
    class:text-slate-200={$darkMode}
    class:hover:bg-slate-200-50={!$darkMode}
    class:hover:bg-slate-700-50={$darkMode}
    class:bg-blue-100={activePanel === 'filter' && !$darkMode}
    class:bg-blue-900={activePanel === 'filter' && $darkMode}
    style="background: {activePanel === 'filter'
      ? ($darkMode ? 'rgba(30, 58, 138, 0.6)' : 'rgba(219, 234, 254, 0.8)')
      : ($darkMode ? 'rgba(51, 65, 85, 0.5)' : 'rgba(255, 255, 255, 0.5)')}"
    on:click={() => setActive('filter')}
    aria-label="Toggle Filter Panel"
    title="Filtreler"
  >
    <!-- Funnel/Filter Icon -->
    <svg xmlns="http://www.w3.org/2000/svg" class="w-6 h-6" fill="none" viewBox="0 0 24 24" stroke="currentColor">
      <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M3 4a1 1 0 011-1h16a1 1 0 011 1v2.586a1 1 0 01-.293.707l-6.414 6.414a1 1 0 00-.293.707V17l-4 4v-6.586a1 1 0 00-.293-.707L3.293 7.293A1 1 0 013 6.586V4z" />
    </svg>
  </button>

  <!-- Camera Button -->
  <button
    class="p-3 rounded-xl transition-all duration-200 hover:scale-105"
    class:text-slate-700={!$darkMode}
    class:text-slate-200={$darkMode}
    class:hover:bg-slate-200-50={!$darkMode}
    class:hover:bg-slate-700-50={$darkMode}
    class:bg-blue-100={activePanel === 'camera' && !$darkMode}
    class:bg-blue-900={activePanel === 'camera' && $darkMode}
    style="background: {activePanel === 'camera'
      ? ($darkMode ? 'rgba(30, 58, 138, 0.6)' : 'rgba(219, 234, 254, 0.8)')
      : ($darkMode ? 'rgba(51, 65, 85, 0.5)' : 'rgba(255, 255, 255, 0.5)')}"
    on:click={() => setActive('camera')}
    aria-label="Toggle Camera Panel"
    title="Kamera Yönetimi"
  >
    <!-- Camera/Video Icon -->
    <svg xmlns="http://www.w3.org/2000/svg" class="w-6 h-6" fill="none" viewBox="0 0 24 24" stroke="currentColor">
      <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M15 10l4.553-2.276A1 1 0 0121 8.618v6.764a1 1 0 01-1.447.894L15 14M5 18h8a2 2 0 002-2V8a2 2 0 00-2-2H5a2 2 0 00-2 2v8a2 2 0 002 2z" />
    </svg>
  </button>

  <!-- Statistics Button -->
  <button
    class="p-3 rounded-xl transition-all duration-200 hover:scale-105"
    class:text-slate-700={!$darkMode}
    class:text-slate-200={$darkMode}
    class:hover:bg-slate-200-50={!$darkMode}
    class:hover:bg-slate-700-50={$darkMode}
    class:bg-blue-100={activePanel === 'stats' && !$darkMode}
    class:bg-blue-900={activePanel === 'stats' && $darkMode}
    style="background: {activePanel === 'stats'
      ? ($darkMode ? 'rgba(30, 58, 138, 0.6)' : 'rgba(219, 234, 254, 0.8)')
      : ($darkMode ? 'rgba(51, 65, 85, 0.5)' : 'rgba(255, 255, 255, 0.5)')}"
    on:click={() => setActive('stats')}
    aria-label="Toggle Statistics Panel"
    title="İstatistikler"
  >
    <!-- Bar Chart/Statistics Icon -->
    <svg xmlns="http://www.w3.org/2000/svg" class="w-6 h-6" fill="none" viewBox="0 0 24 24" stroke="currentColor">
      <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M9 19v-6a2 2 0 00-2-2H5a2 2 0 00-2 2v6a2 2 0 002 2h2a2 2 0 002-2zm0 0V9a2 2 0 012-2h2a2 2 0 012 2v10m-6 0a2 2 0 002 2h2a2 2 0 002-2m0 0V5a2 2 0 012-2h2a2 2 0 012 2v14a2 2 0 01-2 2h-2a2 2 0 01-2-2z" />
    </svg>
  </button>

  <!-- Spacer -->
  <div class="flex-1 md:flex-none"></div>

  <!-- Dark Mode Toggle -->
  <button
    class="p-3 rounded-xl border flex items-center justify-center transition-all duration-300 hover:scale-105"
    class:bg-gradient-to-br={!$darkMode}
    class:from-slate-100={!$darkMode}
    class:to-slate-200={!$darkMode}
    class:hover:from-slate-200={!$darkMode}
    class:hover:to-slate-300={!$darkMode}
    class:border-slate-300={!$darkMode}
    class:bg-slate-600={$darkMode}
    class:hover:bg-slate-500={$darkMode}
    class:border-slate-500={$darkMode}
    on:click={() => darkMode.update(n => !n)}
    aria-label="Dark Mode Toggle"
    title="Dark Mode"
  >
    {#if $darkMode}
      <!-- Sun icon -->
      <svg xmlns="http://www.w3.org/2000/svg" class="w-5 h-5 text-yellow-400 transition-colors duration-300" fill="none" viewBox="0 0 24 24" stroke="currentColor">
        <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 3v1m0 16v1m9-9h-1M4 12H3m15.364 6.364l-.707-.707M6.343 6.343l-.707-.707m12.728 0l-.707.707M6.343 17.657l-.707.707M16 12a4 4 0 11-8 0 4 4 0 018 0z" />
      </svg>
    {:else}
      <!-- Moon icon -->
      <svg xmlns="http://www.w3.org/2000/svg" class="w-5 h-5 text-slate-700 transition-colors duration-300" fill="none" viewBox="0 0 24 24" stroke="currentColor">
        <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M20.354 15.354A9 9 0 018.646 3.646 9.003 9.003 0 0012 21a9.003 9.003 0 008.354-5.646z" />
      </svg>
    {/if}
  </button>

</div>
