<script>
    import { writable } from "svelte/store";
    import FilterNotifications from "./FilterNotifications.svelte";

    // Store to hold fetched detection records
    const detectionRecords = writable([]);

    // Pagination variables
    let currentPage = 1;
    let recordsPerPage = 10;
    let totalRecords = 0;
    let totalPages = 0;

    // Function to fetch detection records from the backend with pagination
    const fetchDetectionRecords = async (page = 1, limit = recordsPerPage) => {
        try {
            const skip = (page - 1) * limit;
            const response = await fetch(
                `http://localhost:8000/detection-sessions?skip=${skip}&limit=${limit}`,
            );
            if (!response.ok) {
                throw new Error(`HTTP error! Status: ${response.status}`);
            }
            const data = await response.json();
            detectionRecords.set(data.records);
            totalRecords = data.total;
            totalPages = Math.ceil(totalRecords / limit);
        } catch (error) {
            console.error("Error fetching detection records:", error);
        }
    };

    // Call the fetch function when the component loads
    fetchDetectionRecords(currentPage, recordsPerPage);

    // Variables for FilterNotifications integration
    let showFilterModal = false;
    let filterStartDate = "";
    let filterEndDate = "";
    let filterStartTime = "";
    let filterEndTime = "";

    // Function to format date to YYYY-MM-DD format
    const formatDate = (isoString) => {
        return new Date(isoString).toISOString().split("T")[0];
    };

    // Function to format time to HH:MM format
    const formatTime = (isoString) => {
        const date = new Date(isoString);
        return date.toLocaleTimeString("tr-TR", {
            hour: "2-digit",
            minute: "2-digit",
            second: "2-digit",
            hour12: false,
        });
    };

    // Function to handle opening images for a detection record
    const openImages = (record) => {
        // Set the date and time values from the record
        filterStartDate = formatDate(record.start);
        filterEndDate = formatDate(record.end);
        filterStartTime = formatTime(record.start);
        filterEndTime = formatTime(record.end);

        // Show the FilterNotifications modal
        showFilterModal = true;
    };

    // Function to close the image viewer
    const closeFilterModal = () => {
        showFilterModal = false;
        // Reset values
        filterStartDate = "";
        filterEndDate = "";
        filterStartTime = "";
        filterEndTime = "";
    };

    // Pagination functions
    const goToPage = (page) => {
        if (page >= 1 && page <= totalPages) {
            currentPage = page;
            fetchDetectionRecords(currentPage, recordsPerPage);
        }
    };

    const nextPage = () => {
        if (currentPage < totalPages) {
            goToPage(currentPage + 1);
        }
    };

    const prevPage = () => {
        if (currentPage > 1) {
            goToPage(currentPage - 1);
        }
    };

    // Handle records per page change
    const handleRecordsPerPageChange = (event) => {
        recordsPerPage = parseInt(event.target.value);
        currentPage = 1;
        fetchDetectionRecords(currentPage, recordsPerPage);
    };

    // Generate page numbers for pagination
    $: pageNumbers = (() => {
        const pages = [];
        const maxVisible = 5;
        let start = Math.max(1, currentPage - Math.floor(maxVisible / 2));
        let end = Math.min(totalPages, start + maxVisible - 1);

        if (end - start + 1 < maxVisible) {
            start = Math.max(1, end - maxVisible + 1);
        }

        for (let i = start; i <= end; i++) {
            pages.push(i);
        }
        return pages;
    })();
</script>

<!-- Detection History - Fixed positioned container -->
<div
    class="fixed-detection-history bg-gray-100 p-4 rounded-lg shadow-lg mx-auto mt-4 max-w-4xl"
