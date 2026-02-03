<!--
  ChartWidget.svelte
  Canvas tabanlı chart widget. Line (çizgi) ve Bar (sütun) grafikleri destekler.
  
  Props:
  - title: Grafik başlığı
  - data: [{time, count}] formatında veri dizisi
  - type: "line" | "bar"
  - icon: Emoji ikon
  - height: Canvas yüksekliği (pixel)
  
  Responsive ve dark mode destekli canvas grafiği.
-->
<script>
  import { darkMode } from "./store.js";
  import { onMount } from "svelte";

  export let title = "";
  export let data = [];
  export let type = "line"; // "line" or "bar"
  export let icon = "";
  export let height = 200;

  let canvasElement;
  let chartContext;

  onMount(() => {
    if (canvasElement) {
      chartContext = canvasElement.getContext("2d");
      drawChart();
    }

    return () => {
      // Cleanup
    };
  });

  $: if (chartContext && data.length > 0) {
    drawChart();
  }

  function drawChart() {
    if (!chartContext) return;

    const canvas = canvasElement;
    const ctx = chartContext;
    const isDark = $darkMode;

    // Canvas temizle
    const rect = canvas.getBoundingClientRect();
    canvas.width = rect.width;
    canvas.height = height;

    if (data.length === 0) {
      ctx.fillStyle = isDark ? "rgba(200, 200, 200, 0.3)" : "rgba(100, 100, 100, 0.3)";
      ctx.font = "12px sans-serif";
      ctx.textAlign = "center";
      ctx.fillText("Veri yok", canvas.width / 2, canvas.height / 2);
      return;
    }

    const padding = 30;
    const chartWidth = canvas.width - padding * 2;
    const chartHeight = canvas.height - padding * 2;

    // Y eksenini hesapla
    const maxValue = Math.max(...data.map((d) => d.count || 0));
    const minValue = 0;
    const valueRange = maxValue === 0 ? 1 : maxValue;

    // X ekseni
    ctx.strokeStyle = isDark ? "rgba(255, 255, 255, 0.1)" : "rgba(0, 0, 0, 0.1)";
    ctx.lineWidth = 1;
    ctx.beginPath();
    ctx.moveTo(padding, canvas.height - padding);
    ctx.lineTo(canvas.width - padding, canvas.height - padding);
    ctx.stroke();

    // Y ekseni
    ctx.beginPath();
    ctx.moveTo(padding, padding);
    ctx.lineTo(padding, canvas.height - padding);
    ctx.stroke();

    // Grid çizgileri ve değerler
    ctx.strokeStyle = isDark ? "rgba(255, 255, 255, 0.05)" : "rgba(0, 0, 0, 0.05)";
    ctx.fillStyle = isDark ? "rgba(200, 200, 200, 0.6)" : "rgba(100, 100, 100, 0.6)";
    ctx.font = "10px sans-serif";
    ctx.textAlign = "right";

    for (let i = 0; i <= 4; i++) {
      const y =
        canvas.height - padding - (chartHeight / 4) * i;
      const value = Math.round((maxValue / 4) * i);

      // Grid çizgisi
      ctx.beginPath();
      ctx.moveTo(padding, y);
      ctx.lineTo(canvas.width - padding, y);
      ctx.stroke();

      // Y ekseni değeri
      ctx.fillText(value.toString(), padding - 8, y + 3);
    }

    // Veri noktaları
    if (type === "line") {
      drawLineChart(
        ctx,
        data,
        chartWidth,
        chartHeight,
        padding,
        valueRange,
        isDark
      );
    } else {
      drawBarChart(
        ctx,
        data,
        chartWidth,
        chartHeight,
        padding,
        valueRange,
        isDark
      );
    }

    // X ekseni etiketleri (sadece ilk, ortadaki ve son)
    ctx.fillStyle = isDark ? "rgba(200, 200, 200, 0.6)" : "rgba(100, 100, 100, 0.6)";
    ctx.textAlign = "center";
    ctx.font = "10px sans-serif";

    const indices = [0, Math.floor(data.length / 2), data.length - 1];
    indices.forEach((i) => {
      if (i < data.length) {
        const x = padding + (chartWidth / (data.length - 1 || 1)) * i;
        const label = data[i].time || "";
        const shortLabel = label.length > 10 ? label.substring(5) : label;
        ctx.fillText(shortLabel, x, canvas.height - padding + 15);
      }
    });
  }

  function drawLineChart(
    ctx,
    data,
    chartWidth,
    chartHeight,
    padding,
    valueRange,
    isDark
  ) {
    // Veri noktalarını çiz
    const pointRadius = 3;
    const points = [];

    data.forEach((d, i) => {
      const x = padding + (chartWidth / (data.length - 1 || 1)) * i;
      const y =
        padding +
        chartHeight -
        ((d.count || 0) / valueRange) * chartHeight;
      points.push({ x, y });
    });

    // Çizgi çiz
    ctx.strokeStyle = "rgb(59, 130, 246)";
    ctx.lineWidth = 2;
    ctx.beginPath();
    ctx.moveTo(points[0].x, points[0].y);
    points.forEach((p) => ctx.lineTo(p.x, p.y));
    ctx.stroke();

    // Noktaları çiz
    ctx.fillStyle = "rgb(59, 130, 246)";
    points.forEach((p) => {
      ctx.beginPath();
      ctx.arc(p.x, p.y, pointRadius, 0, Math.PI * 2);
      ctx.fill();
    });

    // Alan dolgusu
    ctx.fillStyle = "rgba(59, 130, 246, 0.1)";
    ctx.beginPath();
    ctx.moveTo(points[0].x, points[0].y);
    points.forEach((p) => ctx.lineTo(p.x, p.y));
    ctx.lineTo(points[points.length - 1].x, padding + chartHeight);
    ctx.lineTo(points[0].x, padding + chartHeight);
    ctx.closePath();
    ctx.fill();
  }

  function drawBarChart(
    ctx,
    data,
    chartWidth,
    chartHeight,
    padding,
    valueRange,
    isDark
  ) {
    const barWidth = Math.max(2, chartWidth / data.length * 0.8);
    const spacing = chartWidth / data.length;

    data.forEach((d, i) => {
      const x = padding + spacing * i + (spacing - barWidth) / 2;
      const barHeight = ((d.count || 0) / valueRange) * chartHeight;
      const y = padding + chartHeight - barHeight;

      ctx.fillStyle = "rgb(139, 92, 246)";
      ctx.fillRect(x, y, barWidth, barHeight);

      // Hover efekti için border
      ctx.strokeStyle = "rgba(139, 92, 246, 0.3)";
      ctx.lineWidth = 1;
      ctx.strokeRect(x, y, barWidth, barHeight);
    });
  }
