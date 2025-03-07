<script>
    import FilterNotifications from "./FilterNotifications.svelte";

    let notifications = [];
    let selectedImage = null;
    let selectedNotificationId = null;

    const fetchNotifications = async () => {
        const response = await fetch("http://localhost:8000/notifications");
        const data = await response.json();
        notifications = data;
    };

    fetchNotifications();

    const removeNotification = async (id) => {
        await fetch(`http://localhost:8000/notifications/${id}/close`, {
            method: "POST",
        });
        notifications = notifications.filter(
            (notification) => notification._id !== id,
        );
        if (id === selectedNotificationId) {
            closeImage();
        }
    };

    const removeAllNotifications = async () => {
        const userConfirmed = window.confirm(
            "Tüm bildirimleri silmek istediğinizden emin misiniz?",
        );
        if (userConfirmed) {
            await fetch("http://localhost:8000/notifications/clear-all", {
                method: "POST",
            });
            notifications = [];
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

    // const notificationSound = new Audio("/sounds/notification.mp3");
    function setupEventSource() {
        const eventSource = new EventSource("http://localhost:8000/events");

        eventSource.onmessage = (event) => {
            try {
                const data = JSON.parse(event.data);
                console.log("veri tipi", typeof data);
                notifications = [data, ...notifications];

                // notificationSound.play();
            } catch (e) {
                console.error("Hata: Gelen veri JSON formatında değil!", e);
            }
        };

        eventSource.onerror = (err) => {
            console.error("SSE bağlantı hatası!", err);
            eventSource.close();
            setTimeout(setupEventSource, 3000);
        };
    }

    setupEventSource();
</script>
<style>
    .image1 {
        padding: 100px 0;
        
    }
</style>


<div class="flex justify-between items-center p-1.5 border rounded-md">
    <FilterNotifications />
    <button
        class="text-red-600 hover:text-red-800"
        on:click={removeAllNotifications}
        title="Clear All Notifications"
    >
        <svg
            xmlns="http://www.w3.org/2000/svg"
            viewBox="0 0 448 512"
            class="w-6 h-6"
        >
            <path
                d="M432 32H312l-9.4-18.7A24 24 0 0 0 281.1 0H166.8a23.7 23.7 0 0 0 -21.4 13.3L136 32H16A16 16 0 0 0 0 48v32a16 16 0 0 0 16 16h416a16 16 0 0 0 16-16V48a16 16 0 0 0 -16-16zM53.2 467a48 48 0 0 0 47.9 45h245.8a48 48 0 0 0 47.9-45L416 128H32z"
            />
        </svg>
    </button>
</div>

<div class="mt-2 text-center overflow-y-auto">
    <div class="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
        {#each notifications as notification}
            <!-- svelte-ignore a11y-click-events-have-key-events -->
            <div
                class="bg-gray-100 p-4 rounded-md shadow hover:scale-105 transition cursor-pointer"
                on:click={() =>
                    showImage(notification.image_url, notification._id)}
            >
                <div class="flex flex-wrap gap-2">
                    {#each notification.labels as label}
                        {#each Object.entries(label) as [key, value]}
                            <div
                                class="bg-blue-100 border border-blue-300 rounded-md px-2 py-1 text-sm"
                            >
                                <span class="text-blue-600 font-semibold"
                                    >{key}</span
                                >: {value}
                            </div>
                        {/each}
                    {/each}
                </div>
                <img
                    src={"http://localhost:8000/output/" +
                        notification.image_url}
                    alt="Thumbnail"
                    class="w-full rounded-md mt-2"
                />
                <p class="text-gray-500 text-xs mt-2">
                    {notification.time.split(".")[0]}
                </p>
            </div>
        {/each}
    </div>
</div>

{#if selectedImage}
    <div class="fixed inset-0 flex items-center justify-center bg-white z-50">
        <button
            class="absolute left-0 w-16 h-full bg-white hover:bg-gray-100 active:bg-gray-200 border-0 transition-all flex-shrink-0"
            on:click={showPreviousImage}
        >
            <span
                class="absolute left-5 top-1/2 transform -translate-y-1/2 text-gray-700 text-2xl"
            >
                ←
            </span>
        </button>
        <img
            class="max-w-full max-h-full image1"
            src={selectedImage}
            alt="Detected frame"
        />
        <button
            class="absolute right-0 w-16 h-full bg-white hover:bg-gray-100 active:bg-gray-200 border-0 transition-all flex-shrink-0"
            on:click={showNextImage}
        >
            <span
                class="absolute right-5 top-1/2 transform -translate-y-1/2 text-gray-700 text-2xl"
            >
                →
            </span>
        </button>
        <div class="absolute bottom-5 flex gap-4">
            <button
                class="bg-gray-200 px-4 py-2 rounded-md"
                on:click={closeImage}
            >
                Close
            </button>
            <button
                class="bg-red-500 text-white px-4 py-2 rounded-md"
                on:click={() => removeNotification(selectedNotificationId)}
            >
                Remove Notification
            </button>
        </div>
    </div>
{/if}
