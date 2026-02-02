<script>
    import LiveCamera from "./LiveCamera.svelte";
    import Table from "./Table.svelte";
    
    export let leftOpen = true;
</script>

<div class="flex flex-col gap-5 h-full overflow-y-auto transition-all duration-300">
    <LiveCamera />
    <Table />
</div>
