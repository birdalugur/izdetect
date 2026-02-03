<script>
    import LiveCamera from "./LiveCamera.svelte";
    import Table from "./Table.svelte";
    
    export let leftOpen = true;
    export let addMessage = () => {};
</script>

<div class="flex flex-col gap-5 flex-1 min-h-0 overflow-y-auto transition-all duration-300">
    <LiveCamera {addMessage} />
    <Table />
</div>
