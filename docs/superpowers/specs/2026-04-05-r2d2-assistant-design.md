# R2D2 Sesli Asistan — Tasarım Dokümanı

**Tarih:** 2026-04-05  
**Platform:** Windows 11  
**Python:** 3.8+

---

## Genel Bakış

Mikrofonu sürekli dinleyen, "Hey R2" tetikleyici kelimesini duyunca R2D2 sesi çalan ve bir dizi eylemi otomatik olarak gerçekleştiren bir masaüstü asistan uygulaması. Windows başlangıcında otomatik başlar, system tray'de yaşar.

### Tetiklenince Gerçekleşen Eylemler

1. R2D2 ses efekti çal
2. YouTube'da "Star Wars Theme" ara
3. Google Gemini'yi aç
4. Claude'u aç
5. VSCode'u başlat

---

## Mimari

Observer pattern tabanlı modüler yapı. `MicrophoneListener` bir event tetikler, `CommandDispatcher` kayıtlı tüm handler'ları bildirir. Her handler bağımsız çalışır — biri hata verse diğerleri etkilenmez.

```
Mikrofon (PyAudio)
      │
      ▼
MicrophoneListener          ← ses kaydeder, "Hey R2" algılar (ayrı thread)
      │  dispatch("hey_r2")
      ▼
CommandDispatcher           ← Observer merkezi, handler kaydı ve bildirim
      │  notify_all_handlers()
      ├──▶ R2D2SoundHandler     → WAV dosyası oynatır (pygame.mixer)
      ├──▶ BrowserHandler       → YouTube + Gemini + Claude açar
      └──▶ VSCodeHandler        → `code` komutunu PATH'ten çalıştırır

main.py
  ├── Handler'ları dispatcher'a kaydeder
  ├── MicrophoneListener'ı başlatır
  ├── Windows startup kaydı yapar (winreg, ilk çalışmada)
  └── pystray ile system tray ikonunu başlatır
```

---

## Modüller

### `config.py`
Tüm ayarların tek yeri. Kullanıcı buradan konfigürasyon yapar.

```python
TRIGGER_PHRASE = "hey r2"          # case-insensitive karşılaştırılır
BROWSER = None                      # None = varsayılan, "chrome"/"firefox"/"edge"
SOUND_DIR = "sounds/"
STARTUP_ENABLED = True
URLS = {
    "youtube": "https://www.youtube.com/results?search_query=Star+Wars+Theme",
    "gemini":  "https://gemini.google.com",
    "claude":  "https://claude.ai"
}
FREESOUND_SEARCH_URL = "https://freesound.org/apiv2/search/text/"
```

### `command_dispatcher.py`
Observer pattern implementasyonu.

```python
class CommandDispatcher:
    def register(self, event: str, handler: Callable) -> None
    def dispatch(self, event: str) -> None  # her handler try/except ile çağrılır
```

- Handler hataları loglanır, diğer handler'ların çalışması engellenmez
- `threading.Thread` ile handler'lar paralel çalıştırılabilir (opsiyonel)

### `microphone_listener.py`
- `speech_recognition.Recognizer` + Google STT (ücretsiz, API key gerektirmez)
- `adjust_for_ambient_noise()` ile ortam gürültüsüne otomatik adaptasyon
- Ayrı `threading.Thread`'de çalışır, ana thread'i bloklamaz
- "Hey R2" algılandığında `dispatcher.dispatch("hey_r2")` çağırır
- Internet yoksa veya STT başarısız olursa hata loglanır, dinleme devam eder

### `r2d2_sounds.py`
İki katmanlı ses stratejisi:

**Katman 1 — CC0 Lisanslı İndirme:**
- `sounds/` klasöründe WAV yoksa bilinen bir CC0 lisanslı R2D2-tarzı ses URL'inden doğrudan indirir (API key gerektirmez)
- Kaynak URL `config.py`'da tanımlı, değiştirilebilir
- İndirme tek seferlik, önbeleklenir
- Oynatma: `pygame.mixer.Sound`

