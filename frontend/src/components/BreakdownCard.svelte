<!--
  BreakdownCard.svelte
  Dağılım kartı. Verinin kategorilere göre dağılımını progress bar'larla gösterir.
  
  Props:
  - title: Kart başlığı
  - items: [{label_name/camera_id, count}] formatında veri
  - icon: Emoji ikon
  - maxItems: Gösterilecek maksimum item sayısı (default: 5)
  
  Top N itemleri gösterir, fazla olanlar "+X daha" şeklinde belirtilir.
-->
<script>
  import { darkMode } from "./store.js";

  export let title = "";
  export let items = [];
  export let icon = "";
  export let maxItems = 5;

  $: displayItems = items.slice(0, maxItems);
  $: totalCount = items.reduce((sum, item) => sum + (item.count || 0), 0);
</script>

<div class="breakdown-card" class:dark={$darkMode}>
  <div class="card-header">
    {#if icon}
      <div class="icon">{icon}</div>
    {/if}
    <h3>{title}</h3>
  </div>

  <div class="card-body">
    {#if displayItems.length > 0}
      <div class="items-list">
        {#each displayItems as item, index}
          {@const percentage = totalCount > 0 ? (item.count / totalCount) * 100 : 0}
          <div class="item">
            <div class="item-info">
              <span class="item-label">
                {item.label_name || item.camera_id || item.label_id || "N/A"}
              </span>
              <span class="item-count">{item.count}</span>
            </div>
            <div class="progress-bar">
              <div class="progress-fill" style="width: {percentage}%"></div>
            </div>
          </div>
        {/each}
      </div>

      {#if items.length > maxItems}
        <div class="more-indicator">
          +{items.length - maxItems} daha
        </div>
      {/if}
    {:else}
      <div class="empty-state">Veri yok</div>
    {/if}
  </div>
</div>

<style>
  .breakdown-card {
    background: rgba(255, 255, 255, 0.1);
    backdrop-filter: blur(10px);
    border: 1px solid rgba(255, 255, 255, 0.2);
    border-radius: 12px;
    padding: 16px;
    transition: all 0.3s ease;
  }

  .breakdown-card:hover {
    background: rgba(255, 255, 255, 0.15);
    border-color: rgba(255, 255, 255, 0.3);
  }

  .breakdown-card.dark {
    background: rgba(30, 30, 30, 0.4);
    border-color: rgba(255, 255, 255, 0.1);
  }

  .breakdown-card.dark:hover {
    background: rgba(30, 30, 30, 0.6);
    border-color: rgba(255, 255, 255, 0.2);
  }

  .card-header {
    display: flex;
    align-items: center;
    gap: 8px;
    margin-bottom: 12px;
  }

  .icon {
    font-size: 20px;
    line-height: 1;
  }

  .card-header h3 {
    margin: 0;
    font-size: 13px;
    font-weight: 600;
    opacity: 0.8;
    text-transform: uppercase;
    letter-spacing: 0.5px;
  }

  .card-body {
    display: flex;
    flex-direction: column;
    gap: 8px;
  }

  .items-list {
    display: flex;
    flex-direction: column;
    gap: 10px;
  }

  .item {
    display: flex;
    flex-direction: column;
    gap: 4px;
  }

  .item-info {
    display: flex;
    justify-content: space-between;
    align-items: center;
    font-size: 12px;
  }

  .item-label {
    font-weight: 500;
    text-transform: capitalize;
  }

  .item-count {
    font-weight: 700;
    opacity: 0.8;
  }

  .progress-bar {
    height: 6px;
    background: rgba(255, 255, 255, 0.1);
    border-radius: 3px;
    overflow: hidden;
  }

  .progress-fill {
    height: 100%;
    background: linear-gradient(90deg, #3b82f6, #8b5cf6);
    border-radius: 3px;
    transition: width 0.3s ease;
    min-width: 2px;
  }

  .more-indicator {
    font-size: 11px;
    opacity: 0.6;
    text-align: center;
    padding-top: 4px;
  }

  .empty-state {
    text-align: center;
    padding: 20px 0;
    opacity: 0.5;
    font-size: 13px;
  }
</style>
