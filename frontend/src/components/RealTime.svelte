<script>
    let notifications = []; // Gelen sayıları saklamak için bir liste

    function setupEventSource() {
        const eventSource = new EventSource("http://localhost:8000/events");

        eventSource.onmessage = (event) => {
            try { 
                console.log("Gelen veri: ", typeof(event));               
                const data = JSON.parse(event.data);
                
                console.log(data);
                notifications = [...notifications, data];
            } catch (e) {
                console.error("Hata: Gelen veri JSON formatında değil!", e);
            }
        };

        eventSource.onerror = (err) => {
            console.error("SSE bağlantı hatası!", err);
            // Bağlantı başarısız olursa yeniden bağlanmayı deneyin
            eventSource.close();
            setTimeout(setupEventSource, 3000); // 3 saniye sonra yeniden bağlan
        };
    }

    // İlk bağlantıyı başlat
    setupEventSource();
</script>

<main>
    <h1>Bildirimler</h1>
    <ul>
        {#each notifications as notify}
            <li>"url": {notify.image_url}, "time": {notify.time}</li>
        {/each}
    </ul>
</main>