>
    <h2 class="text-xl font-bold text-gray-800 mb-3">Detection History</h2>

    <!-- Records per page selector -->
    <div class="mb-3 flex justify-between items-center">
        <div class="flex items-center gap-2">
            <label for="recordsPerPage" class="text-sm text-gray-600"
                >Records per page:</label
            >
            <select
                id="recordsPerPage"
                bind:value={recordsPerPage}
                on:change={handleRecordsPerPageChange}
                class="px-3 py-1 border border-gray-300 rounded-md text-sm"
            >
                <option value={4}>4</option>
                <option value={10}>10</option>
                <option value={20}>20</option>
                <option value={50}>50</option>
            </select>
        </div>
        <div class="text-sm text-gray-600">
            Total: {totalRecords} records
        </div>
    </div>

    <!-- Fixed height table container with constrained height -->
    <div
        class="table-container overflow-hidden border border-gray-300 rounded-md"
    >
        <div class="overflow-x-auto overflow-y-auto table-scroll">
            <table class="w-full table-auto border-collapse bg-white">
                <thead class="sticky top-0 bg-gray-200 z-1">
                    <tr>
                        <th class="px-4 py-2 text-left text-gray-600 border-b"
                            >Camera ID</th
                        >
                        <th class="px-4 py-2 text-left text-gray-600 border-b"
                            >Start Time</th
                        >
                        <th class="px-4 py-2 text-left text-gray-600 border-b"
                            >End Time</th
                        >
                        <th class="px-4 py-2 text-left text-gray-600 border-b"
                            >Action</th
                        >
                    </tr>
                </thead>
                <tbody>
                    {#each $detectionRecords as record}
                        <tr class="border-b hover:bg-gray-50">
                            <td class="px-4 py-2">{record.camera_id}</td>
                            <td class="px-4 py-2">
                                {new Date(record.start).toLocaleString()}
                            </td>
                            <td class="px-4 py-2">
                                {record.end
                                    ? new Date(record.end).toLocaleString()
                                    : "Ongoing"}
                            </td>
                            <td class="px-4 py-2">
                                <button
                                    on:click={() => openImages(record)}
                                    disabled={!record.start || !record.end}
                                    class="py-1 px-3 rounded-lg text-white font-semibold transition
                                    {record.start && record.end
                                        ? 'bg-blue-500 hover:bg-blue-600'
                                        : 'bg-gray-400 cursor-not-allowed'}"
                                >
                                    Open
                                </button>
                            </td>
                        </tr>
                    {/each}

                    <!-- Empty state if no records -->
                    {#if $detectionRecords.length === 0}
                        <tr>
                            <td
                                colspan="4"
                                class="px-4 py-8 text-center text-gray-500"
                            >
                                No detection records found
                            </td>
                        </tr>
                    {/if}
                </tbody>
            </table>
        </div>
    </div>

    <!-- Pagination controls -->
    {#if totalPages > 1}
        <div class="mt-3 flex justify-between items-center">
            <div class="text-sm text-gray-600">
                Showing {(currentPage - 1) * recordsPerPage + 1} to {Math.min(
                    currentPage * recordsPerPage,
                    totalRecords,
                )} of {totalRecords} entries
            </div>

            <div class="flex items-center gap-2">
                <!-- Previous button -->
                <button
                    on:click={prevPage}
                    disabled={currentPage === 1}
                    class="px-3 py-1 rounded-md text-sm font-medium transition
                    {currentPage === 1
                        ? 'bg-gray-200 text-gray-400 cursor-not-allowed'
                        : 'bg-white text-gray-700 hover:bg-gray-100 border border-gray-300'}"
                >
                    Previous
                </button>

                <!-- Page numbers -->
                {#each pageNumbers as pageNum}
                    <button
                        on:click={() => goToPage(pageNum)}
                        class="px-3 py-1 rounded-md text-sm font-medium transition
                        {currentPage === pageNum
                            ? 'bg-blue-500 text-white'
                            : 'bg-white text-gray-700 hover:bg-gray-100 border border-gray-300'}"
                    >
                        {pageNum}
                    </button>
                {/each}

                <!-- Next button -->
                <button
                    on:click={nextPage}
                    disabled={currentPage === totalPages}
                    class="px-3 py-1 rounded-md text-sm font-medium transition
                    {currentPage === totalPages
                        ? 'bg-gray-200 text-gray-400 cursor-not-allowed'
                        : 'bg-white text-gray-700 hover:bg-gray-100 border border-gray-300'}"
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

<style>
    /* Fixed positioning for Detection History */
    .fixed-detection-history {
        position: relative;
        max-height: 70vh; /* Limit to 70% of viewport height */
        display: flex;
        flex-direction: column;
    }

    /* Table container with constrained height */
    .table-container {
        flex: 1;
        min-height: 200px;
        max-height: calc(
            70vh - 200px
        ); /* Subtract space for header, controls, pagination */
    }

    .table-scroll {
        height: 100%;
        max-height: 300px; /* Maximum table content height */
    }

    /* Ensure the component doesn't exceed the reference component's position */
    @media (max-height: 800px) {
        .fixed-detection-history {
            max-height: 60vh;
        }

        .table-container {
            max-height: calc(60vh - 180px);
        }

        .table-scroll {
            max-height: 250px;
        }
    }

    @media (max-height: 600px) {
        .fixed-detection-history {
            max-height: 50vh;
        }

        .table-container {
            max-height: calc(50vh - 160px);
        }

        .table-scroll {
            max-height: 200px;
        }
    }

    /* Modal styles */
    .modal-overlay {
        position: fixed;
        top: 0;
        left: 0;
        width: 100vw;
        height: 100vh;
        background: rgba(0, 0, 0, 0.5);
        display: flex;
        justify-content: center;
        align-items: center;
        z-index: 100;
    }

    .modal-content {
        background: white;
        padding: 20px;
        border-radius: 8px;
        width: 500px;
        max-width: 90%;
        box-shadow: 0px 4px 6px rgba(0, 0, 0, 0.1);
    }

    /* Prevent table from growing beyond limits */
    .table-container table {
        min-width: 100%;
    }

    /* Better responsive behavior */
    @media (max-width: 768px) {
        .fixed-detection-history {
            margin: 1rem;
            max-width: calc(100% - 2rem);
        }
    }
</style>
