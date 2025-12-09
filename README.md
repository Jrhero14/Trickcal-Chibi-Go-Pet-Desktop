<div align="center">

  <img src="src/logo/main-logo.png" alt="Trickcal Chibi Go Logo" width="400"/>
  
  # Trickcal Chibi Go! Desktop Pet
  
  **Aplikasi Desktop penurun IQ, Cuayo!! CUAYOOOO!!!**
  
  [![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
  ![Python](https://img.shields.io/badge/Python-3.8%2B-blue)
  ![PyQt5](https://img.shields.io/badge/GUI-PyQt5-green)

  <p>
    <a href="#-fitur-utama">Fitur</a> •
    <a href="#-karakter">Karakter</a> •
    <a href="#-cara-install">Install</a> •
    <a href="#-interaksi--kontrol">Interaksi</a> •
    <a href="#-kredit">Kredit</a>
  </p>
</div>

---

## ✨ Tentang Project

**Trickcal Chibi Go Desktop** adalah aplikasi *desktop pet* berbasis Python yang menghidupkan karakter dari game *Trickcal Chibi Go* langsung di layar komputermu.

---

## 🌟 Fitur Utama

* **🧸 Fisika & Interaksi:** Seret, lempar, dan jatuhkan karakter sesuka hati. Mereka akan memantul dan bereaksi!
* **🏀 Mainan Interaktif:** Sertakan **Pumpkin Ball** untuk mereka mainkan. Mereka bisa menendang dan mengejar bola tersebut.
* **⚔️ Steal Skill (Rebutan):** Jika ada lebih dari satu karakter, mereka bisa saling berebut mainan.
* **🔊 Suara & Voice Line:** Dilengkapi dengan efek suara lucu, dan tantrum.
* **⚙️ Kustomisasi Penuh:** Atur jumlah karakter, ukuran (scale), dan suara melalui menu Setup yang mudah digunakan.
* **🍲 The Soup "Nightmare":** Mode rahasia untuk membuat Speaki panik (lihat bagian Interaksi).

---

## 🎭 Karakter

| Karakter | Kepribadian & Perilaku                                                                                                                                                                                                                     |
| :---: |:-------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------|
| <img src="src/characters/erpin/Erpin-Cherrful.png" width="80"/> | **Erpin (The Fairy Queen)**<br>• Suka berjalan santai.<br>• **Hobi:** Tidur tiba-tiba di layar (Idle animation).<br>• Bisa "dipunch" dan bakal tantrum.<br>• Suka mengobrol dengan sesama Erpin.                                           |
| <img src="src/characters/speaki/Speaki-Cherrful.png" width="80"/> | **Speaki (The Priestess)**<br>• Sangat energik dan suka melompat.<br>• Suka mencuri/memegang bola labu.<br>• **Kelemahan:** SANGAT TAKUT dengan Sup Labu (Pumpkin Soup).<br>• Akan menangis dan "tantrum" jika dijatuhkan dari ketinggian. |

---

## 📥 Cara Install

Pastikan kamu sudah menginstall **Python 3.x**.

1.  **Clone Repository ini:**
    ```bash
    git clone [https://github.com/JrHero14/Trickcal-Chibi-Go-Pet-Desktop.git](https://github.com/JrHero14/Trickcal-Chibi-Go-Pet-Desktop.git)
    cd Trickcal-Chibi-Go-Pet-Desktop
    ```

2.  **Install Dependencies:**
    Disarankan menggunakan virtual environment (`venv`).
    ```bash
    pip install -r requirements.txt
    ```

3.  **Jalankan Aplikasi:**
    ```bash
    python src/main.py
    ```

---

## 🎮 Interaksi & Kontrol

### 🖱️ Kontrol Dasar
* **Klik Kiri & Tahan:** Mengangkat (Drag) karakter atau mainan.
* **Lepas Klik:** Melempar karakter (hati-hati, mereka bisa memantul!).
* **Klik Kanan (pada Karakter/Mainan):** Membuka menu konteks untuk keluar (Exit).

### 🎃 Interaksi Spesial: The Pumpkin Soup
Ini adalah fitur unik untuk **Speaki**:
1.  Pastikan opsi **Pumpkin Ball** aktif di menu awal.
2.  **Klik Kanan** pada Bola Labu (Pumpkin) yang ada di layar.
3.  Pilih **"Change to Soup"**.
4.  😱 **Perhatikan Reaksi Speaki:** Speaki akan lari ketakutan, melompat panik, dan berusaha menjauh sejauh mungkin dari mangkuk sup itu!

### 💤 Interaksi Erpin
* Jika kamu membiarkan Erpin terlalu lama, dia mungkin akan **tertidur** (Zzz...).
* Jika ada 2 Erpin, mereka kadang akan saling mendekat untuk **mengobrol**.

---

## 🛠️ Konfigurasi (Setup)

Saat pertama kali dijalankan (atau jika mode silent tidak aktif), window pengaturan akan muncul:

* **Jumlah:** Tentukan berapa banyak Erpin atau Speaki yang ingin dimunculkan.
* **Pumpkin Ball:** Munculkan mainan bola.
* **Steal Skill:** Izinkan mereka saling rebutan bola.
* **Size Scale:** Atur ukuran pet (0.5x sampai 1.2x).
* **Run on Startup:** Jalankan otomatis saat PC nyala.

---

## 📜 Kredit

* **Developer:** [Jeremi Herodian](https://github.com/JrHero14)
* **Library:** PyQt5, Pillow

> *Project ini dibuat untuk tujuan pembelajaran dan hobi (Fan-made). Semua aset karakter adalah hak cipta dari pemilik aslinya.*

---
