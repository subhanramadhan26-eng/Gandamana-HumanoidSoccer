# ⚽ Humanoid Soccer Robot - Software Architecture (Gandamana Team)

![Project Status](https://img.shields.io/badge/Status-Completed%20%7C%20KRI%20Wilayah%202-orange?style=for-the-badge)
![Achievement](https://img.shields.io/badge/KRI%20Wilayah%202-3rd%20Place%20%7C%20Juara%203-bronze?style=for-the-badge)
![Role](https://img.shields.io/badge/Role-Software%20Engineer-blue?style=for-the-badge)

Repository ini berisi arsitektur perangkat lunak utama untuk Robot Sepak Bola Humanoid tim **Gandamana**. Pengembangan fokus pada tiga subsistem kritikal: sistem lokalisasi fisik (*Odometry*), jaringan komunikasi taktis antar agen (*Inter-Robot Communication*), dan sistem integrasi wasit otomatis (*GameController*).

---

## 🛠️ Arsitektur Sub-Sistem

Sistem perangkat lunak robot dibagi menjadi 3 modul utama yang saling terintegrasi untuk mendukung autonomi penuh di lapangan pertandingan:

```mermaid
graph TD
    %% GameController Section
    Jury[GameController Juri / Referee Box] -->|WiFi - UDP Broadcast| A[Modul GameController Robot]
    A -->|State Update: Start/Stop/Foul| B[State Machine / Strategy Brain]

    %% Odometry Section
    Servo[Data Aktual 12 Servo Kaki] -->|Forward Kinematics| C[Modul Odometry Lokalisasi]
    IMU[Sensor IMU - Yaw] --> C
    C -->|Koordinat X, Y, theta| B
    C -->|Telemetry Data| GUI[Custom Field GUI Visualizer]

    %% Inter-Robot Comm Section
    B -->|Taktik Serang/Bertahan| D[Modul Komunikasi Antar Robot]
    D --- E[Jaringan UDP Socket]
    E --- Robot_Lain[Robot Teman di Lapangan]

    style A fill:#6bf,stroke:#333,stroke-width:2px
    style C fill:#f96,stroke:#333,stroke-width:2px
    style D fill:#9f9,stroke:#333,stroke-width:2px
