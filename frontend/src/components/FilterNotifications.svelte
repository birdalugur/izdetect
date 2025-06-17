<!-- FilterNotifications.svelte -->
<script>
    import { createEventDispatcher } from "svelte";
    import NotificationModal from "./NotificationModal.svelte";

    const dispatch = createEventDispatcher();

    export let startDate = "";
    export let endDate = "";
    export let startTime = "";
    export let endTime = "";
    export let autoOpen = false;

    let notifications = [];
    let showModal = false;
    let selectedImage = null;
    let selectedNotificationId = null;
    let currentPage = 1;
    let pageSize = 12;
    let totalNotifications = 0;
    let selectedLabels = {
        human: false,
        vehicle: false,
        animal: false,
    };

    $: if (autoOpen && startDate && endDate) {
        fetchNotificationsByDate(1);
    }

    const fetchNotificationsByDate = async (page = 1) => {
        if (!startDate || !endDate) {
            alert("Lütfen başlangıç ve bitiş tarihini seçin.");
            return;
        }

        const startDateTime = startTime
            ? `${startDate}T${startTime}`
            : startDate;
        const endDateTime = endTime ? `${endDate}T${endTime}` : endDate;

        let labelsParam = "";
        const selectedLabelIds = [];
        if (selectedLabels.human) selectedLabelIds.push(1);
        if (selectedLabels.vehicle) selectedLabelIds.push(2);
        if (selectedLabels.animal) selectedLabelIds.push(3);

        if (selectedLabelIds.length > 0) {
            labelsParam = selectedLabelIds.join(",");
        }

        try {
            const skip = (page - 1) * pageSize;
            const response = await fetch(
                `http://localhost:8000/notifications/by_date?start_date=${startDateTime}&end_date=${endDateTime}&skip=${skip}&limit=${pageSize}&labels=${labelsParam}`,
            );
            if (!response.ok) {
                throw new Error(`HTTP error! status: ${response.status}`);
            }
            const data = await response.json();
            notifications = data;
            totalNotifications = data.length;
            showModal = true;
            currentPage = page;
        } catch (error) {
            console.error("Bildirimler alınamadı:", error);
            alert("Bildirimler alınamadı.");
        }
    };

    const deleteNotification = async (id) => {
        try {
            await fetch(`http://localhost:8000/notifications/${id}`, {
                method: "DELETE",
            });
            notifications = notifications.filter((n) => n._id !== id);
        } catch (error) {
            console.error("Bildirim silinemedi:", error);
            alert("Bildirim silinemedi.");
        }
    };

    const deleteAllNotifications = async () => {
        if (!startDate || !endDate) {
            alert("Lütfen başlangıç ve bitiş tarihini seçin.");
            return;
        }

        try {
            const response = await fetch(
                `http://localhost:8000/notifications/by_date?start_date=${startDate}&end_date=${endDate}`,
                {
                    method: "DELETE",
                },
            );
            if (!response.ok) {
                throw new Error(`HTTP error! status: ${response.status}`);
            }
            const result = await response.json();
            alert(result.message);
            notifications = [];
        } catch (error) {
            console.error("Bildirimler silinemedi:", error);
            alert("Bildirimler silinemedi.");
        }
    };

    const deleteCurrentPageNotifications = async () => {
        if (notifications.length === 0) {
            alert("Silinecek bildirim yok.");
            return;
        }

        const notificationIds = notifications.map((n) => n._id);

        try {
            const response = await fetch(
                `http://localhost:8000/notifications/batch_delete`,
                {
                    method: "DELETE",
                    headers: {
                        "Content-Type": "application/json",
                    },
                    body: JSON.stringify({ notification_ids: notificationIds }),
                },
            );
            if (!response.ok) {
                throw new Error(`HTTP error! status: ${response.status}`);
            }
            const result = await response.json();
            notifications = [];
            alert(result.message);
        } catch (error) {
            console.error("Bildirimler silinemedi:", error);
            alert("Bildirimler silinemedi.");
        }
    };

    const handleModalClose = () => {
        showModal = false;
        dispatch("close");
    };

    const handleNextPage = () => {
        if (notifications.length === pageSize) {
            fetchNotificationsByDate(currentPage + 1);
        }
    };

    const handlePreviousPage = () => {
        if (currentPage > 1) {
            fetchNotificationsByDate(currentPage - 1);
        }
    };

    const handleImageSelect = (event) => {
        const { imageUrl, id } = event.detail;
        selectedImage = imageUrl;
        selectedNotificationId = id;
    };

    const handleImageClose = () => {
        selectedImage = null;
        selectedNotificationId = null;
    };

    const handleDeleteNotification = (event) => {
        const id = event.detail;
        deleteNotification(id);
    };

    const handleDeleteCurrentPage = () => {
        deleteCurrentPageNotifications();
    };

    const handleDeleteAll = () => {
        deleteAllNotifications();
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
            on:click={() => fetchNotificationsByDate(1)}
            class="bg-blue-500 hover:bg-blue-700 text-white font-bold py-1.5 px-6 rounded w-full"
        >
            Filtrele
        </button>
    </div>
</div>

{#if showModal}
    <NotificationModal
        {notifications}
        {currentPage}
        {pageSize}
        {selectedImage}
        {selectedNotificationId}
        on:close={handleModalClose}
        on:nextPage={handleNextPage}
        on:previousPage={handlePreviousPage}
        on:imageSelect={handleImageSelect}
        on:imageClose={handleImageClose}
        on:deleteNotification={handleDeleteNotification}
        on:deleteCurrentPage={handleDeleteCurrentPage}
        on:deleteAll={handleDeleteAll}
    />
{/if}
