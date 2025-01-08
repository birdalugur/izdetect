<script>
    import VideoUpload from "./components/VideoUpload.svelte";
    import Notifications from "./components/Notifications.svelte";
    import Statistics from "./components/Statistics.svelte";
    import Messages from "./components/Messages.svelte";
    import LiveCamera from "./components/LiveCamera.svelte";
    import RealTime from "./components/RealTime.svelte";

    let messages = [];

    const addMessage = (message) => {
        messages = [message, ...messages].slice(0, 5); // Prepend new message and keep only the last 5
    };
</script>

<main>
    <div class="left-panel">
        <VideoUpload {addMessage} />
        <!-- <Statistics /> -->
        <Messages {messages} />
    </div>
    <div class="center-panel">
        <LiveCamera />
        <RealTime />       
    </div>
    <div class="right-panel">
        <Notifications />
    </div>
</main>

<style>
    main {
        display: flex;
        height: 99vh;
        background-color: #f0f0f0;
    }

    .left-panel {
        width: 20%;
        background-color: #ffffff;
        padding: 20px;
        display: flex;
        flex-direction: column;
        gap: 20px; /* Add space between VideoUpload and Statistics */
    }

    .center-panel {
        width: 40%;
        padding: 10px;
        background-color: #f9f9f9;
        /* display: flex; */
        /* align-items: center; */
        /* justify-content: center; */
        /* overflow-y: auto;
        position: relative; For absolute positioning of message box */
    }
    .right-panel {
        width: 40%;
        padding: 20px;
        background-color: #f9f9f9;
        overflow-y: auto;
        display: flex;
        flex-direction: column;
        gap: 10px;
    }
    /* .video-feed {
        width: 100%;

        height: 100%;

        background-color: #cccccc;

        display: flex;

        align-items: center;

        justify-content: center;

        border-radius: 8px;

        box-shadow: 0 2px 4px rgba(0, 0, 0, 0.1);
    } */
</style>
