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
    <h3>Notifications</h3>
    <button
        class="clear-all-btn"
        on:click={removeAllNotifications}
        title="Clear All Notifications"
    >
        <!-- Çöp kutusu simgesi SVG, kırmızı renkte ve dolgusuz olarak -->
        <svg
            xmlns="http://www.w3.org/2000/svg"
            width="16"
            height="16"
            fill="none"
            stroke="red"
            stroke-width="1.5"
            class="bi bi-trash"
            viewBox="0 0 16 16"
        >
            <path
                d="M5.5 5.5a.5.5 0 0 1 .5-.5H10a.5.5 0 0 1 .5.5v8a.5.5 0 0 1-.5.5H6a.5.5 0 0 1-.5-.5v-8z"
            />
            <path
                d="M11 4a1 1 0 0 1 1 1v8a1 1 0 0 1-1 1H6a1 1 0 0 1-1-1V5a1 1 0 0 1 1-1h5zm-5.118 0L6 3.118V3.5a.5.5 0 0 1 1 0V3.118L10.118 4H11a1 1 0 0 1 1 1v.5a.5.5 0 0 1-1 0V5H5.118L5 5.5a.5.5 0 0 1-1 0V5c0-.276.112-.5.5-.5z"
            />
        </svg>
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
                <h4>
                    {#each notification.labels as label}
                        {#each Object.entries(label) as [key, value]}
                            <div>{key}: {value}</div>
                        {/each}
                    {/each}
                </h4>
                <img
                    src={"http://localhost:8000/output/" +
                        notification.image_url}
                    alt="Thumbnail"
                    class="thumbnail"
                />
                <p>{notification.time}</p>
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
        background-color: rgb(187, 201, 211);
        border: 1px solid black;
        border-radius: 5px;
        padding: 5px;
        text-align: center;
    }

    h3 {
        margin: 0;
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
</style>