</script>

<div class="chart-widget" class:dark={$darkMode}>
  <div class="chart-header">
    {#if icon}
      <div class="icon">{icon}</div>
    {/if}
    <h3>{title}</h3>
  </div>

  <div class="chart-container">
    <canvas bind:this={canvasElement}></canvas>
  </div>
</div>

<style>
  .chart-widget {
    background: rgba(255, 255, 255, 0.1);
    backdrop-filter: blur(10px);
    border: 1px solid rgba(255, 255, 255, 0.2);
    border-radius: 12px;
    padding: 16px;
    transition: all 0.3s ease;
  }

  .chart-widget:hover {
    background: rgba(255, 255, 255, 0.15);
    border-color: rgba(255, 255, 255, 0.3);
  }

  .chart-widget.dark {
    background: rgba(30, 30, 30, 0.4);
    border-color: rgba(255, 255, 255, 0.1);
  }

  .chart-widget.dark:hover {
    background: rgba(30, 30, 30, 0.6);
    border-color: rgba(255, 255, 255, 0.2);
  }

  .chart-header {
    display: flex;
    align-items: center;
    gap: 8px;
    margin-bottom: 12px;
  }

  .icon {
    font-size: 20px;
    line-height: 1;
  }

  .chart-header h3 {
    margin: 0;
    font-size: 13px;
    font-weight: 600;
    opacity: 0.8;
    text-transform: uppercase;
    letter-spacing: 0.5px;
  }

  .chart-container {
    width: 100%;
    overflow-x: auto;
  }

  canvas {
    width: 100%;
    display: block;
  }
</style>
