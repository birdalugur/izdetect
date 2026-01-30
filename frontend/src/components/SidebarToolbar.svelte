<script>
  import { darkMode } from './store.js';
  export let open = false;

  function toggle() {
    open = !open;
  }
</script>

<div
  class="md:h-full md:w-16 w-full h-16 flex md:flex-col flex-row items-center justify-start md:py-4 px-4 md:px-0 gap-4 transition-all duration-300 z-50 rounded-xl border border-white/20 shadow-lg"
  class:bg-white-80={!$darkMode}
  class:bg-slate-900-80={$darkMode}
  style="background: {$darkMode ? 'rgba(30, 41, 59, 0.7)' : 'rgba(255, 255, 255, 0.6)'}; backdrop-filter: blur(12px);"
>
  <!-- Hamburger Menu / Toggle Button -->
  <button
    class="p-3 rounded-xl transition-all duration-200 hover:scale-105"
    class:text-slate-700={!$darkMode}
    class:text-slate-200={$darkMode}
    class:hover:bg-slate-200-50={!$darkMode}
    class:hover:bg-slate-700-50={$darkMode}
    style="background: {$darkMode ? 'rgba(51, 65, 85, 0.5)' : 'rgba(255, 255, 255, 0.5)'}"
    on:click={toggle}
    aria-label="Toggle Control Panel"
    title="Control Panel"
  >
    <svg xmlns="http://www.w3.org/2000/svg" class="w-6 h-6" fill="none" viewBox="0 0 24 24" stroke="currentColor">
      <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M4 6h16M4 12h16M4 18h16" />
    </svg>
  </button>

  <!-- Future buttons can go here -->

</div>
