<script>
  import SectionCard from './components/SectionCard.svelte';
  import LeftPanel from "./components/LeftPanel.svelte";
  import MiddlePanel from "./components/MiddlePanel.svelte";
  import Notifications from "./components/Notifications.svelte";
  import Modal from './components/Modal.svelte';
  import { darkMode } from './components/store.js';
  import toast, { Toaster } from 'svelte-french-toast';

  let messages = [];
  let leftOpen = true;

  const addMessage = (message) => {
    messages = [message, ...messages].slice(0, 5);
  };

  // Body class'ını dark mode'a göre değiştir
  $: {
    if (typeof document !== 'undefined') {
      if ($darkMode) {
        document.body.classList.add('dark');
      } else {
        document.body.classList.remove('dark');
      }
    }
  }
</script>

<Modal />
<Toaster closeButton={true} position="top-right" />

<main class="relative flex flex-col md:flex-row gap-6 min-h-screen p-4" class:dark={$darkMode}>
  <!-- Sol Panel -->
  <div class={`transition-all duration-300 overflow-visible ${leftOpen ? 'md:w-1/4 w-full' : 'md:w-0 w-0 p-0'}`}>
    {#if leftOpen}
      <SectionCard className="overflow-visible w-full">
        <LeftPanel {addMessage} bind:open={leftOpen} />
      </SectionCard>
    {:else}
      <LeftPanel {addMessage} bind:open={leftOpen} />
    {/if}
  </div>
  <!-- Orta Panel -->
  <div class={`transition-all duration-300 ${leftOpen ? 'md:w-2/5 w-full' : 'md:w-3/5 w-full'}`}>
    <SectionCard className="w-full">
      <MiddlePanel {leftOpen} />
    </SectionCard>
  </div>
  <!-- Sağ Panel -->
  <div class={`transition-all duration-300 ${leftOpen ? 'md:w-2/5 w-full' : 'md:w-2/5 w-full'}`}>
    <SectionCard className="w-full">
      <Notifications />
    </SectionCard>
  </div>
</main>


