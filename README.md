# Discord CC Creator Bot (Render Uyumlu)

Bu bot, `cc_creator.py` kodunun Discord botu haline getirilmiş versiyonudur. Render üzerinde 7/24 çalışacak şekilde optimize edilmiştir.

## Özellikler
- **!gen <visa/master> <adet>**: Belirtilen tipte ve sayıda kart üretir.
- **Web Sunucusu**: Render'ın botu uyutmaması için `8080` portunda bir web sunucusu çalıştırır.
- **Async Yapı**: Bot komutları işlerken donmaz, BIN sorgularını arka planda yapar.

## Kurulum (Render)

1. Bu dosyaları bir GitHub deposuna yükleyin.
2. [Render](https://render.com/) üzerinde yeni bir **Web Service** oluşturun.
3. GitHub deponuzu bağlayın.
4. **Environment Variables** kısmına şunları ekleyin:
   - `DISCORD_TOKEN`: Discord Developer Portal'dan aldığınız bot tokenı.
   - `PYTHON_VERSION`: `3.11.0`
5. Render botu otomatik olarak kuracak ve başlatacaktır.

## Uyanık Tutma (Ping)
Botun uyumaması için Render tarafından verilen URL'yi (örn: `https://bot-adiniz.onrender.com`) bir "Ping" servisine (örn: [Cron-job.org](https://cron-job.org/) veya [UptimeRobot](https://uptimerobot.com/)) ekleyin. Bu servis her 5-10 dakikada bir sitenize girerek botun aktif kalmasını sağlayacaktır.

Bot sitesine girildiğinde sadece "Bot aktif" yazar, bu ping işlemi için yeterlidir.
