<script>
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
            await fetch(`http://localhost:8000/notifications/clear-all`, {
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

    function setupEventSource() {
        const eventSource = new EventSource("http://localhost:8000/events");

        eventSource.onmessage = (event) => {
            try {
                const data = JSON.parse(event.data);
                console.log("veri tipi", typeof data);
                notifications = [data, ...notifications];
            } catch (e) {
                console.error("Hata: Gelen veri JSON formatında değil!", e);
            }
        };

        eventSource.onerror = (err) => {
            console.error("SSE bağlantı hatası!", err);
            eventSource.close();
            setTimeout(setupEventSource, 3000); // 3 saniye sonra yeniden bağlan
        };
    }

    setupEventSource();
</script>

<div class="head">
    <form
        class="mt-0 mx-auto max-w-xl py-0 px-2 rounded-full bg-gray-50 border flex focus-within:border-gray-300"
    >
        <input
            type="text"
            placeholder="Filter by label"
            class="bg-transparent w-full focus:outline-none pr-4 font-semibold border-0 focus:ring-0 px-0 py-0"
            name="topic"
        /><button
            class="flex flex-row items-center justify-center min-w-[130px] px-4 rounded-full font-medium tracking-wide border disabled:cursor-not-allowed disabled:opacity-50 transition ease-in-out duration-150 text-base bg-black text-white font-medium tracking-wide border-transparent py-1.5 h-[38px] -mr-3"
        >
            Search
        </button>
    </form>

    <button
        class="clear-all-btn"
        on:click={removeAllNotifications}
        title="Clear All Notifications"
    >
        <!-- Çöp kutusu simgesi SVG, kırmızı renkte ve dolgusuz olarak -->
        <svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 448 512"
            ><!--!Font Awesome Free 6.7.2 by @fontawesome - https://fontawesome.com License - https://fontawesome.com/license/free Copyright 2025 Fonticons, Inc.--><path
                d="M432 32H312l-9.4-18.7A24 24 0 0 0 281.1 0H166.8a23.7 23.7 0 0 0 -21.4 13.3L136 32H16A16 16 0 0 0 0 48v32a16 16 0 0 0 16 16h416a16 16 0 0 0 16-16V48a16 16 0 0 0 -16-16zM53.2 467a48 48 0 0 0 47.9 45h245.8a48 48 0 0 0 47.9-45L416 128H32z"
            /></svg
        >
    </button>
</div>

<div class="notifications-container">
    <div class="notification-list">
        {#each notifications as notification}
            <!-- svelte-ignore a11y-click-events-have-key-events -->
            <!-- svelte-ignore a11y-no-static-element-interactions -->
            <div
                class="notification-box"
                on:click={() =>
                    showImage(notification.image_url, notification._id)}
            >
                <div class="notification-details">
                    {#each notification.labels as label}
                        {#each Object.entries(label) as [key, value]}
                            <div class="detail">
                                <span class="detail-key">{key}</span>:
                                <span class="detail-value">{value}</span>
                            </div>
                        {/each}
                    {/each}
                </div>
                <img
                    src={"http://localhost:8000/output/" +
                        notification.image_url}
                    alt="Thumbnail"
                    class="thumbnail"
                />
                <p class="time">{notification.time.split(".")[0]}</p>
            </div>
        {/each}
    </div>

    {#if selectedImage}
        <div class="image-viewer">
            <!-- svelte-ignore a11y-click-events-have-key-events -->
            <div class="overlay" on:click={closeImage}></div>
            <button class="nav-btn left" on:click={showPreviousImage}>←</button>
            <img src={selectedImage} alt="Detected frame" />
            <button class="nav-btn right" on:click={showNextImage}>→</button>
            <button on:click={closeImage}>Close</button>
            <button on:click={() => removeNotification(selectedNotificationId)}>
                Remove Notification
            </button>
        </div>
    {/if}
</div>

<style>
    .nav-btn {
        position: absolute;
        top: 50%;
        transform: translateY(-50%);
        background: rgba(255, 255, 255, 0.6);
        border: none;
        font-size: 24px;
        cursor: pointer;
        padding: 10px;
        border-radius: 50%;
    }

    .nav-btn:hover {
        background: rgba(255, 255, 255, 0.8);
    }

    .nav-btn.left {
        left: 10px;
    }

    .nav-btn.right {
        right: 10px;
    }

    .head {
        display: flex;
        justify-content: space-between;
        align-items: center;
        /*border: 1px solid black;*/
        border-radius: 5px;
        padding: 5px;
        height: 50px; /* Yüksekliği sabitleyin */
    }

    .clear-all-btn {
        background: none;
        border: none;
        color: red;
        cursor: pointer;
        padding: 4px;
        width: 24px;
        height: 24px;
        display: flex;
        align-items: center;
        justify-content: center;
    }

    .clear-all-btn:hover {
        color: darkred;
    }

    .notifications-container {
        margin-top: 5px;
        text-align: center;
        max-height: 100%; /* Maksimum yükseklik belirleyin */
        overflow-y: auto; /* Bildirimlerin kaydırılabilir olmasını sağlar */
    }

    .notification-list {
        display: grid;
        grid-template-columns: repeat(auto-fill, minmax(200px, 1fr));
        gap: 10px;
    }

    .notification-box {
        background: #f5f5f5;
        border-radius: 8px;
        padding: 10px;
        box-shadow: 0 2px 4px rgba(0, 0, 0, 0.1);
        transition: transform 0.2s;
        cursor: pointer;
    }

    .notification-box:hover {
        transform: scale(1.05);
    }

    .thumbnail {
        width: 100%;
        border-radius: 4px;
    }

    .image-viewer img {
        max-width: 100%;
    }

    .image-viewer button {
        margin: 10px;
        padding: 8px 16px;
        background: #f5f5f5;
        border: none;
        border-radius: 4px;
        cursor: pointer;
        transition: background 0.2s;
    }

    .image-viewer {
        position: fixed;
        top: 50%;
        left: 50%;
        transform: translate(-50%, -50%) scale(0.8);
        background: rgba(0, 0, 0, 0.8);
        padding: 20px;
        border-radius: 8px;
        text-align: center;
        opacity: 0;
        animation: fadeInScale 0.3s ease-out forwards;
        z-index: 1000;
    }

    @keyframes fadeInScale {
        0% {
            opacity: 0;
            transform: translate(-50%, -50%) scale(0.8);
        }
        100% {
            opacity: 1;
            transform: translate(-50%, -50%) scale(1);
        }
    }

    .image-viewer button:hover {
        background: #ccc;
    }
    .notification-details {
        display: flex;
        justify-content: space-between;
        margin: 10px 0;
        font-size: 14px;
        font-weight: bold;
    }

    .detail {
        display: flex;
        gap: 4px;
        align-items: center;
        padding: 4px;
        background: #eef4fb;
        border: 1px solid #d1e2f5;
        border-radius: 4px;
    }

    .detail-key {
        color: #2b6cb0;
    }

    .detail-value {
        color: #1a202c;
        font-weight: normal;
    }

    .time {
        margin-top: 10px;
        color: #718096;
        font-size: 12px;
    }
</style>
