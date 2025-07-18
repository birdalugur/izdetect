<!-- src/components/GlassCard.svelte -->
<script>
  import { darkMode } from './store.js';
  export let className = '';
</script>

<div class={`glass-card w-full p-6 ${className}`} class:dark={$darkMode}>
  <slot />
</div>

<style>
  .glass-card {
    /* Light mode - Ultra clean glass */
    background: rgba(255, 255, 255, 0.6);
    
    /* Glassmorphism */
    backdrop-filter: blur(10px) saturate(110%);
    -webkit-backdrop-filter: blur(10px) saturate(110%);
    
    /* Border ve shadow */
    border-radius: 12px;
    border: 1px solid rgba(190, 192, 194, 0.3);
    box-shadow: 
      /* Soft definition */
      0 4px 12px -2px rgba(15, 23, 42, 0.04),
      /* Ambient glow */
      0 2px 6px -1px rgba(51, 65, 85, 0.03),
      /* Highlight ring */
      0 0 0 0.5px rgba(255, 255, 255, 0.6),
      /* Inner brightness */
      inset 0 1px 2px rgba(255, 255, 255, 0.3);
    
    position: relative;
    
    /* Smooth transitions */
    transition: all 0.25s cubic-bezier(0.4, 0, 0.2, 1);
  }

  /* Dark mode - Refined slate glass */
  .glass-card.dark {
    background: rgba(51, 65, 85, 0.7);
    
    border: 1px solid rgba(49, 59, 73, 0.6);
    box-shadow: 
      /* Soft definition */
      0 4px 12px -2px rgba(0, 0, 0, 0.15),
      /* Ambient depth */
      0 2px 6px -1px rgba(15, 23, 42, 0.2),
      /* Highlight ring */
      0 0 0 0.5px rgba(100, 116, 139, 0.4),
      /* Inner brightness */
      inset 0 1px 2px rgba(148, 163, 184, 0.15);
  }
</style>
