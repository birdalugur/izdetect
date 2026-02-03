<!--
  StatsPanel.svelte
  Ana istatistik paneli bileşeni. Tüm istatistikleri bir konteyner içinde gösterir.
  
  Özellikler:
  - Dönem seçimi (Bugün/Hafta/Ay)
  - Özet metrikler (toplam, aktif, kapalı bildirimler)
  - Zaman çizelgesi grafiği (saatlik/günlük veriler)
  - Nesne türleri ve kameralar breakdown'ı
  - 30 saniye polling ile otomatik güncelleme
  - Dark mode desteği
  - Dikey scroll için optimize edilmiş layout
-->
<script>
  import { darkMode, statsStore, fetchStats, changeStatsPeriod, startStatsPolling, stopStatsPolling } from "./store.js";
  import StatCard from "./StatCard.svelte";
  import BreakdownCard from "./BreakdownCard.svelte";
  import ChartWidget from "./ChartWidget.svelte";
  import Ram from "./Ram.svelte";
  import { onMount, onDestroy } from "svelte";

  let selectedPeriod = "today";
  let showPeriodMenu = false;

  const periods = [
    { value: "today", label: "Bugün" },
    { value: "week", label: "Bu Hafta" },
    { value: "month", label: "Bu Ay" }
  ];

  onMount(() => {
    // Store'dan mevcut dönemi al
    const unsubscribe = statsStore.subscribe(store => {
      selectedPeriod = store.period;
    });

    // İstatistikleri polling ile güncelle (30 saniyede bir)
    startStatsPolling(30000);

    return () => {
      unsubscribe();
      stopStatsPolling();
    };
  });

  onDestroy(() => {
    stopStatsPolling();
  });

  async function handlePeriodChange(period) {
    selectedPeriod = period;
    showPeriodMenu = false;
    await changeStatsPeriod(period);
  }

  function formatLastUpdated(date) {
    if (!date) return "Güncellenmedi";
    const now = new Date();
    const diff = now - new Date(date);
    const seconds = Math.floor(diff / 1000);

    if (seconds < 60) {
      return "az önce";
    } else if (seconds < 3600) {
      const minutes = Math.floor(seconds / 60);
      return `${minutes} dakika önce`;
    } else {
      const hours = Math.floor(seconds / 3600);
      return `${hours} saat önce`;
    }
  }
</script>

