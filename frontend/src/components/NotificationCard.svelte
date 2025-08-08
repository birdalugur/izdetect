<!-- NotificationCard.svelte -->
<script>
    import { createEventDispatcher } from "svelte";
    import { SERVER_IP } from "./store.js";

    const dispatch = createEventDispatcher();

    export let notification;

    const handleImageClick = () => {
        dispatch("imageClick", {
            imageUrl: notification.image_url,
            id: notification._id,
        });
    };

    const handleDelete = (event) => {
        event.stopPropagation();
        dispatch("delete", notification._id);
    };
</script>

<div
    class="border p-4 rounded-lg cursor-pointer shadow hover:shadow-md transition-shadow"
>
    <!-- svelte-ignore a11y-click-events-have-key-events -->
    <img
        src={`${SERVER_IP}:8000/cameras/output/${notification.image_url}`}
        alt="Thumbnail"
        class="w-full h-40 object-cover rounded-md mb-2 cursor-pointer"
        on:click={handleImageClick}
    />
    <div class="flex flex-wrap gap-2">
        {#each notification.labels as label}
            {#each Object.entries(label) as [key, value]}
                <span class="bg-gray-200 px-2 py-1 rounded-full text-sm">
                    {key}: {value}
                </span>
            {/each}
        {/each}
    </div>
    <p class="text-sm text-gray-600 mt-2">
        {notification.time.split(".")[0]}
    </p>
    <button
        class="glass-btn flex items-center gap-2 px-3 py-1 rounded-full shadow border border-white/30 text-red-700 hover:text-white bg-white/30 hover:bg-red-500/80 backdrop-blur-md transition-all duration-200"
        on:click={handleDelete}
    >
        <svg
            xmlns="http://www.w3.org/2000/svg"
            class="h-4 w-4"
            viewBox="0 0 20 20"
            fill="currentColor"
        >
            <path
                fill-rule="evenodd"
                d="M9 2a1 1 0 00-.894.553L7.382 4H4a1 1 0 000 2v10a2 2 0 002 2h8a2 2 0 002-2V6a1 1 0 100-2h-3.382l-.724-1.447A1 1 0 0011 2H9zM7 8a1 1 0 012 0v6a1 1 0 11-2 0V8zm5-1a1 1 0 00-1 1v6a1 1 0 102 0V8a1 1 0 00-1-1z"
                clip-rule="evenodd"
            />
        </svg>
        <span>Sil</span>
    </button>
</div>

<style>
    .glass-btn {
        background: rgba(255, 255, 255, 0.35);
        backdrop-filter: blur(12px) saturate(180%);
        -webkit-backdrop-filter: blur(12px) saturate(180%);
        border-radius: 9999px;
        box-shadow: 0 4px 24px 0 rgba(31, 38, 135, 0.18);
        border: 1.5px solid rgba(255, 255, 255, 0.35);
        transition:
            background 0.2s,
            box-shadow 0.2s,
            color 0.2s;
    }
    .glass-btn:hover {
        background: rgba(239, 68, 68, 0.7);
        color: #fff;
    }
</style>
