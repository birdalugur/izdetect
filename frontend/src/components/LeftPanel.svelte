<!-- src/components/LeftPanel.svelte -->
<script>
  import GlassCard from './GlassCard.svelte';
  import Control   from './Control.svelte';
  import Ram       from './Ram.svelte';
  import { darkMode } from './store.js';

  export let addMessage;
  export let open = true;
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
          </div>
        </GlassCard>
      </div>
      
      <Control {addMessage} />
      <Ram />
    </div>
  {/if}
</div>



