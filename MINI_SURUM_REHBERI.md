# EGS Scrapper Mini Surum Rehberi

Bu rehber, yeni surum cikarirken her seferinde ayni sirayi izlemek icin hazirlandi.
Teknik ayrinti bilmeden de takip edebilirsin.

## 1. Degisiklikleri Topla

Yeni surumden once kendine sunu sor:

- Bu surumde ne degisti?
- Hangi hata duzeldi?
- Yeni bir ozellik geldi mi?

Kural:
- Her degisiklik surum notlarina yazilacak.
- Yeni bir ozellik geldiyse yardim metni de guncellenecek.

## 2. Yeni Surum Numarasi Ver

Her yeni paket yeni bir surum olmalidir.

Ornek:
- `v1.8.32` sonrasi `v1.8.33`

Bu islem programin icinde kayit altina alinir.

## 3. Yedek Al

Yeni surumden once mutlaka yedek olmalidir.

Bu projede yedekler genelde su klasorde tutulur:

```text
backups\
```

El kuralin:
- Once yedek
- Sonra surum

## 4. Surum Notunu Yaz

Surum notu, bu surumde ne oldugunu kisa ve net anlatir.

Ornek:
- Ortak sozluk kaldirildi
- Her kanal kendi sozlugunu kullanmaya basladi
- Guncelleme paketi sistemi eklendi

Kisa yazmak yeterlidir. Onemli olan unutulmamasidir.

## 5. Yardimi Guncelle

Eger kullanicinin gorecegi yeni bir davranis geldiyse yardim da guncellenir.

Ornek:
- yeni menu
- yeni tus kisayolu
- yeni guncelleme adimi
- yeni sozluk mantigi

Sadece kod degisti ama kullaniciya gorunen bir sey degismediyse her zaman gerekmez.

## 6. Paketi Hazirla

Sirayla:

1. `build_exe.bat` calistir
2. `prepare_release.bat` calistir

Sonuc:
- tam paket olusur
- guncelleme paketi olusur

## 7. Hangisini Gonderecegini Sec

Yeni kurulum yapacak kisiye:
- tam paket

Program zaten kurulu olan kisiye:
- guncelleme paketi

Genel kural:
- mevcut kullaniciya tam klasor gonderme
- mumkunse update paketi gonder

## 8. Kullaniciya Ne Soylenecek

Kullaniciya su basit adimlar yeter:

1. Zip dosyasini ayri bir klasore ac
2. `apply_update.bat` dosyasini calistir
3. Mevcut EGS Scrapper klasorunu sec
4. Program once yedek alir
5. Sonra yeni dosyalari kurar

## 9. Neler Korunur

Update sirasinda sunlar korunmalidir:

- ayarlar
- veritabanlari
- kanal kurallari
- kanal sozlukleri
- loglar
- hata raporlari

Yani kullanicinin calismasi silinmemelidir.

## 10. En Kisa Kontrol Listesi

Her surumde bu 8 soruya bak:

1. Degisiklik yapildi mi?
2. Surum numarasi verildi mi?
3. Yedek alindi mi?
4. Surum notu yazildi mi?
5. Yardim gerekiyorsa guncellendi mi?
6. `build_exe.bat` calisti mi?
7. `prepare_release.bat` calisti mi?
8. Dogru paket kullaniciya gonderildi mi?

Bu sorulara cevap `evet` ise surum hazirdir.

## 11. En Pratik Kural

Kafan karisinca sadece sunu hatirla:

1. Degisikligi yaptir
2. Surumu kaydet
3. Yedek al
4. Paketi hazirla
5. Kullanicya update gonder

Bu rehber, yeni surumlerde tekrar tekrar ayni guvenli sirayi izlemek icin tutulur.
