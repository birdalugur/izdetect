<script>
    let numbers = []; // Gelen sayıları saklamak için bir liste

    function setupEventSource() {
        const eventSource = new EventSource("http://localhost:8000/events");

        eventSource.onmessage = (event) => {
            try {
                const data = JSON.parse(event.data);
                numbers = [...numbers, data.number];
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
    <h1>Rastgele Sayılar</h1>
    <ul>
        {#each numbers as number}
            <li>{number}</li>
        {/each}
    </ul>
</main>
