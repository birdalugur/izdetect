<script>
  export let currentPage = 1;
  export let totalPages = 1;
  export let onPageChange = () => {};

  // Akıllı sayfa numarası hesaplama
  $: visiblePages = getVisiblePages(currentPage, totalPages);

  function getVisiblePages(current, total) {
    const maxVisible = 5; // Maksimum görünür sayfa sayısı
    let start = Math.max(1, current - Math.floor(maxVisible / 2));
    let end = Math.min(total, start + maxVisible - 1);
    
    // Eğer sonda isek, başlangıcı ayarla
    if (end - start + 1 < maxVisible) {
      start = Math.max(1, end - maxVisible + 1);
    }
    
    const pages = [];
    for (let i = start; i <= end; i++) {
      pages.push(i);
    }
    return pages;
  }
</script>

{#if totalPages > 1}
  <div class="flex justify-center items-center gap-1 mt-1">
    <!-- İlk sayfa butonu -->
    {#if currentPage > 3}
      <button
        on:click={() => onPageChange(1)}
        class="w-8 h-8 text-xs rounded glass-btn hover:bg-blue-500/70 hover:text-white transition-all duration-200"
      >1</button>
      {#if currentPage > 4}
        <span class="px-2 text-gray-500">...</span>
      {/if}
    {/if}

    <!-- Önceki butonu -->
    <button
      on:click={() => onPageChange(currentPage - 1)}
      disabled={currentPage === 1}
      class="px-3 py-1 text-xs rounded glass-btn disabled:opacity-50 hover:bg-blue-500/70 hover:text-white transition-all duration-200"
    >‹</button>

    <!-- Görünür sayfa numaraları -->
    {#each visiblePages as page}
      <button
        on:click={() => onPageChange(page)}
        class={`w-8 h-8 text-xs rounded transition-all duration-200 ${
          currentPage === page
            ? 'bg-blue-500/80 text-white shadow-lg scale-105'
            : 'glass-btn hover:bg-blue-500/70 hover:text-white'
        }`}
      >{page}</button>
    {/each}

    <!-- Sonraki butonu -->
    <button
      on:click={() => onPageChange(currentPage + 1)}
      disabled={currentPage === totalPages}
      class="px-3 py-1 text-xs rounded glass-btn disabled:opacity-50 hover:bg-blue-500/70 hover:text-white transition-all duration-200"
    >›</button>

    <!-- Son sayfa butonu -->
    {#if currentPage < totalPages - 2}
      {#if currentPage < totalPages - 3}
        <span class="px-2 text-gray-500">...</span>
      {/if}
      <button
        on:click={() => onPageChange(totalPages)}
        class="w-8 h-8 text-xs rounded glass-btn hover:bg-blue-500/70 hover:text-white transition-all duration-200"
      >{totalPages}</button>
    {/if}
  </div>
{/if}

<style>
  .glass-btn {
    background: rgba(255,255,255,0.35);
    backdrop-filter: blur(12px) saturate(180%);
    -webkit-backdrop-filter: blur(12px) saturate(180%);
    border-radius: 6px;
    box-shadow: 0 2px 12px 0 rgba(31, 38, 135, 0.15);
    border: 1px solid rgba(255,255,255,0.25);
    transition: all 0.2s ease;
  }
  .glass-btn:hover {
    box-shadow: 0 4px 16px 0 rgba(31, 38, 135, 0.25);
    transform: translateY(-1px);
  }
  .glass-btn:disabled {
    cursor: not-allowed;
    transform: none;
    box-shadow: 0 2px 12px 0 rgba(31, 38, 135, 0.1);
  }
</style> 