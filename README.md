# TTS Studio

**A Python-powered desktop game-show controller for live TTS (Teka-Teki Silang / Teka-Teki Sulit) gameplay.**

TTS Studio adalah aplikasi desktop untuk mengelola permainan teka-teki dalam format acara live. Aplikasi menyediakan panel operator dan layar panggung terpisah, sehingga seluruh permainan dapat dikendalikan dari satu komputer dengan monitor tambahan, proyektor, atau TV.

Dibangun menggunakan **Python** dan **PySide6**, TTS Studio dirancang untuk kebutuhan permainan interaktif, presentasi, komunitas, acara panggung, maupun produksi hiburan kecil.

---

## Overview

TTS Studio menggabungkan game controller, pengelolaan pertanyaan, scoreboard, dan stage display dalam satu aplikasi desktop. Operator mengendalikan permainan melalui control panel, sementara penonton melihat tampilan permainan yang dirancang untuk layar besar.

### Core Concept
- **Operator Console:** Pusat kendali permainan.
- **Stage Display:** Tampilan publik yang terpisah dari operator.
- **Game Engine:** Pengelola state dan aturan permainan.
- **Question Manager:** Pengelola soal, petunjuk, dan jawaban.
- **Score Engine:** Pengelola skor dan perubahan skor.
- **Session System:** Pengelola sesi dan progres permainan.

### Goals
- Menyediakan kontrol permainan yang mudah digunakan saat acara live.
- Mendukung dua layar dalam satu komputer.
- Memisahkan operator UI dari stage display.
- Memungkinkan reveal soal dan jawaban secara bertahap.
- Mengelola skor secara real-time.
- Mengurangi kesalahan operator melalui kontrol yang jelas.
- Menyimpan dan memuat kumpulan soal.
- Mendukung penggunaan offline.
- Memungkinkan pengembangan fitur tambahan tanpa merombak core engine.

---

## Features

### Version 1 — Core Game System

#### Game Control
- Start game
- Pause game
- Resume game
- Reset game
- Next question
- Previous question
- Select question
- Reveal question
- Reveal answer
- Hide answer
- Mark question as completed

#### Question Management
- Question number
- Question text
- Answer
- Hint or clue
- Category
- Optional notes for operator
- Question status
- Load question set from JSON

#### Scoreboard
- Multiple teams
- Custom team names
- Add score
- Subtract score
- Configurable score increments
- Score history
- Scoreboard display on stage

#### Dual Display
- Operator console on primary display
- Stage display on secondary display
- Display selection
- Fullscreen stage mode
- Windowed preview
- Single-display fallback
- Display reconnection handling

#### Stage Display
- Game title
- Question number
- Question text
- Answer reveal
- Team scoreboard
- Game status
- Visual transitions

### Planned Features

#### Version 2 — Show Experience
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

#### Version 3 — Advanced Game Management
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

#### Future Possibilities
- Buzzer system
- External player devices
- Remote control
- OBS integration
- Custom event themes
- Tournament mode
- Plugin architecture

---

## Architecture

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

### Design Principles
- **Single source of truth:** Game state is centrally managed.
- **Separation of concerns:** UI, logic, data, and rendering are separated.
- **Event-driven:** UI components communicate through signals and events.
- **Offline-first:** The application does not require an internet connection.
- **Fail-safe:** Operator actions should not unexpectedly destroy game state.
- **Extensible:** New features should be added through isolated modules.

---

## Technology Stack

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

## Project Structure

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

## Requirements

- Python 3.10 or newer
- Windows, Linux, or macOS with Qt-compatible desktop environment
- Optional second monitor, TV, or projector
- Keyboard and mouse

### Recommended Setup
- Windows 10 or Windows 11
- Python 3.11 or 3.12
- Two displays for live gameplay

---

## Installation

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

## Basic Gameplay Workflow

1. Launch TTS Studio.
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

## Question Data Format

Questions are stored in JSON.

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

## Operator Controls

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

### Keyboard Shortcuts

Planned shortcuts:

| Key | Action |
| :--- | :--- |
| `Space` | Reveal / advance configured action |
| `Right Arrow` | Next question |
| `Left Arrow` | Previous question |
| `R` | Reveal answer |
| `P` | Pause |
| `Escape` | Exit fullscreen or safe display mode |

> **Note:** Keyboard shortcuts must avoid conflicting actions and should be configurable in a later version.

---

## Display Management

TTS Studio supports multiple displays through Qt's screen management.

### Display Modes
- Operator mode
- Stage mode
- Stage preview
- Fullscreen mode
- Single-screen mode

### Display Behavior
- Stage display can be assigned to a detected monitor.
- Stage window can enter fullscreen.
- Operator window remains accessible.
- Application should handle a missing secondary display.
- Display configuration should be recoverable.

---

## Game State

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

## UI Design Direction

### Operator Console
The operator console prioritizes speed, clarity, and control.
- Dark interface
- High contrast
- Large action buttons
- Clear question status
- Team score visibility
- Question navigation
- Minimal unnecessary decoration
- Confirmation for destructive actions
- Keyboard-first interaction where practical

### Stage Display
The stage display prioritizes audience readability.
- Large typography
- Minimal interface elements
- Strong contrast
- Consistent layout
- Animated transitions
- Clear question number
- Clear answer reveal
- Scoreboard visibility
- No operator controls

### Visual Theme
Initial design direction:
- Dark broadcast-inspired interface
- Neutral dark background
- Accent color for active actions
- Separate visual states for locked, active, revealed, and completed questions
- Typography optimized for large-screen readability

---

## Safety and Reliability

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

## Testing

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

*Tests should prioritize core game logic before UI testing.*

---

## Development Roadmap

### Phase 1 — Foundation
- Project setup
- PySide6 application entry point
- Main operator window
- Secondary stage window
- Screen detection
- Basic UI theme

### Phase 2 — Core Engine
- Game state
- Game controller
- Question model
- Question selection
- Question progression
- Reveal logic

### Phase 3 — Gameplay
- Stage question rendering
- Answer reveal
- Team management
- Score engine
- Scoreboard rendering

### Phase 4 — Live Experience
- Fullscreen display
- Animation system
- Countdown
- Sound effects
- Keyboard shortcuts
- Display recovery

### Phase 5 — Data Management
- JSON question loading
- JSON question export
- Session saving
- Session recovery
- Question editor

### Phase 6 — Distribution
- Windows packaging
- Application icon
- Build scripts
- Release configuration
- Smoke tests

---

## Development Principles

1. Build the core engine before adding visual effects.
2. Keep the operator UI and stage display independent.
3. Use a centralized game state.
4. Make operator actions predictable.
5. Keep the application offline-capable.
6. Prioritize readability over decorative design.
7. Build features incrementally.
8. Test gameplay logic independently of the UI.
9. Keep the codebase modular.
10. Avoid premature complexity.

---

## License

License to be determined.

---

## Project Status

**Status:** Planning / Initial Development  
TTS Studio is currently in the specification stage. Features and implementation details may change as development progresses.