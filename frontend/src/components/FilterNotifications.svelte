<script>
    let startDate = "";
    let endDate = "";
    let startTime = "";
    let endTime = "";
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

    const fetchNotificationsByDate = async (page = 1) => {
        if (!startDate || !endDate) {
            alert("Lütfen başlangiç ve bitiş tarihini seçin.");
            return;
        }

        const startDateTime = startTime
            ? `${startDate}T${startTime}`
            : startDate;
        const endDateTime = endTime ? `${endDate}T${endTime}` : endDate;

        // Seçili label'ları API için hazırla
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
                `http://localhost:8000/notifications_by_date?start_date=${startDateTime}&end_date=${endDateTime}&skip=${skip}&limit=${pageSize}&labels=${labelsParam}`,
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
            console.error("Bildirimler alinamadi:", error);
            alert("Bildirimler alinamadi.");
        }
    };

    const showImage = (imageUrl, id) => {
        selectedImage = "http://localhost:8000/output/" + imageUrl;
        selectedNotificationId = id;
    };

    const closeImage = () => {
        selectedImage = null;
        selectedNotificationId = null;
    };

    const showNextImage = () => {
        const currentIndex = notifications.findIndex(
            (notification) => notification._id === selectedNotificationId,
        );
        if (currentIndex >= 0 && currentIndex < notifications.length - 1) {
            const nextNotification = notifications[currentIndex + 1];
            showImage(nextNotification.image_url, nextNotification._id);
        }
    };

    const showPreviousImage = () => {
        const currentIndex = notifications.findIndex(
            (notification) => notification._id === selectedNotificationId,
        );
        if (currentIndex > 0) {
            const previousNotification = notifications[currentIndex - 1];
            showImage(previousNotification.image_url, previousNotification._id);
        }
    };

    const deleteNotification = async (id) => {
        try {
            await fetch(`http://localhost:8000/delete_notification/${id}`, {
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
            alert("Lütfen başlangiç ve bitiş tarihini seçin.");
            return;
        }

        try {
            const response = await fetch(
                `http://localhost:8000/delete_notifications_by_date?start_date=${startDate}&end_date=${endDate}`,
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
        try {
            for (const notification of notifications) {
                await fetch(
                    `http://localhost:8000/delete_notification/${notification._id}`,
                    {
                        method: "DELETE",
                    },
                );
            }
            notifications = [];
            alert("Sayfadaki bildirimler silindi.");
        } catch (error) {
            console.error("Bildirimler silinemedi:", error);
            alert("Bildirimler silinemedi.");
        }
    };

    const nextPage = () => {
        if (notifications.length === pageSize) {
            fetchNotificationsByDate(currentPage + 1);
        }
    };

    const previousPage = () => {
        if (currentPage > 1) {
            fetchNotificationsByDate(currentPage - 1);
        }
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
    <div
        class="fixed inset-0 bg-black bg-opacity-70 flex items-center justify-center z-50"
    >
        <div
            class="bg-white rounded-lg w-11/12 max-w-6xl h-3/4 overflow-auto relative"
        >
            <!-- Navbar -->
            <div
                class="p-6 grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4"
            >
                <div
                    class="fixed top-10 right-10 px-4 py-2 flex justify-between items-center z-10"
                >
                    <button
                        class="bg-red-500 hover:bg-red-700 text-white px-4 pb-2 rounded"
                        on:click={() => (showModal = false)}
                    >
                        <span class="text-2xl">&times;</span>
                    </button>
                </div>

                {#each notifications as notification}
                    <!-- svelte-ignore a11y-click-events-have-key-events -->
                    <div class="border p-4 rounded-lg cursor-pointer">
                        <img
                            src={"http://localhost:8000/output/" +
                                notification.image_url}
                            alt="Thumbnail"
                            class="w-full rounded-md mb-2 cursor-pointer"
                            on:click={() =>
                                showImage(
                                    notification.image_url,
                                    notification._id,
                                )}
                        />
                        <div class="flex flex-wrap gap-2">
                            {#each notification.labels as label}
                                {#each Object.entries(label) as [key, value]}
                                    <span
                                        class="bg-gray-200 px-2 py-1 rounded-full text-sm"
                                    >
                                        {key}: {value}
                                    </span>
                                {/each}
                            {/each}
                        </div>
                        <p class="text-sm text-gray-600 mt-2">
                            {notification.time.split(".")[0]}
                        </p>
                        <button
                            class="mt-2 bg-red-500 hover:bg-red-700 text-white px-3 py-1 rounded"
                            on:click={(event) => {
                                event.stopPropagation();
                                deleteNotification(notification._id);
                            }}
                        >
                            Sil
                        </button>
                    </div>
                {/each}
            </div>
            <!-- Pagination Controls -->
            <div class="flex justify-center mt-4">
                <button
                    class="bg-blue-500 hover:bg-blue-700 text-white font-bold py-2 px-4 rounded-l"
                    on:click={previousPage}
                    disabled={currentPage === 1}
                >
                    Önceki
                </button>
                <span class="bg-gray-200 px-4 py-2">
                    Sayfa {currentPage}
                </span>
                <button
                    class="bg-blue-500 hover:bg-blue-700 text-white font-bold py-2 px-4 rounded-r"
                    on:click={nextPage}
                    disabled={notifications.length < pageSize}
                >
                    Sonraki
                </button>
            </div>
            <!-- Delete Buttons -->
            <div class="flex justify-center mt-4 space-x-4">
                <button
                    class="bg-red-500 hover:bg-red-700 text-white font-bold py-2 px-4 rounded"
                    on:click={deleteAllNotifications}
                >
                    Tümünü Sil
                </button>
                <button
                    class="bg-red-500 hover:bg-red-700 text-white font-bold py-2 px-4 rounded"
                    on:click={deleteCurrentPageNotifications}
                >
                    Sayfayı Sil
                </button>
            </div>
        </div>
    </div>
{/if}

{#if selectedImage}
    <div
        class="fixed top-0 left-0 w-full h-full bg-white flex items-center justify-center z-50"
    >
        <!-- Kapat butonu sağ üst köşeye taşındı -->
        <button
            class="absolute top-4 right-4 z-50 bg-gray-200 hover:bg-gray-300 rounded-full w-10 h-10 flex items-center justify-center text-gray-700 hover:text-gray-900"
            on:click={closeImage}
        >
            <span class="text-xl">&times;</span>
        </button>

        <button
            class="absolute left-0 w-16 h-full bg-white hover:bg-gray-100 active:bg-gray-200 border-0 transition-all flex-shrink-0 text-2xl"
            on:click={showPreviousImage}
        >
            ←
        </button>

        <div class="relative bg-white p-4 rounded-lg">
            <img
                src={selectedImage}
                alt="Detected frame"
                class="max-w-full max-h-[80vh]"
            />
        </div>

        <button
            class="absolute right-0 w-16 h-full bg-white hover:bg-gray-100 active:bg-gray-200 border-0 transition-all flex-shrink-0 text-2xl"
            on:click={showNextImage}
        >
            →
        </button>
    </div>
{/if}
