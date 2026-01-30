<script>
  import GlassCard from './GlassCard.svelte';
  import Filter from './Filter.svelte';
  import { darkMode } from './store.js';

  export let open = true;
</script>

<div class="relative h-full">
  {#if open}
    <div class="pt-1 flex flex-col gap-2 h-full overflow-y-auto pb-1 transition-all duration-300">
      <!-- Header Section -->
      <div class="mb-1">
        <GlassCard className="p-3 border-gray-200/40 !bg-gray-100/60 dark:!bg-slate-300/60">
           <div class="flex items-center justify-between">
              <h2 class="text-base font-bold leading-tight transition-colors duration-300" class:text-slate-800={!$darkMode} class:text-slate-100={$darkMode}>
                 Filtreler
              </h2>
           </div>
        </GlassCard>
      </div>

      <Filter />
    </div>
  {/if}
</div>
