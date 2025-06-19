<script>
    import NotificationModal from "./NotificationModal.svelte";

    let startDate = "";
    let endDate = "";
    let startTime = "";
    let endTime = "";
    let showModal = false;
    let selectedLabels = {
        human: false,
        vehicle: false,
        animal: false,
    };

    const openModal = () => {
        if (!startDate || !endDate) {
            alert("Lütfen başlangıç ve bitiş tarihini seçin.");
            return;
        }
        showModal = true;
    };

    const handleModalClose = () => {
        showModal = false;
    };

    // Filter parametrelerini NotificationModal'a geçirmek için hesaplanan değerler
    $: filterParams = {
        startDate,
        endDate,
        startTime,
        endTime,
        selectedLabels
    };
</script>

<div class="w-full max-w-full">
    <div class="flex flex-col space-y-2">
        <div class="flex flex-col space-y-2">
            <!-- svelte-ignore a11y-label-has-associated-control -->
            <label class="text-sm font-medium">Başlangıç</label>
            <div class="flex space-x-2">
                <input
                    type="date"
                    bind:value={startDate}
                    class="border p-1.5 rounded flex-1"
                />
                <input
                    type="time"
                    bind:value={startTime}
                    class="border p-1.5 rounded flex-1"
                />
            </div>
        </div>

        <div class="flex flex-col space-y-2">
            <!-- svelte-ignore a11y-label-has-associated-control -->
            <label class="text-sm font-medium">Bitiş</label>
            <div class="flex space-x-2">
                <input
                    type="date"
                    bind:value={endDate}
                    class="border p-1.5 rounded flex-1"
                />
                <input
                    type="time"
                    bind:value={endTime}
                    class="border p-1.5 rounded flex-1"
                />
            </div>
            <!-- svelte-ignore a11y-label-has-associated-control -->
            <label class="text-sm font-medium">Filtrele (Etiketler)</label>
            <div class="flex space-x-4">
                <label class="inline-flex items-center">
                    <input
                        type="checkbox"
                        bind:checked={selectedLabels.human}
                        class="rounded border-gray-300"
                    />
                    <span class="ml-2">İnsan</span>
                </label>
                <label class="inline-flex items-center">
                    <input
                        type="checkbox"
                        bind:checked={selectedLabels.vehicle}
                        class="rounded border-gray-300"
                    />
                    <span class="ml-2">Araç</span>
                </label>
                <label class="inline-flex items-center">
                    <input
                        type="checkbox"
                        bind:checked={selectedLabels.animal}
                        class="rounded border-gray-300"
                    />
                    <span class="ml-2">Hayvan</span>
                </label>
            </div>
        </div>

        <button
            on:click={openModal}
            class="bg-blue-500 hover:bg-blue-700 text-white font-bold py-1.5 px-6 rounded w-full"
        >
            Filtrele
        </button>
    </div>
</div>

{#if showModal}
    <NotificationModal
        {filterParams}
        on:close={handleModalClose}
    />
{/if}