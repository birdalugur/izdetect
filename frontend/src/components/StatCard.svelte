<!--
  StatCard.svelte
  Tek bir metrik kartı. Değer, trend, ikon ve önceki dönem karşılaştırması gösterir.
  
  Props:
  - title: Kart başlığı
  - value: Ana değer
  - previousValue: Önceki dönem değeri
  - trend: "up" | "down" | null
  - percentChange: Yüzde değişim
  - icon: Emoji ikon
-->
<script>
  import { darkMode } from "./store.js";

  export let title = "";
  export let value = 0;
  export let previousValue = 0;
  export let unit = "";
  export let icon = "";
  export let trend = null; // "up", "down", or null
  export let percentChange = 0;

  $: isPositive = trend === "up";
  $: isNegative = trend === "down";
</script>

<div class="stat-card" class:dark={$darkMode}>
  <div class="card-header">
    {#if icon}
      <div class="icon">{icon}</div>
    {/if}
    <h3>{title}</h3>
  </div>

  <div class="card-body">
    <div class="main-value">
      {value.toLocaleString()}
      {#if unit}
        <span class="unit">{unit}</span>
      {/if}
    </div>

    {#if previousValue !== undefined && previousValue !== null}
      <div class="comparison">
        {#if trend}
          <span class="badge" class:positive={isPositive} class:negative={isNegative}>
            {#if isPositive}
              <span class="arrow">↑</span>
            {:else if isNegative}
              <span class="arrow">↓</span>
            {/if}
            {Math.abs(percentChange).toFixed(1)}%
          </span>
        {/if}
        <span class="prev-label">geçen: {previousValue.toLocaleString()}</span>
      </div>
    {/if}
  </div>
</div>

<style>
  .stat-card {
    background: rgba(255, 255, 255, 0.1);
    backdrop-filter: blur(10px);
    border: 1px solid rgba(255, 255, 255, 0.2);
    border-radius: 12px;
    padding: 16px;
    transition: all 0.3s ease;
  }

  .stat-card:hover {
    background: rgba(255, 255, 255, 0.15);
    border-color: rgba(255, 255, 255, 0.3);
  }

  .stat-card.dark {
    background: rgba(30, 30, 30, 0.4);
    border-color: rgba(255, 255, 255, 0.1);
  }

  .stat-card.dark:hover {
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

  .main-value {
    font-size: 28px;
    font-weight: 700;
    line-height: 1;
    letter-spacing: -0.5px;
  }

  .unit {
    font-size: 16px;
    opacity: 0.7;
    margin-left: 4px;
  }

  .comparison {
    display: flex;
    align-items: center;
    gap: 8px;
    font-size: 12px;
  }

  .badge {
    display: inline-flex;
    align-items: center;
    gap: 2px;
    padding: 2px 6px;
    border-radius: 6px;
    font-weight: 600;
    font-size: 11px;
  }

  .badge.positive {
    background: rgba(34, 197, 94, 0.2);
    color: #22c55e;
  }

  .badge.negative {
    background: rgba(239, 68, 68, 0.2);
    color: #ef4444;
  }

  .arrow {
    font-size: 10px;
  }

  .prev-label {
    opacity: 0.6;
    font-size: 11px;
  }
</style>
