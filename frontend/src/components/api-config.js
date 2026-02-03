// Environment configuration for frontend API
// Tarayıcıda erişilebilir API sunucusunun adresini ayarla

// Eğer LOCAL makine üzerinde çalışıyorsanız - localhost otomatik kullanılır
// Eğer REMOTE makine'den erişiyorsanız - aşağıdaki IP'yi değiştir:

export const API_CONFIG = {
  // 'auto' = tarayıcının hostname'ini kullan (localhost, 127.0.0.1, vb.)
  // 'custom' = aşağıdaki customApiUrl'yi kullan
  mode: 'auto', // veya 'custom'
  
  // Eğer mode: 'custom' ise bu adresi kullan:
  customApiUrl: 'http://10.100.17.72', // değiştir: örn. 'http://192.168.1.100'
  
  // API port'u (genellikle 8000)
  apiPort: 8000
};
