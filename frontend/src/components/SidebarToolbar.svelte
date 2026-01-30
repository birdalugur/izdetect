<script>
  import { darkMode } from './store.js';

  // activePanel: 'control' | 'filter' | null
  export let activePanel = 'control';

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
  <!-- Control Panel / Dashboard Button -->
  <button
    class="p-3 rounded-xl transition-all duration-200 hover:scale-105"
    class:text-slate-700={!$darkMode}
    class:text-slate-200={$darkMode}
    class:hover:bg-slate-200-50={!$darkMode}
    class:hover:bg-slate-700-50={$darkMode}
    class:bg-blue-100={activePanel === 'control' && !$darkMode}
    class:bg-blue-900={activePanel === 'control' && $darkMode}
    style="background: {activePanel === 'control'
      ? ($darkMode ? 'rgba(30, 58, 138, 0.6)' : 'rgba(219, 234, 254, 0.8)')
      : ($darkMode ? 'rgba(51, 65, 85, 0.5)' : 'rgba(255, 255, 255, 0.5)')}"
    on:click={() => setActive('control')}
    aria-label="Toggle Control Panel"
    title="Dashboard"
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

</div>
