<!-- src/components/LeftPanel.svelte -->
<script>
  import GlassCard from './GlassCard.svelte';
  import Control   from './Control.svelte';
  import Ram       from './Ram.svelte';
  import { darkMode } from './store.js';

  export let addMessage;
  export let open = true;

  function toggleDarkMode() {
    darkMode.update(n => !n);
  }
</script>

<div class="relative h-full">
  <!-- Panel Content -->
  {#if open}
    <div class="pt-1 flex flex-col gap-2 h-full overflow-y-auto pb-1 transition-all duration-300">
      <!-- Logo Section - Horizontal Layout -->
      <div class="mb-1">
        <GlassCard   className="p-2.5 border-gray-200/40 !bg-gray-100/60 dark:!bg-slate-300/60">
          <div class="flex items-center gap-3">
            <!-- Logo Container -->
            <div class="relative flex-shrink-0">
              <!-- Subtle Background -->
              <div class="absolute inset-0"></div>
              <div class="relative w-10 h-12 rounded-xl p-1 overflow-hidden">
                <img 
                  src="/img/logo.png" 
                  alt="IzDetect Logo" 
                  class="w-full h-full object-contain"
                  on:error={(e) => {
                    e.target.style.display = 'none';
                    e.target.nextElementSibling.style.display = 'block';
                  }}
                />
                <svg 
                  xmlns="http://www.w3.org/2000/svg" 
                  class="w-5 h-5 text-gray-600 hidden absolute top-1/2 left-1/2 transform -translate-x-1/2 -translate-y-1/2" 
                  fill="none" 
                  viewBox="0 0 24 24" 
                  stroke="currentColor"
                >
                  <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M15 10l4.553-2.276A1 1 0 0121 8.618v6.764a1 1 0 01-1.447.894L15 14M5 18h8a2 2 0 002-2V8a2 2 0 00-2-2H5a2 2 0 00-2 2v8a2 2 0 002 2z" />
                </svg>
              </div>
            </div>
            
            <!-- Text Content -->
            <div  class="flex-1 min-w-0">
              <h2  class="text-base font-bold leading-tight transition-colors duration-300" class:text-slate-800={!$darkMode} class:text-slate-100={$darkMode}>İzGöz </h2>
              <p class="text-xs font-medium transition-colors duration-300" class:text-slate-600={!$darkMode} class:text-slate-300={$darkMode}>Drone Tabanlı Akıllı Gözlem Sistemi</p>
            </div>

            <!-- Dark Mode Toggle -->
            <button
              class="flex-shrink-0 w-8 h-8 rounded-lg border flex items-center justify-center transition-all duration-300 hover:scale-105 shadow-sm"
              class:bg-gradient-to-br={!$darkMode}
              class:from-slate-100={!$darkMode}
              class:to-slate-200={!$darkMode}
              class:hover:from-slate-200={!$darkMode}
              class:hover:to-slate-300={!$darkMode}
              class:border-slate-300={!$darkMode}
              class:bg-slate-600={$darkMode}
              class:hover:bg-slate-500={$darkMode}
              class:border-slate-500={$darkMode}
              on:click={toggleDarkMode}
              aria-label="Dark Mode Toggle"
            >
              {#if $darkMode}
                <!-- Sun icon -->
                <svg xmlns="http://www.w3.org/2000/svg" class="w-4 h-4 text-yellow-400 transition-colors duration-300" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                  <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 3v1m0 16v1m9-9h-1M4 12H3m15.364 6.364l-.707-.707M6.343 6.343l-.707-.707m12.728 0l-.707.707M6.343 17.657l-.707.707M16 12a4 4 0 11-8 0 4 4 0 018 0z" />
                </svg>
              {:else}
                <!-- Moon icon -->
                <svg xmlns="http://www.w3.org/2000/svg" class="w-4 h-4 text-slate-700 transition-colors duration-300" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                  <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M20.354 15.354A9 9 0 018.646 3.646 9.003 9.003 0 0012 21a9.003 9.003 0 008.354-5.646z" />
                </svg>
              {/if}
            </button>
          </div>
        </GlassCard>
      </div>
      
      <Control {addMessage} />
      <Ram />
    </div>
  {/if}
</div>



