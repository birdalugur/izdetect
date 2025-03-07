<script>
    import { onMount } from "svelte";
  
    let ram = { total: 1, used: 0 };
  
    async function fetchRam() {
      const response = await fetch("http://localhost:8000/ram");
      ram = await response.json();
    }
  
    onMount(() => {
      fetchRam();
      setInterval(fetchRam, 2000);
    });
  </script>
  
  <div class="bg-gray-100 p-6 rounded-lg shadow-lg mx-auto border border-gray-300">
    <div class="max-w-lg mx-auto ">
      <h1 class="text-xl font-bold text-center mb-4">RAM Kullanımı</h1>
      <div class="relative w-full h-8 bg-gray-300 rounded-lg overflow-hidden">
        <div
          class="h-full bg-green-500 transition-all"
          style="width: {ram.used / ram.total * 100}%"
        ></div>
      </div>
      <p class="text-center mt-2">
        Kullanılan RAM: {(ram.used / (1024 ** 3)).toFixed(2)} GB / {(ram.total / (1024 ** 3)).toFixed(2)} GB
      </p>
    </div>
  </div>
 
  