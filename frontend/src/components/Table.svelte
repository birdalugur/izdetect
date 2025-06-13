<script>
    import { writable } from "svelte/store";
    import { onMount } from "svelte";
    import FilterNotifications from "./FilterNotifications.svelte";

    /* ---------- Durum ---------- */
    const detectionRecords = writable([]);
    let currentPage = 1;
    const recordsPerPage = 4;
    let totalRecords = 0;

    /* ---------- Türetilen değerler ---------- */
    $: totalPages  = Math.ceil(totalRecords / recordsPerPage);
    $: pageNumbers = (() => {
        if (!totalPages) return [];
        const max = 5;
        let start = Math.max(1, currentPage - Math.floor(max / 2));
        let end   = Math.min(totalPages, start + max - 1);
        if (end - start + 1 < max) start = Math.max(1, end - max + 1);
        return Array.from({ length: end - start + 1 }, (_, i) => start + i);
    })();

    /* ---------- Veri çekme ---------- */
    const fetchDetectionRecords = async () => {
        const skip = (currentPage - 1) * recordsPerPage;
        try {
            const r = await fetch(`http://localhost:8000/detection-sessions?skip=${skip}&limit=${recordsPerPage}`);
            if (!r.ok) throw new Error(r.status);
            const d = await r.json();
            detectionRecords.set(d.records);
            totalRecords = d.total;
        } catch (err) {
            console.error("Fetch error:", err);
        }
    };

    onMount(fetchDetectionRecords);
    $: currentPage, fetchDetectionRecords();   // Sayfa değişince yeniden çek

    /* ---------- Yardımcılar ---------- */
    const fmt = (iso, type = "date") => {
        const d = new Date(iso);
        return type === "date"
            ? d.toISOString().split("T")[0]
            : d.toLocaleTimeString("tr-TR", { hour: "2-digit", minute: "2-digit", second: "2-digit", hour12: false });
    };

    /* ---------- Modal kontrolü ---------- */
    let showFilterModal = false;
    let filterStartDate = "", filterEndDate = "", filterStartTime = "", filterEndTime = "";

    const openImages = r => {
        filterStartDate = fmt(r.start, "date");
        filterEndDate   = fmt(r.end,   "date");
        filterStartTime = fmt(r.start, "time");
        filterEndTime   = fmt(r.end,   "time");
        showFilterModal = true;
    };
    const closeFilterModal = () => (showFilterModal = false);

    /* ---------- Sayfalama ---------- */
    const goToPage = p => p >= 1 && p <= totalPages && (currentPage = p);
    const nextPage = () => goToPage(currentPage + 1);
    const prevPage = () => goToPage(currentPage - 1);
</script>

<div class="relative max-h-[70vh] flex flex-col bg-gray-100 p-4 rounded-lg shadow-lg mt-4 w-full">
    <h2 class="text-xl font-bold text-gray-800 mb-3">Detection History</h2>

    <div class="mb-3 flex justify-end items-center text-sm text-gray-600">
        Total: {totalRecords} records
    </div>

    <!-- Tablo -->
    <div class="flex-1 min-h-[200px] max-h-[calc(70vh-200px)] overflow-hidden border border-gray-300 rounded-md">
        <div class="overflow-x-auto overflow-y-auto h-full max-h-[300px]">
            <table class="w-full min-w-full table-auto border-collapse bg-white">
                <thead class="sticky top-0 bg-gray-200 z-1">
                    <tr>
                        <th class="px-4 py-2 text-left text-gray-600 border-b">Camera ID</th>
                        <th class="px-4 py-2 text-left text-gray-600 border-b">Start Time</th>
                        <th class="px-4 py-2 text-left text-gray-600 border-b">End Time</th>
                        <th class="px-4 py-2 text-left text-gray-600 border-b">Action</th>
                    </tr>
                </thead>
                <tbody>
                    {#each $detectionRecords as rec}
                        <tr class="border-b hover:bg-gray-50">
                            <td class="px-4 py-2">{rec.camera_id}</td>
                            <td class="px-4 py-2">{new Date(rec.start).toLocaleString('tr-TR')}</td>
                            <td class="px-4 py-2">
                                {rec.end ? new Date(rec.end).toLocaleString('tr-TR') : "Ongoing"}
                            </td>
                            <td class="px-4 py-2">
                                <button
                                    on:click={() => openImages(rec)}
                                    disabled={!rec.start || !rec.end}
                                    class={`py-1 px-3 rounded-lg text-white font-semibold transition ${
                                        rec.start && rec.end
                                            ? 'bg-blue-500 hover:bg-blue-600'
                                            : 'bg-gray-400 cursor-not-allowed'
                                    }`}
                                >
                                    Open
                                </button>
                            </td>
                        </tr>
                    {/each}

                    {#if $detectionRecords.length === 0}
                        <tr>
                            <td colspan="4" class="px-4 py-8 text-center text-gray-500">
                                No detection records found
                            </td>
                        </tr>
                    {/if}
                </tbody>
            </table>
        </div>
    </div>

    <!-- Sayfalama -->
    {#if totalPages > 1}
        <div class="mt-3 flex justify-between items-center flex-wrap gap-2">
            <div class="text-sm text-gray-600">
                Showing {(currentPage - 1) * recordsPerPage + 1}
                to {Math.min(currentPage * recordsPerPage, totalRecords)}
                of {totalRecords} entries
            </div>

            <div class="flex items-center flex-wrap gap-2">
                <button
                    on:click={prevPage}
                    disabled={currentPage === 1}
                    class={`px-3 py-1 rounded-md text-sm font-medium transition ${
                        currentPage === 1
                            ? 'bg-gray-200 text-gray-400 cursor-not-allowed'
                            : 'bg-white text-gray-700 hover:bg-gray-100 border border-gray-300'
                    }`}
                >
                    Previous
                </button>

                {#each pageNumbers as n}
                    <button
                        on:click={() => goToPage(n)}
                        class={`px-3 py-1 rounded-md text-sm font-medium transition ${
                            currentPage === n
                                ? 'bg-blue-500 text-white'
                                : 'bg-white text-gray-700 hover:bg-gray-100 border border-gray-300'
                        }`}
                    >
                        {n}
                    </button>
                {/each}

                <button
                    on:click={nextPage}
                    disabled={currentPage === totalPages}
                    class={`px-3 py-1 rounded-md text-sm font-medium transition ${
                        currentPage === totalPages
                            ? 'bg-gray-200 text-gray-400 cursor-not-allowed'
                            : 'bg-white text-gray-700 hover:bg-gray-100 border border-gray-300'
                    }`}
                >
                    Next
                </button>
            </div>
        </div>
    {/if}
</div>

{#if showFilterModal}
    <FilterNotifications
        bind:startDate={filterStartDate}
        bind:endDate={filterEndDate}
        bind:startTime={filterStartTime}
        bind:endTime={filterEndTime}
        autoOpen={true}
        on:close={closeFilterModal}
    />
{/if}
