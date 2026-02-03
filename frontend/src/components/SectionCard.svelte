<!-- src/components/SectionCard.svelte -->
<script>
  import { darkMode } from './store.js';
  export let className = "";
</script>

<div class="section-card {className}" class:dark={$darkMode}>
  <slot />
</div>

<style>
  .section-card {
    /* Light mode - Crystal clear */
    background: rgba(255, 255, 255, 0.85);
    
    /* Glassmorphism */
    backdrop-filter: blur(16px) saturate(120%);
    -webkit-backdrop-filter: blur(16px) saturate(120%);
    
    /* Border ve shadow */
    border: 1px solid rgba(241, 245, 249, 0.8);
    border-radius: 18px;
    box-shadow: 
      /* Ana gölge - soft */
      0 16px 40px -8px rgba(15, 23, 42, 0.08),
      /* Ambient gölge */
      0 6px 16px -4px rgba(51, 65, 85, 0.06),
      /* Definition gölge */
      0 2px 8px -2px rgba(71, 85, 105, 0.04),
      /* Highlight ring */
      0 0 0 1px rgba(255, 255, 255, 0.7);
    
    /* Layout */
    padding: 2rem;
    display: flex;
    flex-direction: column;
    flex: 1;
    min-height: 0;
    position: relative;
    overflow: hidden;
    
    /* Smooth transitions */
    transition: all 0.3s cubic-bezier(0.4, 0, 0.2, 1);
  }

  /* Dark mode - Professional slate */
  .section-card.dark {
    background: rgba(30, 41, 59, 0.9);
    
    border: 1px solid rgba(51, 65, 85, 0.5);
    box-shadow: 
      /* Ana gölge - deep */
      0 16px 40px -8px rgba(0, 0, 0, 0.25),
      /* Ambient gölge */
      0 6px 16px -4px rgba(15, 23, 42, 0.3),
      /* Definition gölge */
      0 2px 8px -2px rgba(30, 41, 59, 0.4),
      /* Highlight ring - subtle */
      0 0 0 1px rgba(71, 85, 105, 0.3),
      /* Inner glow */
      inset 0 1px 2px rgba(148, 163, 184, 0.1);
  }

  /* Responsive tasarım */
  @media (max-width: 768px) {
    .section-card {
      padding: 1rem;
      border-radius: 16px;
      min-height: 300px;
    }
  }
</style> 