<div align="center">

  <img src="https://capsule-render.vercel.app/api?type=rect&color=11131f&height=130&section=header&text=%F0%9F%8E%99%EF%B8%8F%20MIC%20MUTE%20CONTROLLER&fontSize=35&fontColor=7aa2f7&fontAlignY=55" alt="Microphone Control Banner" width="100%" />

  <br/>

  ![Status](https://img.shields.io/badge/STATUS-COMPLETED-44cc11?style=for-the-badge&logo=github)
  ![Platform](https://img.shields.io/badge/PLATFORM-WINDOWS-0078D6?style=for-the-badge&logo=windows&logoColor=white)
  ![Language](https://img.shields.io/badge/PYTHON-TKINTER%20%2F%20PYCAW-e03131?style=for-the-badge)

</div>

---

## 📝 รายละเอียดโปรเจกต์ (Project Overview)

โปรแกรมควบคุมการเปิด-ปิดไมโครโฟนด้วยคีย์ลัดสำหรับ Windows (**Mic Mute Controller**) พัฒนาขึ้นเพื่อให้ผู้ใช้งานสามารถสั่ง Mute / Unmute ไมโครโฟนระดับฮาร์ดแวร์ได้ทันทีจากทุกหน้าจอแม้ขณะเล่นเกมแบบ Fullscreen มีการออกแบบโครงสร้างโค้ดที่สะอาด กินทรัพยากรเครื่องต่ำมาก (ใช้ RAM เพียง ~15–20 MB) พร้อมระบบตรวจจับไมโครโฟนอัตโนมัติ แถบแจ้งเตือนลอยบนหน้าจอ (Floating OSD) และไอคอนควบคุมใน System Tray อย่างเป็นระบบ ⚡

## 🛠️ เทคโนโลยีที่ใช้ (Tech Stack)

* **Core Language:** Python 3 🐍
* **GUI & High-DPI Rendering:** Tkinter / TTK + Windows Shcore API 🖥️
* **Audio Hardware Control:** Pycaw (Windows Core Audio API) & Comtypes 🎙️
* **Global Hotkey & System Tray:** Keyboard Hook Library & Pystray (Pillow) ⌨️
* **Single Instance & Registry:** Windows Kernel32 Mutex / Event & Winreg 🔒
* **Packaging & Installer:** PyInstaller & Inno Setup Compiler 📦

---

## ✨ ฟีเจอร์หลัก (Key Features)

* **One-Click Keybind:** ตั้งค่าปุ่มคีย์ลัดได้ง่ายเพียงคลิกแล้วกดปุ่มที่ต้องการบนคีย์บอร์ด (กด `Esc` เพื่อยกเลิก) ⌨️
* **Auto-Detect Microphone:** อัปเดตรายชื่อไมโครโฟนอัตโนมัติทันทีเมื่อเสียบใหม่หรือถอดสายออกโดยไม่ต้องรีสตาร์ทโปรแกรม 🔌
* **Floating OSD Overlay:** หน้าต่างแจ้งเตือนโปร่งใสไร้กรอบด้านล่างหน้าจอ เมาส์คลิกทะลุได้ (Click-Through) และไม่แย่งโฟกัสขณะเล่นเกม 🎮
* **System Tray Integration:** แสดงไอคอนสถานะสีเขียว/แดงที่มุมขวาล่าง ชี้ดูชื่อไมค์ได้ คลิกซ้ายเพื่อเปิด-ปิดไมค์ได้ทันที 📌
* **Single Instance Protection:** ป้องกันการเปิดโปรแกรมซ้อน หากกดเปิดซ้ำจะทำการดึงหน้าต่างเดิมที่ซ่อนอยู่ขึ้นมาแสดงผลอัตโนมัติ 🛡️
* **Multi-Language Support:** รองรับการสลับภาษา **ไทย / อังกฤษ** ทันที และสามารถเพิ่มภาษาอื่นเองได้ผ่านไฟล์ `languages.json` 🌐
* **Windows Startup:** เลือกตั้งค่าให้เปิดโปรแกรมอัตโนมัติเมื่อเปิดเครื่อง พร้อมพับเก็บลง System Tray ทันที 🚀

---

## 📥 ดาวน์โหลดและติดตั้ง (Download & Installation)

สำหรับผู้ใช้งานทั่วไป ไม่จำเป็นต้องติดตั้ง Python สามารถดาวน์โหลดตัวติดตั้งไปใช้งานได้ทันที:

1. ไปที่เมนู **[Releases](../../releases)** ด้านขวามือของหน้าเพจนี้
2. ดาวน์โหลดไฟล์ **`Mic_Control_Setup.exe`**
3. ดับเบิลคลิกไฟล์เพื่อติดตั้งลงเครื่อง แล้วเปิดใช้งานได้ทันที 🎉

---

## 💻 สำหรับนักพัฒนา (Development & Build)

หากต้องการรันจากซอร์สโค้ดหรือแก้ไขโปรแกรมเพิ่มเติม สามารถทำตามขั้นตอนดังนี้:

```powershell
# 1. ติดตั้งไลบรารีที่จำเป็น
python -m pip install -r requirements.txt

# 2. รันโปรแกรมจากซอร์สโค้ด
python Mic_Control.py

# 3. สร้างไฟล์ไอคอนและแปลงเป็นไฟล์ .exe เดี่ยว
python make_icon.py
python -m PyInstaller --noconsole --onefile --icon=mic_icon.ico Mic_Control.py
```

---

## 📂 โครงสร้างไฟล์ในโปรเจกต์ (Project Structure)

```text
📦 Mic-Mute-Controller
 ┣ 📜 Mic_Control.py       # ซอร์สโค้ดหลักของโปรแกรม (แบ่งหมวดหมู่ชัดเจน)
 ┣ 📜 make_icon.py         # สคริปต์สร้างไฟล์ไอคอนความละเอียดสูง (mic_icon.ico)
 ┣ 📜 languages.json       # ไฟล์ข้อมูลภาษา (สามารถแก้ไขหรือเพิ่มภาษาใหม่ได้)
 ┣ 📜 installer.iss        # สคริปต์ Inno Setup สำหรับสร้างตัวติดตั้ง .exe
 ┣ 📜 requirements.txt     # รายชื่อไลบรารีที่ใช้ในโปรเจกต์
 ┗ 📜 README.md            # เอกสารอธิบายโปรเจกต์
```
