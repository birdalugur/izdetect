<!-- src/components/Filter.svelte -->
<script>
  import GlassCard from './GlassCard.svelte';
  import NotificationModal from './NotificationModal.svelte';
  import toast, { Toaster } from 'svelte-french-toast';
  import { modalStore } from './store.js';

  let baslangicTarih    = '';
  let bitisTarih        = '';
  let baslangicSaat     = '';
  let bitisSaat         = '';
  let seciliEtiketler   = { insan: false, arac: false, hayvan: false };

  function filtrele() {
    if (!baslangicTarih || !bitisTarih) {
      toast.error("Lütfen başlangıç ve bitiş tarihlerini seçin.", { duration: 3000, position: 'top-right' });
      return;
    }
    modalStore.set({
      isOpen: true,
      component: NotificationModal,
      props: {
        filterParams: filtreParametreleri
      }
    });
  }

  $: filtreParametreleri = {
    startDate: baslangicTarih,
    endDate:   bitisTarih,
    startTime: baslangicSaat,
    endTime:   bitisSaat,
    selectedLabels: seciliEtiketler
  };
</script>

<GlassCard className="max-w-md w-full mx-auto p-6 space-y-3">

  <!-- Tarih & Saat -->
  <div class="grid grid-cols-1 sm:grid-cols-2 gap-6">
    <div class="flex flex-col space-y-2">
      <label for="baslangicTarih" class="text-white-900 dark:text-black-200 font-medium">Başlangıç</label>
      <input id="baslangicTarih" type="date" bind:value={baslangicTarih}
        class="h-10 px-3 bg-white/20 dark:bg-white-700/50 border border-white-300 dark:border-white-600 text-white-700 dark:text-white-200 rounded focus:outline-none focus:ring-2 focus:ring-white-200 dark:focus:ring-white-400" />
      <input id="baslangicSaat" type="time" bind:value={baslangicSaat}
        class="h-10 px-3 bg-white/20 dark:bg-white-700/50 border border-white-300 dark:border-white-600 text-white-700 dark:text-white-200 rounded focus:outline-none focus:ring-2 focus:ring-white-200 dark:focus:ring-white-400" />
    </div>
    <div class="flex flex-col space-y-2">
      <label for="bitisTarih" class="text-white-900 dark:text-black-200 font-medium">Bitiş</label>
      <input id="bitisTarih" type="date" bind:value={bitisTarih}
        class="h-10 px-3 bg-white/20 dark:bg-white-700/50 border border-white-300 dark:border-white-600 text-white-700 dark:text-white-200 rounded focus:outline-none focus:ring-2 focus:ring-white-200 dark:focus:ring-slate-400" />
      <input id="bitisSaat" type="time" bind:value={bitisSaat}
        class="h-10 px-3 bg-white/20 dark:bg-white-700/50 border border-white-300 dark:border-white-600 text-white-700 dark:text-white-200 rounded focus:outline-none focus:ring-2 focus:ring-white-200 dark:focus:ring-white-400" />
    </div>
  </div>

  <!-- Etiketler -->
  <div class="flex justify-center space-x-2">
    {#each Object.entries(seciliEtiketler) as [key, val]}
      <button
        type="button"
        on:click={() => seciliEtiketler[key] = !val}
        class="flex-1 py-3 px-4 rounded-full transition-all duration-200 font-semibold flex items-center justify-center gap-2 border-2
          {val
            ? (key === 'insan' ? 'bg-green-500 border-green-600 text-white shadow-lg scale-105' : 
               key === 'arac' ? 'bg-blue-500 border-blue-600 text-white shadow-lg scale-105' : 
               key === 'hayvan' ? 'bg-orange-500 border-orange-600 text-white shadow-lg scale-105' : 
               'bg-gray-500 border-gray-600 text-white shadow-lg scale-105')
            : (key === 'insan' ? 'bg-green-100 border-green-300 text-green-800 hover:bg-green-200' :
               key === 'arac' ? 'bg-blue-100 border-blue-300 text-blue-800 hover:bg-blue-200' : 
               key === 'hayvan' ? 'bg-orange-100 border-orange-300 text-orange-800 hover:bg-orange-200' : 
               'bg-gray-100 border-gray-300 text-gray-800 hover:bg-gray-200')}"
      >
        <!-- İkonlar -->
        {#if key === 'insan'}
          <svg xmlns="http://www.w3.org/2000/svg" class="w-4 h-4" fill="currentColor" viewBox="0 0 24 24">
            <path d="M12 12c2.21 0 4-1.79 4-4s-1.79-4-4-4-4 1.79-4 4 1.79 4 4 4zm0 2c-2.67 0-8 1.34-8 4v2h16v-2c0-2.66-5.33-4-8-4z"/>
          </svg>
        {:else if key === 'arac'}
          <svg xmlns="http://www.w3.org/2000/svg" class="w-4 h-4" fill="currentColor" viewBox="0 0 24 24">
            <path d="M18.92 6.01C18.72 5.42 18.16 5 17.5 5h-11c-.66 0-1.22.42-1.42 1.01L3 12v8c0 .55.45 1 1 1h1c.55 0 1-.45 1-1v-1h12v1c0 .55.45 1 1 1h1c.55 0 1-.45 1-1v-8l-2.08-5.99zM6.5 16c-.83 0-1.5-.67-1.5-1.5S5.67 13 6.5 13s1.5.67 1.5 1.5S7.33 16 6.5 16zm11 0c-.83 0-1.5-.67-1.5-1.5s.67-1.5 1.5-1.5 1.5.67 1.5 1.5-.67 1.5-1.5 1.5zM5 11l1.5-4.5h11L19 11H5z"/>
          </svg>
        {:else if key === 'hayvan'}
          <svg xmlns="http://www.w3.org/2000/svg" class="w-4 h-4" fill="currentColor" viewBox="0 0 24 24">
            <path d="M4.5 12c0-.83.67-1.5 1.5-1.5s1.5.67 1.5 1.5-.67 1.5-1.5 1.5-1.5-.67-1.5-1.5zm11-1.5c.83 0 1.5.67 1.5 1.5s-.67 1.5-1.5 1.5-1.5-.67-1.5-1.5.67-1.5 1.5-1.5zm5.5 1.5c0 .83-.67 1.5-1.5 1.5s-1.5-.67-1.5-1.5.67-1.5 1.5-1.5 1.5.67 1.5 1.5zm-10 6.5c-2.76 0-5-2.24-5-5 0-.34.04-.67.09-1h2.84c-.59.58-1.43 1-2.43 1v2c2.21 0 4 1.79 4 4 0 .34-.04.67-.09 1h2.84c-.59-.58-1.43-1-2.43-1v-2z"/>
          </svg>
        {/if}
        
        {key.charAt(0).toUpperCase() + key.slice(1)}
      </button>
    {/each}
  </div>

  <!-- Uygula -->
  <div class="text-center">
    <button
      on:click={filtrele}
      class="px-8 py-3 bg-gradient-to-r from-blue-600 to-indigo-600 hover:from-blue-700 hover:to-indigo-700 text-white font-semibold rounded-full shadow-lg hover:shadow-xl transition-all duration-200 flex items-center gap-2 mx-auto"
    >
      <svg xmlns="http://www.w3.org/2000/svg" class="w-5 h-5" fill="none" viewBox="0 0 24 24" stroke="currentColor">
        <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M3 4a1 1 0 011-1h16a1 1 0 011 1v2.586a1 1 0 01-.293.707l-6.414 6.414a1 1 0 00-.293.707V17l-4 4v-6.586a1 1 0 00-.293-.707L3.293 7.293A1 1 0 013 6.586V4z" />
      </svg>
      Uygula
    </button>
  </div>
</GlassCard>
