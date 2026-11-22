<div align="center">

# 🎯 TTS Studio

**A Python-powered desktop game-show controller for live TTS (Teka-Teki Silang / Teka-Teki Sulit) gameplay.**

![Python](https://img.shields.io/badge/Python-3.10%2B-3776AB?style=for-the-badge&logo=python&logoColor=white)
![PySide6](https://img.shields.io/badge/GUI-PySide6%20(Qt)-41CD52?style=for-the-badge&logo=qt&logoColor=white)
![Platform](https://img.shields.io/badge/Platform-Windows%20%7C%20Linux%20%7C%20macOS-lightgrey?style=for-the-badge)
![Status](https://img.shields.io/badge/Status-Planning%20%2F%20Initial%20Dev-orange?style=for-the-badge)
![Offline](https://img.shields.io/badge/Mode-Offline--First-success?style=for-the-badge)

<p align="center">
  <b>TTS Studio</b> adalah aplikasi desktop untuk mengelola permainan teka-teki dalam format acara live. Aplikasi menyediakan panel operator dan layar panggung terpisah, sehingga seluruh permainan dapat dikendalikan dari satu komputer dengan monitor tambahan, proyektor, atau TV.
</p>

<p align="center">
  Dibangun menggunakan <b>Python</b> dan <b>PySide6</b>, TTS Studio dirancang untuk kebutuhan permainan interaktif, presentasi, komunitas, acara panggung, maupun produksi hiburan kecil.
</p>

</div>

---

## 📑 Table of Contents

- [📖 Overview](#-overview)
- [✨ Features](#-features)
- [🏗️ Architecture](#️-architecture)
- [🛠️ Technology Stack](#️-technology-stack)
- [📂 Project Structure](#-project-structure)
- [💻 Requirements & Installation](#-requirements--installation)
- [🎮 Basic Gameplay Workflow](#-basic-gameplay-workflow)
- [📄 Question Data Format](#-question-data-format)
- [🎛️ Operator Controls](#️-operator-controls)
- [🖥️ Display Management](#️-display-management)
- [⚙️ Game State](#️-game-state)
- [🎨 UI Design Direction](#-ui-design-direction)
- [🛡️ Safety and Reliability](#️-safety-and-reliability)
- [🧪 Testing](#-testing)
- [🗺️ Development Roadmap](#️-development-roadmap)
- [🧭 Development Principles](#-development-principles)
- [📜 License & Status](#-license--status)

---

## 📖 Overview

**TTS Studio** menggabungkan game controller, pengelolaan pertanyaan, scoreboard, dan stage display dalam satu aplikasi desktop. Operator mengendalikan permainan melalui control panel, sementara penonton melihat tampilan permainan yang dirancang untuk layar besar.

### 🧩 Core Concept

| Komponen | Deskripsi |
| :--- | :--- |
| **Operator Console** | Pusat kendali permainan. |
| **Stage Display** | Tampilan publik yang terpisah dari operator. |
| **Game Engine** | Pengelola state dan aturan permainan. |
| **Question Manager** | Pengelola soal, petunjuk, dan jawaban. |
| **Score Engine** | Pengelola skor dan perubahan skor. |
| **Session System** | Pengelola sesi dan progres permainan. |

### 🎯 Goals
- ✅ Menyediakan kontrol permainan yang mudah digunakan saat acara live.
- ✅ Mendukung dua layar dalam satu komputer.
- ✅ Memisahkan operator UI dari stage display.
- ✅ Memungkinkan reveal soal dan jawaban secara bertahap.
- ✅ Mengelola skor secara real-time.
- ✅ Mengurangi kesalahan operator melalui kontrol yang jelas.
- ✅ Menyimpan dan memuat kumpulan soal.
- ✅ Mendukung penggunaan offline.
- ✅ Memungkinkan pengembangan fitur tambahan tanpa merombak core engine.

---

## ✨ Features

### 🚀 Version 1 — Core Game System

<table>
  <tr>
    <td valign="top" width="50%">
      <h4>🎮 Game Control</h4>
      <ul>
        <li>Start game</li>
        <li>Pause game</li>
        <li>Resume game</li>
        <li>Reset game</li>
        <li>Next question</li>
        <li>Previous question</li>
        <li>Select question</li>
        <li>Reveal question</li>
        <li>Reveal answer</li>
        <li>Hide answer</li>
        <li>Mark question as completed</li>
      </ul>
    </td>
    <td valign="top" width="50%">
      <h4>❓ Question Management</h4>
      <ul>
        <li>Question number</li>
        <li>Question text</li>
        <li>Answer</li>
        <li>Hint or clue</li>
        <li>Category</li>
        <li>Optional notes for operator</li>
        <li>Question status</li>
        <li>Load question set from JSON</li>
      </ul>
    </td>
  </tr>
  <tr>
    <td valign="top" width="50%">
      <h4>🏆 Scoreboard</h4>
      <ul>
        <li>Multiple teams</li>
        <li>Custom team names</li>
        <li>Add score</li>
        <li>Subtract score</li>
        <li>Configurable score increments</li>
        <li>Score history</li>
        <li>Scoreboard display on stage</li>
      </ul>
    </td>
    <td valign="top" width="50%">
      <h4>🖥️ Dual Display</h4>
      <ul>
        <li>Operator console on primary display</li>
        <li>Stage display on secondary display</li>
        <li>Display selection</li>
        <li>Fullscreen stage mode</li>
        <li>Windowed preview</li>
        <li>Single-display fallback</li>
        <li>Display reconnection handling</li>
      </ul>
    </td>
  </tr>
  <tr>
    <td valign="top" colspan="2">
      <h4>📺 Stage Display</h4>
      <ul>
        <li>Game title • Question number • Question text • Answer reveal • Team scoreboard • Game status • Visual transitions</li>
      </ul>
    </td>
  </tr>
</table>

### 🔮 Planned Features

<details>
<summary><b>🎬 Version 2 — Show Experience</b> (Klik untuk melihat detail)</summary>
<br>

- Animated question transitions
- Answer reveal animations
- Countdown timer
- Sound effects
- Intro and outro screens
- Custom stage themes
- Score animations
- Team spotlight
- Round transitions
- Custom fonts and assets
</details>

<details>
<summary><b>🧠 Version 3 — Advanced Game Management</b> (Klik untuk melihat detail)</summary>
<br>

- Question editor
- Question set editor
- Import and export
- Session history
- Autosave
- Undo actions
- Custom scoring rules
- Game presets
- Multiple round configurations
- Random question selection
</details>

<details>
<summary><b>🌌 Future Possibilities</b> (Klik untuk melihat detail)</summary>
<br>

- Buzzer system
- External player devices
- Remote control
- OBS integration
- Custom event themes
- Tournament mode
- Plugin architecture
</details>

---

## 🏗️ Architecture

TTS Studio uses a modular desktop architecture.

```text
┌─────────────────────────────────────┐
│          Operator Console           │
│                                     │
│  Controls / Questions / Scoreboard  │
└──────────────────┬──────────────────┘
                   │
                   ▼
┌─────────────────────────────────────┐
│           Game Controller           │
│                                     │
│     Commands / State / Events       │
└──────────────────┬──────────────────┘
                   │
         ┌─────────┼──────────┐
         ▼         ▼          ▼
┌─────────────┐ ┌─────────┐ ┌──────────────┐
│ Game Engine │ │  Score  │ │  Questions   │
│             │ │ Engine  │ │   Manager    │
└──────┬──────┘ └─────────┘ └──────────────┘
       │
       ▼
┌─────────────────────────────────────┐
│            Game State               │
│                                     │
│ Question / Score / Round / Display  │
└──────────────────┬──────────────────┘
                   │
                   ▼
┌─────────────────────────────────────┐
│            Stage Display            │
│                                     │
│     Public screen / Fullscreen      │
└─────────────────────────────────────┘
```

### 📐 Design Principles
- **Single source of truth:** Game state is centrally managed.
- **Separation of concerns:** UI, logic, data, and rendering are separated.
- **Event-driven:** UI components communicate through signals and events.
- **Offline-first:** The application does not require an internet connection.
- **Fail-safe:** Operator actions should not unexpectedly destroy game state.
- **Extensible:** New features should be added through isolated modules.

---

## 🛠️ Technology Stack

| Component | Technology |
| :--- | :--- |
| **Language** | Python |
| **GUI Framework** | PySide6 |
| **UI System** | Qt Widgets |
| **Animation** | Qt Animation Framework |
| **State Management** | Application-level Game State |
| **Data Storage** | JSON |
| **Audio** | Qt Multimedia |
| **Testing** | pytest |
| **Packaging** | PyInstaller |
| **Version Control** | Git |

---

## 📂 Project Structure

```text
tts-studio/
├── README.md
├── requirements.txt
├── pyproject.toml
├── main.py
│
├── app/
│   ├── __init__.py
│   ├── application.py
│   └── settings.py
│
├── core/
│   ├── __init__.py
│   ├── game_controller.py
│   ├── game_state.py
│   ├── game_engine.py
│   ├── score_engine.py
│   └── events.py
│
├── models/
│   ├── __init__.py
│   ├── question.py
│   ├── team.py
│   └── round.py
│
├── services/
│   ├── __init__.py
│   ├── question_service.py
│   ├── session_service.py
│   ├── settings_service.py
│   └── display_service.py
│
├── ui/
│   ├── __init__.py
│   ├── operator/
│   │   ├── main_window.py
│   │   ├── control_panel.py
│   │   ├── question_panel.py
│   │   ├── scoreboard_panel.py
│   │   └── toolbar.py
│   │
│   ├── display/
│   │   ├── stage_window.py
│   │   ├── question_view.py
│   │   ├── answer_view.py
│   │   └── scoreboard_view.py
│   │
│   ├── components/
│   │   ├── buttons.py
│   │   ├── cards.py
│   │   └── dialogs.py
│   │
│   └── styles/
│       ├── theme.py
│       └── stylesheet.qss
│
├── data/
│   ├── questions/
│   │   └── sample_questions.json
│   └── sessions/
│
├── assets/
│   ├── fonts/
│   ├── images/
│   ├── sounds/
│   └── icons/
│
├── tests/
│   ├── test_game_engine.py
│   ├── test_score_engine.py
│   └── test_question_service.py
│
└── scripts/
    └── build.py
```

---

## 💻 Requirements & Installation

### 📋 Requirements
- Python 3.10 or newer
- Windows, Linux, or macOS with Qt-compatible desktop environment
- Optional second monitor, TV, or projector
- Keyboard and mouse

> **Recommended Setup:** Windows 10 or Windows 11, Python 3.11 or 3.12, and Two displays for live gameplay.

### 🚀 Installation

1. **Clone the repository**
   ```bash
   git clone https://github.com/USERNAME/tts-studio.git
   cd tts-studio
   ```

2. **Create virtual environment**
   ```bash
   python -m venv .venv
   ```
   - **Windows:**
     ```bash
     .venv\Scripts\activate
     ```
   - **Linux/macOS:**
     ```bash
     source .venv/bin/activate
     ```

3. **Install dependencies**
   ```bash
   pip install -r requirements.txt
   ```

4. **Run application**
   ```bash
   python main.py
   ```

---

## 🎮 Basic Gameplay Workflow

1. Launch **TTS Studio**.
2. Select the stage display.
3. Load a question set.
4. Configure teams.
5. Start the game.
6. Select a question.
7. Display the question on stage.
8. Reveal the answer when appropriate.
9. Update team scores.
10. Continue to the next question.
11. End the game.

---

## 📄 Question Data Format

Questions are stored in JSON format.

### Example
```json
{
  "title": "Sample Game",
  "questions": [
    {
      "id": "q001",
      "number": 1,
      "category": "General",
      "question": "Kenapa ayam menyeberang jalan?",
      "answer": "Untuk sampai ke sisi seberang.",
      "hint": "",
      "notes": "",
      "points": 10
    }
  ]
}
```

### Question Schema

| Field | Type | Description |
| :--- | :--- | :--- |
| `id` | `string` | Unique question identifier |
| `number` | `integer` | Display number |
| `category` | `string` | Question category |
| `question` | `string` | Question text |
| `answer` | `string` | Answer text |
| `hint` | `string` | Optional clue |
| `notes` | `string` | Operator notes |
| `points` | `integer` | Default score value |

---

## 🎛️ Operator Controls

The operator console is designed for fast and predictable interaction.

| Action | Description |
| :--- | :--- |
| **Select Question** | Select a question |
| **Show Question** | Display question on stage |
| **Reveal Answer** | Reveal the answer |
| **Hide Answer** | Hide answer |
| **Next Question** | Move to the next question |
| **Previous Question** | Return to the previous question |
| **Add Score** | Increase team score |
| **Subtract Score** | Decrease team score |
| **Pause Game** | Pause the session |
| **Reset Game** | Reset the current session |

### ⌨️ Keyboard Shortcuts

Planned shortcuts:

| Key | Action |
| :--- | :--- |
| <kbd>Space</kbd> | Reveal / advance configured action |
| <kbd>Right Arrow</kbd> | Next question |
| <kbd>Left Arrow</kbd> | Previous question |
| <kbd>R</kbd> | Reveal answer |
| <kbd>P</kbd> | Pause |
| <kbd>Escape</kbd> | Exit fullscreen or safe display mode |

> 💡 **Note:** Keyboard shortcuts must avoid conflicting actions and should be configurable in a later version.

---

## 🖥️ Display Management

TTS Studio supports multiple displays through Qt's screen management.

| Display Modes | Display Behavior |
| :--- | :--- |
| • Operator mode<br>• Stage mode<br>• Stage preview<br>• Fullscreen mode<br>• Single-screen mode | • Stage display can be assigned to a detected monitor.<br>• Stage window can enter fullscreen.<br>• Operator window remains accessible.<br>• Application should handle a missing secondary display.<br>• Display configuration should be recoverable. |

---

## ⚙️ Game State

The game state is managed centrally.

```python
GameState(
    current_question_id=None,
    current_round=1,
    answer_visible=False,
    question_visible=False,
    game_started=False,
    game_paused=False,
    teams=[],
    completed_questions=[]
)
```

*The actual implementation will use appropriate Python data structures or typed models.*

### State Management Rules
- UI components must not independently maintain authoritative game state.
- State changes must go through the game controller.
- Display components should render the current state.
- Score changes should be validated.
- Question progression should be deterministic.
- Reset actions should be explicit.

---

## 🎨 UI Design Direction

<table>
  <tr>
    <td valign="top" width="50%">
      <h4>🎛️ Operator Console</h4>
      <p><i>Prioritizes speed, clarity, and control.</i></p>
      <ul>
        <li>Dark interface</li>
        <li>High contrast</li>
        <li>Large action buttons</li>
        <li>Clear question status</li>
        <li>Team score visibility</li>
        <li>Question navigation</li>
        <li>Minimal unnecessary decoration</li>
        <li>Confirmation for destructive actions</li>
        <li>Keyboard-first interaction where practical</li>
      </ul>
    </td>
    <td valign="top" width="50%">
      <h4>📺 Stage Display</h4>
      <p><i>Prioritizes audience readability.</i></p>
      <ul>
        <li>Large typography</li>
        <li>Minimal interface elements</li>
        <li>Strong contrast</li>
        <li>Consistent layout</li>
        <li>Animated transitions</li>
        <li>Clear question number</li>
        <li>Clear answer reveal</li>
        <li>Scoreboard visibility</li>
        <li>No operator controls</li>
      </ul>
    </td>
  </tr>
</table>

### 🖌️ Visual Theme
Initial design direction:
- Dark broadcast-inspired interface
- Neutral dark background
- Accent color for active actions
- Separate visual states for locked, active, revealed, and completed questions
- Typography optimized for large-screen readability

---

## 🛡️ Safety and Reliability

TTS Studio is designed for live operation.
- Avoid accidental game resets.
- Confirm destructive operations.
- Preserve session state where possible.
- Provide display fallback.
- Avoid blocking the UI during operations.
- Validate question data.
- Keep score changes auditable within the session.
- Handle missing assets gracefully.
- Provide a safe way to exit fullscreen.
- Allow the operator to recover from display errors.

---

## 🧪 Testing

The project should include tests for:
- Question selection
- Question progression
- Answer reveal state
- Game pause and resume
- Score changes
- Score validation
- Session reset
- JSON question loading
- Invalid question data

> *Tests should prioritize core game logic before UI testing.*

---

## 🗺️ Development Roadmap

- [ ] **Phase 1 — Foundation**
  - Project setup, PySide6 application entry point, Main operator window, Secondary stage window, Screen detection, Basic UI theme.
- [ ] **Phase 2 — Core Engine**
  - Game state, Game controller, Question model, Question selection, Question progression, Reveal logic.
- [ ] **Phase 3 — Gameplay**
  - Stage question rendering, Answer reveal, Team management, Score engine, Scoreboard rendering.
- [ ] **Phase 4 — Live Experience**
  - Fullscreen display, Animation system, Countdown, Sound effects, Keyboard shortcuts, Display recovery.
- [ ] **Phase 5 — Data Management**
  - JSON question loading, JSON question export, Session saving, Session recovery, Question editor.
- [ ] **Phase 6 — Distribution**
  - Windows packaging, Application icon, Build scripts, Release configuration, Smoke tests.

---

## 🧭 Development Principles

1. **Build the core engine** before adding visual effects.
2. **Keep the operator UI and stage display independent.**
3. **Use a centralized game state.**
4. **Make operator actions predictable.**
5. **Keep the application offline-capable.**
6. **Prioritize readability** over decorative design.
7. **Build features incrementally.**
8. **Test gameplay logic** independently of the UI.
9. **Keep the codebase modular.**
10. **Avoid premature complexity.**

---

## 📜 License & Status

- **License:** License to be determined.
- **Project Status:** `Planning / Initial Development` — TTS Studio is currently in the specification stage. Features and implementation details may change as development progresses.