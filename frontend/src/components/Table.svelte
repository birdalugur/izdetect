<!-- Table.svelte -->
<script>
    import { writable } from "svelte/store";
    import FilterNotifications from "./FilterNotifications.svelte";

    // Store to hold fetched detection records
    const detectionRecords = writable([]);

    // Function to fetch detection records from the backend
    const fetchDetectionRecords = async () => {
        try {
            const response = await fetch(
                "http://localhost:8000/detection-sessions",
            );
            if (!response.ok) {
                throw new Error(`HTTP error! Status: ${response.status}`);
            }
            const data = await response.json();
            detectionRecords.set(data);
        } catch (error) {
            console.error("Error fetching detection records:", error);
        }
    };

    // Call the fetch function when the component loads
    fetchDetectionRecords();

    // Variables for FilterNotifications integration
    let showFilterModal = false;
    let filterStartDate = "";
    let filterEndDate = "";
    let filterStartTime = "";
    let filterEndTime = "";

    // Function to format date to YYYY-MM-DD format
    const formatDate = (isoString) => {
        return new Date(isoString).toISOString().split('T')[0];
    };

    // Function to format time to HH:MM format
    const formatTime = (isoString) => {
        return new Date(isoString).toISOString().split('T')[1].slice(0, 5);
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
</script>

<div class="bg-gray-100 p-4 rounded-lg shadow-lg mx-auto mt-4 max-w-4xl">
    <h2 class="text-xl font-bold text-gray-800 mb-4">Detection History</h2>
    <div class="overflow-x-auto">
        <table class="w-full table-auto border-collapse">
            <thead>
                <tr class="bg-gray-200">
                    <th class="px-4 py-2 text-left text-gray-600">Camera ID</th>
                    <th class="px-4 py-2 text-left text-gray-600">Start Time</th>
                    <th class="px-4 py-2 text-left text-gray-600">End Time</th>
                    <th class="px-4 py-2 text-left text-gray-600">Action</th>
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
            </tbody>
        </table>
    </div>
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
</style>
