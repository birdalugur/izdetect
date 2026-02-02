<script>
  import SectionCard from "./components/SectionCard.svelte";
  import SidebarToolbar from "./components/SidebarToolbar.svelte";
  import LeftPanel from "./components/LeftPanel.svelte";
  import FilterPanel from "./components/FilterPanel.svelte";
  import CameraPanel from "./components/CameraPanel.svelte";
  import MiddlePanel from "./components/MiddlePanel.svelte";
  import Notifications from "./components/Notifications.svelte";
  import Modal from "./components/Modal.svelte";
  import { darkMode } from "./components/store.js";
  import toast, { Toaster } from "svelte-french-toast";

  let messages = [];
  let activePanel = "control"; // 'control' | 'filter' | null

  const addMessage = (message) => {
    messages = [message, ...messages].slice(0, 5);
  };

  // Body class'ını dark mode'a göre değiştir
  $: {
    if (typeof document !== "undefined") {
      if ($darkMode) {
        document.body.classList.add("dark");
      } else {
        document.body.classList.remove("dark");
      }
    }
  }
</script>

<Modal />
<Toaster closeButton={true} position="top-right" />

<main
  class="relative flex flex-col md:flex-row gap-4 min-h-screen p-4"
  class:dark={$darkMode}
>
  <!-- Sidebar Toolbar -->
  <div class="flex-none z-40">
    <SidebarToolbar bind:activePanel={activePanel} />
  </div>

  <!-- Sol Panel -->
  <div
    class={`transition-all duration-300 overflow-visible ${activePanel ? "md:w-1/3 w-full" : "md:w-0 w-0 p-0 overflow-hidden"}`}
  >
    {#if activePanel === 'control'}
      <SectionCard className="overflow-visible w-full h-full">
        <LeftPanel {addMessage} open={true} />
      </SectionCard>
    {:else if activePanel === 'filter'}
      <SectionCard className="overflow-visible w-full h-full">
        <FilterPanel open={true} />
      </SectionCard>
    {:else if activePanel === 'camera'}
      <SectionCard className="overflow-visible w-full h-full">
        <CameraPanel open={true} />
      </SectionCard>
    {/if}
  </div>
  <!-- Orta Panel -->
  <div
    class={`transition-all duration-300 ${activePanel ? "md:w-1/3 w-full" : "md:w-1/2 w-full"}`}
  >
    <SectionCard className="w-full">
      <MiddlePanel leftOpen={!!activePanel} />
    </SectionCard>
  </div>
  <!-- Sağ Panel -->
  <div
    class={`transition-all duration-300 ${activePanel ? "md:w-1/3 w-full" : "md:w-1/2 w-full"}`}
  >
    <SectionCard className="w-full">
      <Notifications />
    </SectionCard>
  </div>
</main>
