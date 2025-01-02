<script>
    export let messages = [];
</script>

<div class="message-box">
    <h3>Messages</h3>
    <ul>
        {#each messages as message}
            <li>{message}</li>
        {/each}
    </ul>
</div>

<style>
    .message-box {
        /* position: absolute; */
        top: 10px;
        left: 10px;
        background-color: #f8f9fa;
        padding: 1px;
        border-radius: 8px;
        box-shadow: 0 2px 4px rgba(0, 0, 0, 0.1);
        width: 100%;
        max-height: 155px;  /* Set a maximum height */
        overflow-y: auto;  /* Enable scrolling when content exceeds height */
    }

    .message-box h3 {
        margin-top: 0;
        margin-bottom: 10px;
        font-size: 16px;
        font-weight: bold;
    }

    .message-box ul {
        list-style: none;
        padding: 0;
        margin: 0;
    }

    .message-box li {
        font-size: 14px;
        margin-bottom: 5px;
        color: #333;
    }
</style>
