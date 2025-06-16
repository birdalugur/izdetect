<!-- NotificationModal.svelte -->
<script>
    import { createEventDispatcher } from "svelte";
    import NotificationCard from "./NotificationCard.svelte";

    const dispatch = createEventDispatcher();

    export let notifications = [];
    export let currentPage = 1;
    export let pageSize = 12;
    export let selectedImage = null;
    export let selectedNotificationId = null;

    const closeModal = () => {
        dispatch("close");
    };

    const showImage = (imageUrl, id) => {
        selectedImage = "http://localhost:8000/cameras/output/" + imageUrl;
        selectedNotificationId = id;
        dispatch("imageSelect", { imageUrl: selectedImage, id });
    };

    const closeImage = () => {
        selectedImage = null;
        selectedNotificationId = null;
        dispatch("imageClose");
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

    const nextPage = () => {
        if (notifications.length === pageSize) {
            dispatch("nextPage");
        }
    };

    const previousPage = () => {
        if (currentPage > 1) {
            dispatch("previousPage");
        }
    };

    const deleteCurrentPageNotifications = () => {
        dispatch("deleteCurrentPage");
    };

    const deleteAllNotifications = () => {
        dispatch("deleteAll");
    };

    const handleImageClick = (event) => {
        const { imageUrl, id } = event.detail;
        showImage(imageUrl, id);
    };

    const handleNotificationDelete = (event) => {
        const id = event.detail;
        dispatch("deleteNotification", id);
    };
</script>

<!-- Modal -->
<div class="fixed inset-0 bg-black bg-opacity-70 flex items-center justify-center z-50">
    <div class="bg-white rounded-lg w-11/12 max-w-6xl h-3/4 overflow-auto relative flex flex-col">
        <!-- Navigation Bar -->
        <div class="sticky top-0 bg-gray-100 shadow-sm z-10">
            <div class="flex items-center justify-between py-2 px-3">
                <div class="flex items-center space-x-1 text-sm">
                    <button
                        class="bg-blue-500 hover:bg-blue-700 text-white py-1 px-2 rounded-l flex items-center"
                        on:click={previousPage}
                        disabled={currentPage === 1}
                    >
                        <svg
                            xmlns="http://www.w3.org/2000/svg"
                            class="h-4 w-4"
                            viewBox="0 0 20 20"
                            fill="currentColor"
                        >
                            <path
                                fill-rule="evenodd"
                                d="M12.707 5.293a1 1 0 010 1.414L9.414 10l3.293 3.293a1 1 0 11-1.414 1.414l-4-4a1 1 0 010-1.414l4-4a1 1 0 011.414 0z"
                                clip-rule="evenodd"
                            />
                        </svg>
                        <span class="ml-1">Önceki</span>
                    </button>
                    <span class="bg-gray-200 px-2 py-1 rounded text-xs">
                        Sayfa {currentPage}
                    </span>
                    <button
                        class="bg-blue-500 hover:bg-blue-700 text-white py-1 px-2 rounded-r flex items-center"
                        on:click={nextPage}
                        disabled={notifications.length < pageSize}
                    >
                        <span class="mr-1">Sonraki</span>
                        <svg
                            xmlns="http://www.w3.org/2000/svg"
                            class="h-4 w-4"
                            viewBox="0 0 20 20"
                            fill="currentColor"
                        >
                            <path
                                fill-rule="evenodd"
                                d="M7.293 14.707a1 1 0 010-1.414L10.586 10 7.293 6.707a1 1 0 011.414-1.414l4 4a1 1 0 010 1.414l-4 4a1 1 0 01-1.414 0z"
                                clip-rule="evenodd"
                            />
                        </svg>
                    </button>
                </div>

                <div class="flex space-x-1 text-sm">
                    <button
                        class="bg-red-500 hover:bg-red-700 text-white py-1 px-2 rounded flex items-center"
                        on:click={deleteCurrentPageNotifications}
                    >
                        <svg
                            xmlns="http://www.w3.org/2000/svg"
                            class="h-4 w-4 mr-1"
                            viewBox="0 0 20 20"
                            fill="currentColor"
                        >
                            <path
                                fill-rule="evenodd"
                                d="M9 2a1 1 0 00-.894.553L7.382 4H4a1 1 0 000 2v10a2 2 0 002 2h8a2 2 0 002-2V6a1 1 0 100-2h-3.382l-.724-1.447A1 1 0 0011 2H9zM7 8a1 1 0 012 0v6a1 1 0 11-2 0V8zm5-1a1 1 0 00-1 1v6a1 1 0 102 0V8a1 1 0 00-1-1z"
                                clip-rule="evenodd"
                            />
                        </svg>
                        Sayfayı Sil
                    </button>
                    <button
                        class="bg-red-600 hover:bg-red-800 text-white py-1 px-2 rounded flex items-center"
                        on:click={deleteAllNotifications}
                    >
                        <svg
                            xmlns="http://www.w3.org/2000/svg"
                            class="h-4 w-4 mr-1"
                            viewBox="0 0 20 20"
                            fill="currentColor"
                        >
                            <path
                                fill-rule="evenodd"
                                d="M9 2a1 1 0 00-.894.553L7.382 4H4a1 1 0 000 2v10a2 2 0 002 2h8a2 2 0 002-2V6a1 1 0 100-2h-3.382l-.724-1.447A1 1 0 0011 2H9zM7 8a1 1 0 012 0v6a1 1 0 11-2 0V8zm5-1a1 1 0 00-1 1v6a1 1 0 102 0V8a1 1 0 00-1-1z"
                                clip-rule="evenodd"
                            />
                        </svg>
                        Tümünü Sil
                    </button>
                    <button
                        class="bg-gray-500 hover:bg-gray-700 text-white py-1 px-2 rounded"
                        on:click={closeModal}
                    >
                        <svg
                            xmlns="http://www.w3.org/2000/svg"
                            class="h-5 w-5"
                            fill="none"
                            viewBox="0 0 24 24"
                            stroke="currentColor"
                        >
                            <path
                                stroke-linecap="round"
                                stroke-linejoin="round"
                                stroke-width="2"
                                d="M6 18L18 6M6 6l12 12"
                            />
                        </svg>
                    </button>
                </div>
            </div>
        </div>

        <!-- Content -->
        <div class="p-6 grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4 flex-grow">
            {#each notifications as notification}
                <NotificationCard
                    {notification}
                    on:imageClick={handleImageClick}
                    on:delete={handleNotificationDelete}
                />
            {/each}
        </div>
    </div>
</div>

<!-- Image Viewer -->
{#if selectedImage}
    <div class="fixed top-0 left-0 w-full h-full bg-white flex items-center justify-center z-50">
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