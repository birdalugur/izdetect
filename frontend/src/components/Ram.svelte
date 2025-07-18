<!-- src/components/Ram.svelte -->
<script>
  import { onMount } from 'svelte';
  import GlassCard from './GlassCard.svelte';
  import { darkMode } from './store.js';

  let ram = { total: 1, used: 0 };

  async function fetchRam() {
    try {
      const res = await fetch('http://localhost:8000/system/ram');
      if (res.ok) ram = await res.json();
    } catch (err) {
      console.error('RAM fetch error:', err);
    }
  }

  onMount(() => {
    fetchRam();
    const interval = setInterval(fetchRam, 2000);
    return () => clearInterval(interval);
  });

  $: usedGB = (ram.used/(1024**3)).toFixed(2);
  $: totalGB = (ram.total/(1024**3)).toFixed(2);
  $: percentage = ((ram.used/ram.total)*100).toFixed(1);
  $: getBarColor = (pct) => {
    if (pct < 50) return 'from-emerald-400 to-green-500';
    if (pct < 75) return 'from-yellow-400 to-orange-500';
    return 'from-orange-500 to-red-500';
  };
</script>

<GlassCard className="max-w-sm w-full mx-auto p-4 space-y-4">
  <div class="flex flex-col space-y-4">
    <!-- Modern Progress Bar -->
    <div class="relative">
      <!-- Arka plan bar -->
      <div class="w-full h-8 bg-white/40 backdrop-blur-sm rounded-xl border border-white/30 shadow-inner overflow-hidden">
        <!-- Progress bar -->
        <div
          class="h-full bg-gradient-to-r {getBarColor(percentage)} transition-all duration-700 ease-out relative rounded-xl"
          style="width: {percentage}%"
        >
          <!-- Parlama efekti -->
          <div class="absolute inset-0 bg-gradient-to-r from-transparent via-white/20 to-transparent animate-pulse"></div>
        </div>
        
        <!-- Sayı barın içinde -->
        <div class="absolute inset-0 flex items-center justify-center">
          <span class="text-sm font-bold drop-shadow-sm transition-colors duration-300" class:text-slate-800={!$darkMode} class:text-white={$darkMode}>
            {usedGB} GB / {totalGB} GB
          </span>
        </div>
        
        <!-- Yüzde - sağ üst köşe -->
        <div class="absolute top-1 right-2">
          <span class="text-xs font-semibold px-2 py-0.5 rounded-full backdrop-blur-sm transition-all duration-300 {!$darkMode ? 'text-slate-700 bg-white/60' : 'text-slate-200 bg-slate-600/60'}">
            %{percentage}
          </span>
        </div>
      </div>
    </div>

    <!-- Durum göstergesi -->
    <div class="flex items-center justify-between text-xs transition-colors duration-300" class:text-slate-600={!$darkMode} class:text-slate-400={$darkMode}>
      <div class="flex items-center gap-2">
        <div class="w-2 h-2 rounded-full bg-gradient-to-r {getBarColor(percentage)}"></div>
        <span>
          {#if percentage < 50}
            Optimal
          {:else if percentage < 75}
            Orta Kullanım
          {:else}
            Yüksek Kullanım
          {/if}
        </span>
      </div>
      <span class="font-mono">
        {(ram.total - ram.used)/(1024**3) > 1 ? ((ram.total - ram.used)/(1024**3)).toFixed(2) + ' GB Boş' : ((ram.total - ram.used)/(1024**2)).toFixed(0) + ' MB Boş'}
      </span>
    </div>
  </div>
</GlassCard>
