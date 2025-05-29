<script>
    import { writable } from 'svelte/store';

    // Mock data simulating MongoDB collection
    const detectionRecords = writable([
        {
            _id: '1',
            camera_id: 'cam-2',
            start: '2024-05-29T14:30:00.000Z',
            end: '2024-05-29T14:31:45.000Z'
        },
        {
            _id: '2',
            camera_id: 'cam-2',
            start: '2024-05-29T15:00:00.000Z',
            end: null
        },
        {
            _id: '3',
            camera_id: 'cam-1',
            start: '2024-05-29T16:00:00.000Z',
            end: '2024-05-29T16:02:30.000Z'
        }
    ]);

    // Store to track which record's images are being viewed
    let selectedRecord = writable(null);

    // Function to handle opening images for a detection record
    const openImages = (record) => {
        selectedRecord.set(record);
    };

    // Function to close the image viewer
    const closeImages = () => {
        selectedRecord.set(null);
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
                        <td class="px-4 py-2">{new Date(record.start).toLocaleString()}</td>
                        <td class="px-4 py-2">{record.end ? new Date(record.end).toLocaleString() : 'Ongoing'}</td>
                        <td class="px-4 py-2">
                            <button
                                on:click={() => openImages(record)}
                                disabled={!record.start || !record.end}
                                class="py-1 px-3 rounded-lg text-white font-semibold transition
                                {record.start && record.end ? 'bg-blue-500 hover:bg-blue-600' : 'bg-gray-400 cursor-not-allowed'}"
                            >
                                Open
                            </button>
                        </td>
                    </tr>
                {/each}
            </tbody>
        </table>
    </div>

    {#if $selectedRecord}
        <!-- svelte-ignore a11y-click-events-have-key-events -->
        <div class="modal-overlay" on:click={closeImages}>
            <div class="modal-content" on:click|stopPropagation>
                <h3 class="text-lg font-bold mb-2">Images for { $selectedRecord.camera_id } ({ new Date($selectedRecord.start).toLocaleString() })</h3>
                <p class="text-gray-600 mb-4">Placeholder for detection images (to be implemented with backend integration).</p>
                <button
                    on:click={closeImages}
                    class="py-2 px-4 bg-red-500 hover:bg-red-600 text-white font-semibold rounded-lg"
                >
                    Close
                </button>
            </div>
        </div>
    {/if}
</div>

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