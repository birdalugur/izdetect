<script>
    import Control from "./Control.svelte";
    import Ram from "./Ram.svelte";
    import Filter from "./Filter.svelte";

    // Props
    export let addMessage;
</script>

<div class="bg-white-100 flex flex-col gap-5 overflow-y-auto rounded-lg">
    <Control {addMessage} />
    <Ram />
    <Filter />
</div>
