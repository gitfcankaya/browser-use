# Amazon.de ASIN Product Scraper 🛍️

Web uygulaması ile Amazon.de'den ASIN numaraları kullanarak ürün bilgilerini otomatik olarak çeker.

## Özellikler

- ✅ Tekli veya çoklu ASIN desteği (virgülle ayrılmış)
- ✅ Yapılandırılmış JSON çıktısı
- ✅ Çıkarılan bilgiler:
  - Ürün başlığı
  - Fiyat
  - Müşteri değerlendirmesi
  - Yorum sayısı
  - Stok durumu
  - Marka
  - Ürün açıklaması
  - Özellikler
  - Ürün görselleri
- ✅ AI destekli akıllı veri çıkarma

## Kurulum

### Gereksinimler

1. Python 3.11 veya üzeri
2. OpenAI API anahtarı
3. Gradio kütüphanesi

### Adımlar

1. Repoyu klonlayın veya dosyaları indirin:
```bash
cd browser-use/examples/apps/amazon-asin-scraper
```

2. Gerekli bağımlılıkları yükleyin:
```bash
uv pip install gradio
```

3. `.env` dosyası oluşturun ve OpenAI API anahtarınızı ekleyin:
```bash
OPENAI_API_KEY=sk-your-api-key-here
```

## Kullanım

### Web Arayüzü ile

1. Uygulamayı başlatın:
```bash
python amazon_scraper.py
```

2. Tarayıcınızda otomatik olarak açılan web arayüzüne gidin (genellikle http://localhost:7860)

3. Formu doldurun:
   - **OpenAI API Key**: API anahtarınızı girin (veya .env dosyasında ayarlayın)
   - **ASIN Number(s)**: Bir veya birden fazla ASIN girin (virgülle ayırın)
   - **Model**: Kullanılacak LLM modelini seçin (varsayılan: gpt-4.1-mini)
   - **Headless Mode**: Tarayıcının arka planda çalışmasını istiyorsanız işaretli bırakın

4. "🔍 Scrape Products" butonuna tıklayın

5. Sonuçlar JSON formatında alt metin kutusunda görüntülenecektir

### Örnek Kullanım

**Tek ASIN:**
```
B08N5WRWNW
```

**Çoklu ASIN (virgülle ayrılmış):**
```
B08N5WRWNW, B09G9FPHY6, B0C1H26C46
```

## Çıktı Formatı

### Tek Ürün İçin

```json
{
  "asin": "B08N5WRWNW",
  "title": "Sony PlayStation 5...",
  "price": "€499.99",
  "rating": "4.5 out of 5 stars",
  "reviews_count": "12,543",
  "availability": "In Stock",
  "brand": "Sony",
  "description": "Experience lightning-fast loading...",
  "features": [
    "Ultra-high speed SSD",
    "Stunning games",
    "4K-TV gaming"
  ],
  "images": [
    "https://m.media-amazon.com/images/I/..."
  ],
  "url": "https://www.amazon.de/dp/B08N5WRWNW"
}
```

### Çoklu Ürün İçin

```json
{
  "products": [
    {
      "asin": "B08N5WRWNW",
      "title": "...",
      ...
    },
    {
      "asin": "B09G9FPHY6",
      "title": "...",
      ...
    }
  ],
  "scraped_at": "2024-01-15T10:30:00"
}
```

## Notlar

- Her ürün için scraping işlemi yaklaşık 30-60 saniye sürebilir
- Amazon.de'nin kullanım koşullarına uygun şekilde kullanın
- API maliyetleri OpenAI'nin fiyatlandırmasına göre değişir
- Çok sayıda ürün için scraping yaparken API rate limitlerini göz önünde bulundurun

## Teknik Detaylar

Bu uygulama şu teknolojileri kullanır:
- **browser-use**: AI destekli tarayıcı otomasyonu
- **Gradio**: Web arayüzü
- **Pydantic**: Veri doğrulama ve serileştirme
- **OpenAI GPT**: Akıllı veri çıkarma

## Sorun Giderme

### "No module named gradio" hatası
```bash
uv pip install gradio
```

### "Please provide an OpenAI API key" hatası
- `.env` dosyasında `OPENAI_API_KEY` değişkenini ayarlayın veya
- Web arayüzünde API anahtarını manuel olarak girin

### Tarayıcı açılmıyor
- Headless modun işaretli olduğundan emin olun, veya
- Grafik arayüzü olan bir sistemde çalıştığınızdan emin olun

## Lisans

Bu proje browser-use projesinin bir parçası olarak MIT lisansı altında sunulmaktadır.
