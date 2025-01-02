<script>
    import { onMount } from "svelte";
    // import io from "socket.io-client";

    let objectStats = {};
    let totalNotifications = 0;

    const fetchStatistics = async () => {
        const response = await fetch("http://localhost:5000/statistics");
        const data = await response.json();
        objectStats = data.object_stats;
        totalNotifications = data.total_notifications;
    };

    onMount(() => {
        fetchStatistics();
    });

    // const socket = io("http://localhost:5000");
    // socket.on("notification", () => {
    //     fetchStatistics();
    // });

    // socket.on("connect", () => {
    //     console.log("Connected to server for statistics");
    // });

    // socket.on("notification", (data) => {
    //     // Bildirimde gelen objelerin sayısını güncelle
    //     data.labels.forEach((label) => {
    //         const [name, count] = label.split(": ");
    //         objectStats[name] = (objectStats[name] || 0) + parseInt(count);
    //     });
    //     totalNotifications += 1;
    // });

    // socket.on("disconnect", () => {
    //     console.log("Disconnected from server");
    // });
</script>

<div class="statistics-container">
    <h2>Statistics</h2>
    <div class="object-stats">
        <ul>
            {#each Object.entries(objectStats) as [key, value]}
                <li>{key}: {value}</li>
            {/each}
        </ul>
    </div>
    <p>Total Notifications: {totalNotifications}</p>
</div>

<style>
    .statistics-container {
        margin-top: 20px; /* Ensures it stays below the buttons */
        background-color: #f8f9fa;
        padding: 1px;
        border-radius: 8px;
        box-shadow: 0 2px 4px rgba(0, 0, 0, 0.1);
        width: 100%;
        text-align: left;
    }

    p {
        font-size: 14px;
    }

    h2 {
        font-size: 16px;
        margin-bottom: 10px;
    }
</style>
