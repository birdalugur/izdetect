<script>
    import Control from "./components/Control.svelte";
    import Notifications from "./components/Notifications.svelte";
    import Statistics from "./components/Statistics.svelte";
    import Messages from "./components/Messages.svelte";
    import LiveCamera from "./components/LiveCamera.svelte";
    import Timeline from "./components/Timeline.svelte";

    let messages = [];

    const addMessage = (message) => {
        messages = [message, ...messages].slice(0, 5); // Prepend new message and keep only the last 5
    };
</script>

<main class="flex h-[99vh] bg-gray-100">
    <div class="w-1/5 bg-white p-5 flex flex-col gap-5">
        <Control {addMessage} />
        <!-- <Statistics /> -->
        <Messages {messages} />
        <!-- <Timeline /> -->
    </div>
    <div class="w-2/5 p-2 bg-gray-50">
        <LiveCamera />
    </div>
    <div class="w-2/5 p-5 bg-gray-50 overflow-y-auto flex flex-col gap-2.5">
        <Notifications />
    </div>
</main>