<div class="stats-panel" class:dark={$darkMode}>
  <!-- Header -->
  <div class="panel-header">
    <h2>İstatistikler</h2>

    <!-- Period Selector -->
    <div class="period-selector">
      <button
        class="period-button"
        on:click={() => (showPeriodMenu = !showPeriodMenu)}
      >
        {periods.find((p) => p.value === selectedPeriod)?.label || "Bugün"}
        <span class="dropdown-arrow">▼</span>
      </button>

      {#if showPeriodMenu}
        <div class="period-menu">
          {#each periods as period}
            <button
              class="period-option"
              class:active={period.value === selectedPeriod}
              on:click={() => handlePeriodChange(period.value)}
            >
              {period.label}
            </button>
          {/each}
        </div>
      {/if}
    </div>
  </div>

  <!-- Last Updated Info -->
  {#if $statsStore.lastUpdated}
    <div class="last-updated">
      Son güncelleme: {formatLastUpdated($statsStore.lastUpdated)}
    </div>
  {/if}

  <!-- Loading/Error States -->
  {#if $statsStore.loading}
    <div class="loading">
      <div class="spinner"></div>
      <p>İstatistikler yükleniyor...</p>
    </div>
  {:else if $statsStore.error}
    <div class="error">
      <p>⚠️ Hata: {$statsStore.error}</p>
    </div>
  {:else}
    <!-- Content -->
    <div class="stats-content">
      <!-- RAM Display -->
      <div class="stats-section">
        <Ram />
      </div>

      <!-- Summary Stats -->
      {#if $statsStore.summary}
        <div class="stats-section">
          <h3 class="section-title">Özet</h3>
          <div class="stats-grid">
            <StatCard
              title="Toplam Bildirim"
              value={$statsStore.summary.total_notifications}
              icon="📊"
            />
            <StatCard
              title="Aktif Bildirim"
              value={$statsStore.summary.active_notifications}
              icon="🔴"
            />
            <StatCard
              title="Kapalı Bildirim"
              value={$statsStore.summary.closed_notifications}
              icon="⚪"
            />
            <StatCard
              title="Aktif Oturum"
              value={$statsStore.summary.active_sessions}
              icon="▶️"
            />
          </div>
        </div>
      {/if}

      <!-- Comparison Section (if available) -->
      {#if $statsStore.comparison && $statsStore.comparison['today_vs_yesterday']}
        {@const comp = $statsStore.comparison['today_vs_yesterday']}
        <div class="stats-section">
          <h3 class="section-title">Karşılaştırma (Bugün vs Dün)</h3>
          <div class="comparison-card">
            <div class="comp-item">
              <span class="label">Bugün:</span>
              <span class="value">{comp.current_count}</span>
            </div>
            <div class="comp-item">
              <span class="label">Dün:</span>
              <span class="value">{comp.compare_count}</span>
            </div>
            <div class="comp-item">
              <span class="label">Değişim:</span>
              <span
                class="badge"
                class:positive={comp.trend === "up"}
                class:negative={comp.trend === "down"}
              >
                {#if comp.trend === "up"}
                  ↑
                {:else if comp.trend === "down"}
                  ↓
                {:else}
                  →
                {/if}
                {Math.abs(comp.percent_change)}%
              </span>
            </div>
          </div>
        </div>
      {/if}

      <!-- Timeline Chart -->
      {#if $statsStore.timeline && $statsStore.timeline.length > 0}
        <div class="stats-section">
          <h3 class="section-title">Zaman Çizelgesi</h3>
          <ChartWidget
            title="Saatlik Bildirimler"
            data={$statsStore.timeline}
            type="line"
            icon="📈"
            height={200}
          />
        </div>
      {/if}

      <!-- Breakdown Cards -->
      <div class="breakdowns-grid">
        {#if $statsStore.byLabel && $statsStore.byLabel.length > 0}
          <BreakdownCard
            title="Nesne Türleri"
            items={$statsStore.byLabel}
            icon="🏷️"
            maxItems={5}
          />
        {/if}

        {#if $statsStore.byCamera && $statsStore.byCamera.length > 0}
          <BreakdownCard
            title="Kameralar"
            items={$statsStore.byCamera}
            icon="📷"
            maxItems={5}
          />
        {/if}
      </div>
    </div>
  {/if}
</div>

<style>
  .stats-panel {
    display: flex;
    flex-direction: column;
    gap: 16px;
    height: 100%;
    background: rgba(255, 255, 255, 0.05);
    padding: 16px;
    border-radius: 12px;
    overflow-y: auto;
    overflow-x: hidden;
  }

  .stats-panel.dark {
    background: rgba(0, 0, 0, 0.3);
  }

  /* Scrollbar styling */
  .stats-panel::-webkit-scrollbar {
    width: 8px;
  }

  .stats-panel::-webkit-scrollbar-track {
    background: rgba(255, 255, 255, 0.05);
    border-radius: 4px;
  }

  .stats-panel::-webkit-scrollbar-thumb {
    background: rgba(255, 255, 255, 0.2);
    border-radius: 4px;
  }

  .stats-panel::-webkit-scrollbar-thumb:hover {
    background: rgba(255, 255, 255, 0.3);
  }

  .panel-header {
    display: flex;
    justify-content: space-between;
    align-items: center;
    gap: 12px;
    margin-bottom: 8px;
    flex-wrap: wrap;
  }

  .panel-header h2 {
    margin: 0;
    font-size: 18px;
    font-weight: 700;
  }

  .period-selector {
    position: relative;
  }

  .period-button {
    background: rgba(59, 130, 246, 0.2);
    border: 1px solid rgba(59, 130, 246, 0.4);
    color: inherit;
    padding: 6px 12px;
    border-radius: 6px;
    font-size: 12px;
    font-weight: 600;
    cursor: pointer;
    display: flex;
    align-items: center;
    gap: 6px;
    transition: all 0.2s ease;
  }

  .period-button:hover {
    background: rgba(59, 130, 246, 0.3);
    border-color: rgba(59, 130, 246, 0.6);
  }

  .dropdown-arrow {
    font-size: 10px;
    transition: transform 0.2s ease;
  }

  .period-button:active .dropdown-arrow {
    transform: rotate(180deg);
  }

  .period-menu {
    position: absolute;
    top: 100%;
    right: 0;
    background: rgba(255, 255, 255, 0.1);
    backdrop-filter: blur(10px);
    border: 1px solid rgba(255, 255, 255, 0.2);
    border-radius: 8px;
    margin-top: 4px;
    z-index: 10;
    overflow: hidden;
    min-width: 120px;
  }

  .period-option {
    display: block;
    width: 100%;
    padding: 8px 12px;
    background: none;
    border: none;
    color: inherit;
    text-align: left;
    cursor: pointer;
    font-size: 12px;
    transition: background 0.2s ease;
  }

  .period-option:hover {
    background: rgba(255, 255, 255, 0.1);
  }

  .period-option.active {
    background: rgba(59, 130, 246, 0.3);
    font-weight: 600;
  }

  .last-updated {
    font-size: 11px;
    opacity: 0.6;
    text-align: right;
  }

  .loading {
    display: flex;
    flex-direction: column;
    align-items: center;
    justify-content: center;
    gap: 12px;
    padding: 40px 20px;
    opacity: 0.7;
  }

  .spinner {
    width: 32px;
    height: 32px;
    border: 3px solid rgba(255, 255, 255, 0.1);
    border-top-color: rgb(59, 130, 246);
    border-radius: 50%;
    animation: spin 1s linear infinite;
  }

  @keyframes spin {
    to {
      transform: rotate(360deg);
    }
  }

  .loading p {
    margin: 0;
    font-size: 13px;
  }

  .error {
    background: rgba(239, 68, 68, 0.1);
    border: 1px solid rgba(239, 68, 68, 0.3);
    border-radius: 8px;
    padding: 12px;
    color: #ef4444;
    font-size: 12px;
  }

  .error p {
    margin: 0;
  }

  .stats-content {
    display: flex;
    flex-direction: column;
    gap: 16px;
  }

  .stats-section {
    display: flex;
    flex-direction: column;
    gap: 12px;
  }

  .section-title {
    margin: 0;
    font-size: 12px;
    font-weight: 600;
    opacity: 0.7;
    text-transform: uppercase;
    letter-spacing: 0.5px;
  }

  .stats-grid {
    display: grid;
    grid-template-columns: 1fr 1fr;
    gap: 12px;
  }

  .comparison-card {
    background: rgba(255, 255, 255, 0.1);
    backdrop-filter: blur(10px);
    border: 1px solid rgba(255, 255, 255, 0.2);
    border-radius: 12px;
    padding: 16px;
    display: flex;
    justify-content: space-around;
    gap: 12px;
  }

  .comp-item {
    display: flex;
    flex-direction: column;
    align-items: center;
    gap: 4px;
  }

  .comp-item .label {
    font-size: 11px;
    opacity: 0.6;
  }

  .comp-item .value {
    font-size: 24px;
    font-weight: 700;
  }

  .badge {
    display: inline-flex;
    align-items: center;
    gap: 4px;
    padding: 4px 8px;
    border-radius: 6px;
    font-weight: 600;
    font-size: 12px;
    background: rgba(239, 68, 68, 0.2);
    color: #ef4444;
  }

  .badge.positive {
    background: rgba(34, 197, 94, 0.2);
    color: #22c55e;
  }

  .badge.negative {
    background: rgba(239, 68, 68, 0.2);
    color: #ef4444;
  }

  .breakdowns-grid {
    display: grid;
    grid-template-columns: 1fr;
    gap: 12px;
  }

  @media (min-width: 480px) {
    .stats-grid {
      grid-template-columns: repeat(2, 1fr);
    }

    .breakdowns-grid {
      grid-template-columns: repeat(2, 1fr);
    }
  }
</style>
