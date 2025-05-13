# 🎮💡 Micro:bit Interactive Projects

This repository contains two embedded systems projects developed on the BBC Micro:bit platform:

- **Interactive Gaming using MicroPython**
- **LED Matrix Light Show using ARM Assembly**

Both projects demonstrate creative hardware interaction and efficient embedded programming techniques.

---

## 📘 Table of Contents

- [Project 1: Micro:bit Gaming (MicroPython)](#project-1-microbit-gaming-micropython)
  - [Overview](#overview)
  - [Games Implemented](#games-implemented)
  - [Challenges Faced](#challenges-faced)
  - [Future Improvements](#future-improvements)
- [Project 2: LED Matrix Light Show (ARM Assembly)](#project-2-led-matrix-light-show-arm-assembly)
  - [Objective](#objective)
  - [Implementation Details](#implementation-details)
  - [Challenges Solved](#challenges-solved)
  - [Future Enhancements](#future-enhancements)
- [Team Members](#team-members)

---

## Project 1: Micro:bit Gaming (MicroPython)

### 🎯 Overview

We created three interactive games that utilize the Micro:bit’s built-in sensors, buttons, LED matrix, and radio. These games were developed in **MicroPython**, while the LED controller was implemented in **ARM Assembly** for performance.

### 🕹️ Games Implemented

#### 1. Dino Game (Single Player)

- Inspired by the Chrome Dino game.
- **Controls**:  
  - Button A → Jump  
  - Button B → Crouch  
  - Clap (Microphone) → Jump
- **Obstacles**: Random birds and ground blocks.
- **Scoring**: Increases with time and survival.

#### 2. Battleship (Two Player)

- Wireless gameplay using Micro:bit radio.
- **Controls**:
  - Buttons A/B → Navigate
  - Shake → Fire
- **Gameplay**:
  - Turn-based guessing
  - Ship placement and confirmation
  - LED feedback for hit/miss

#### 3. Hunter-Enemy Tag Game (Two Player)

- Real-time grid-based chase game.
- **Role Selection**:  
  - Button A → Hunter  
  - Button B → Enemy
- **Controls**:
  - Button A → Left  
  - Button B → Right  
  - A+B → Down  
  - Tilt → Up
- Game ends after 60 seconds.

### ⚠️ Challenges Faced

- Radio communication reliability
- Limited memory and inputs
- Responsive real-time interaction
- Balancing features with simplicity

### 🚀 Future Improvements

- Game menu selector
- 3+ player multiplayer support
- Bluetooth-based remote control
- Sound effects using GPIO
- Persistent high scores

---

## Project 2: LED Matrix Light Show (ARM Assembly)

### 🎯 Objective

Create an LED animation system using **pure ARM Assembly**, bypassing MicroPython to directly control hardware and understand low-level embedded development.

### 🛠️ Implementation Details

#### 🔌 Hardware Controlled

- 5×5 LED Matrix
- Buttons A & B
- nRF51822 Microcontroller

#### 🔁 Display Mechanism

- Multiplexing LED control
- GPIO row-column scanning

#### 🔄 Animations Implemented

1. **Triangle Animation** – Dynamic triangular effect
2. **Closing Animation** – Collapse toward center
3. **Pattern Selector** (3 modes):
   - Full Matrix
   - Four Corner Squares
   - Two Left Squares

#### 🧠 Button Handling

- Button A → Switch modes
- Button B → Cycle patterns
- Debounce logic & state tracking

### ⚠️ Challenges Solved

- Flicker-free animation via calibrated delays
- GPIO complexity using datasheets
- No debugger — used LED feedback for debugging
- Button bouncing handled with delay + state logic

### 🌟 Future Enhancements

#### Short-Term

- Add motion-sensitive patterns using accelerometer
- Sound effects via edge connector
- PWM-based brightness control

#### Long-Term

- Wireless Bluetooth control via phone
- Power-efficient scanning
- Store patterns in non-volatile memory
- Build simple LED-based interactive games

---

## 👥 Team Members

- **P Jaya Raghunandhan Reddy** - BT2024029  
- **Pasham Godha** - BT2024082  
- **Varanasi Harshith Raj** - BT2024177  
- **Hasini Samudrala** - BT2024113  
- **Polareddy Harshavardhan Reddy** - BT202406  
- **Gangavarapu Jaswant** - BT2024010

---

## 📎 Project Files

- [`Micro_bit Gaming Project Report.pdf`](./Micro_bit%20Gaming%20Project%20Report.pdf)
- [`Micro_bit LED Matrix Light Show Project Report.pdf`](./Micro_bit%20LED%20Matrix%20Light%20Show%20Project%20Report.pdf)
