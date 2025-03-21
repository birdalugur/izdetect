<script>
    let startDate = "";
    let endDate = "";
    let notifications = [];
    let showModal = false;
    let selectedImage = null;
    let selectedNotificationId = null;
    let currentPage = 1;
    let pageSize = 12;
    let totalNotifications = 0;

    const fetchNotificationsByDate = async (page = 1) => {
        if (!startDate || !endDate) {
            alert("Lütfen başlangiç ve bitiş tarihini seçin.");
            return;
        }

        try {
            const skip = (page - 1) * pageSize;
            const response = await fetch(
                `http://localhost:8000/notifications_by_date?start_date=${startDate}&end_date=${endDate}&skip=${skip}&limit=${pageSize}`,
            );
            if (!response.ok) {
                throw new Error(`HTTP error! status: ${response.status}`);
            }
            const data = await response.json();
            notifications = data;
            totalNotifications = data.length; // Burada toplam bildirim sayısını almak için endpoint'i güncellemeniz gerekebilir.
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

<div class="rounded-lg">
    <div class="flex space-x-4">
        <input
            type="date"
            bind:value={startDate}
            class="border p-1.5 rounded w-48"
        />
        <input
            type="date"
            bind:value={endDate}
            class="border p-1.5 rounded w-48"
        />
        <button
            on:click={() => fetchNotificationsByDate(1)}
            class="bg-blue-500 hover:bg-blue-700 text-white font-bold py-1.5 px-6 rounded"
        >
            Filtrele
        </button>
    </div>
</div>

{#if showModal}
    <div
        class="fixed inset-0 bg-black bg-opacity-70 flex items-center justify-center z-50"
    >
        <div class="bg-white rounded-lg w-3/4 h-3/4 overflow-auto relative">
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
        </div>
    </div>
{/if}

{#if selectedImage}
    <div
        class="fixed top-0 left-0 w-full h-full bg-black bg-opacity-70 flex items-center justify-center z-50"
    >
        <div class="relative bg-white p-4 rounded-lg">
            <button
                class="absolute top-2 right-2 text-gray-600 hover:text-gray-800"
                on:click={closeImage}>Kapat</button
            >
            <button
                class="absolute top-1/2 left-2 transform -translate-y-1/2 text-gray-600 hover:text-gray-800"
                on:click={showPreviousImage}>←</button
            >
            <img
                src={selectedImage}
                alt="Detected frame"
                class="max-w-full max-h-[80vh]"
            />
            <button
                class="absolute top-1/2 right-2 transform -translate-y-1/2 text-gray-600 hover:text-gray-800"
                on:click={showNextImage}>→</button
            >
        </div>
    </div>
{/if}