**Katman 2 — Sentetik Yedek:**
- İndirme başarısız olursa `numpy` + `scipy.io.wavfile` ile sentetik R2D2 chirp sesi üretir
- Frekans modülasyonlu kısa bip dizisi (R2D2 karakteristik sesi)
- `sounds/r2d2_synth.wav` olarak kaydedilir

### `browser_controller.py`
- `config.URLS` içindeki URL'leri sırayla açar
- `webbrowser.get(config.BROWSER)` — `BROWSER=None` ise sistem varsayılanı kullanılır
- Her URL açma arasında kısa gecikme (browser sekmeler arası yarış durumunu önler)

### `vscode_launcher.py`
- `subprocess.run(["code", "."])` ile PATH'ten `code` komutunu çalıştırır
- `FileNotFoundError` yakalanır, kullanıcıya açıklayıcı log mesajı gösterilir
- VSCode bulunamazsa diğer eylemler etkilenmez

### `tray_app.py`
- `pystray.Icon` ile system tray ikonu (`assets/r2d2_icon.png`)
- Sağ tık menüsü:
  - **Durum:** "Dinleniyor..." / "Duraklatıldı"
  - **Duraklat / Devam Et**
  - **Çıkış**
- Duraklatma: `MicrophoneListener.pause()` / `.resume()` çağırır

### `startup_manager.py`
- Windows Registry `HKEY_CURRENT_USER\Software\Microsoft\Windows\CurrentVersion\Run` anahtarına kayıt
- `winreg` modülü (Python standart kütüphane, ek bağımlılık yok)
- `config.STARTUP_ENABLED = False` yapılırsa kaydı siler
- İlk çalıştırmada otomatik olarak `main.py` tarafından çağrılır

### `main.py`
Uygulama giriş noktası:
1. Logging konfigürasyonu (`logs/r2d2.log`)
2. `pygame.mixer` başlatma
3. `CommandDispatcher` oluşturma
4. Handler'ları kaydetme (`R2D2SoundHandler`, `BrowserHandler`, `VSCodeHandler`)
5. `MicrophoneListener` başlatma (thread)
6. `startup_manager.register()` çağırma
7. `tray_app.run()` (bloklayan, ana thread)

---

## Dosya Yapısı

```
r2d2_assistant/
├── main.py
├── config.py
├── command_dispatcher.py
├── microphone_listener.py
├── r2d2_sounds.py
├── browser_controller.py
├── vscode_launcher.py
├── tray_app.py
├── startup_manager.py
├── sounds/
│   └── .gitkeep
├── assets/
│   └── r2d2_icon.png
├── logs/
│   └── .gitkeep
├── requirements.txt
└── README.md
```

---

## Bağımlılıklar (`requirements.txt`)

```
SpeechRecognition==3.10.0
pyaudio==0.2.14
pygame==2.5.2
pystray==0.19.5
Pillow==10.3.0
numpy==1.26.4
scipy==1.13.0
requests==2.31.0
```

**Kurulum notu:** Windows'ta `pyaudio` için önce `pipwin install pyaudio` veya pre-built wheel kullanılmalıdır. README'de adım adım açıklanacak.

---

## Hata Yönetimi

| Durum | Davranış |
|---|---|
| Mikrofon bulunamadı | Hata loglanır, tray'de "Mikrofon yok" uyarısı |
| İnternet yok (STT) | Hata loglanır, dinleme devam eder |
| Ses indirme başarısız | Sentetik ses üretimine geçilir |
| VSCode PATH'te yok | Hata loglanır, diğer eylemler çalışır |
| Browser açılamadı | Her URL için ayrı try/except, hata loglanır |

---

## Kapsam Dışı

- macOS / Linux desteği (şu an sadece Windows)
- Birden fazla tetikleyici kelime
- Sesli yanıt (TTS) — R2D2 sesi yeterli
- GUI ayar paneli
