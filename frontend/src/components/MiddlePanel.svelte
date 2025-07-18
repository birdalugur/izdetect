<script>
    import LiveCamera from "./LiveCamera.svelte";
    import Table from "./Table.svelte";
    
    export let leftOpen = true;
</script>

<div class="pt-1 flex flex-col gap-11 h-full overflow-y-auto pb-1 transition-all duration-300">
    <LiveCamera />
    {#if leftOpen}
        <Table />
    {/if}
</div>
