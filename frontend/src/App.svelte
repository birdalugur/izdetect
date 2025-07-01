<script>
    import LeftPanel from "./components/LeftPanel.svelte";
    import Notifications from "./components/Notifications.svelte";
    import MiddlePanel from "./components/MiddlePanel.svelte";

    let messages = [];

    const addMessage = (message) => {
        messages = [message, ...messages].slice(0, 5); // Prepend new message and keep only the last 5
    };
</script>

<main class="flex h-[99vh] bg-white gap-x-4">
    <div class="w-1/5">
        <LeftPanel {addMessage} />
    </div>
    <div class="w-2/5">
        <MiddlePanel />
    </div>
    <div class="w-2/5 p-2 bg-gray-100 overflow-y-auto flex flex-col rounded-lg mb-4">
        <Notifications />
    </div>
</main>

