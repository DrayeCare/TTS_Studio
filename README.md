🎯 TTS Studio

A Python-powered desktop game-show controller for live TTS (Teka-Teki Silang / Teka-Teki Sulit) gameplay.

📑 Table of Contents

📖 Overview

✨ Features

🏗️ Architecture

🛠️ Technology Stack

📂 Project Structure

💻 Requirements & Installation

🎮 Basic Gameplay Workflow

📄 Question Data Format

🎛️ Operator Controls

🖥️ Display Management

⚙️ Game State

🎨 UI Design Direction

🛡️ Safety and Reliability

🧪 Testing

🗺️ Development Roadmap

🧭 Development Principles

📜 License & Status

📖 Overview

TTS Studio menggabungkan game controller, pengelolaan pertanyaan, scoreboard, dan stage display dalam satu aplikasi desktop. Operator mengendalikan permainan melalui control panel, sementara penonton melihat tampilan permainan yang dirancang untuk layar besar.

🧩 Core Concept

Komponen

Deskripsi

Operator Console

Pusat kendali permainan.

Stage Display

Tampilan publik yang terpisah dari operator.

Game Engine

Pengelola state dan aturan permainan.

Question Manager

Pengelola soal, petunjuk, dan jawaban.

Score Engine

Pengelola skor dan perubahan skor.

Session System

Pengelola sesi dan progres permainan.

🎯 Goals

✅ Menyediakan kontrol permainan yang mudah digunakan saat acara live.

✅ Mendukung dua layar dalam satu komputer.

✅ Memisahkan operator UI dari stage display.

✅ Memungkinkan reveal soal dan jawaban secara bertahap.

✅ Mengelola skor secara real-time.

✅ Mengurangi kesalahan operator melalui kontrol yang jelas.

✅ Menyimpan dan memuat kumpulan soal.

✅ Mendukung penggunaan offline.

✅ Memungkinkan pengembangan fitur tambahan tanpa merombak core engine.

✨ Features

🚀 Version 1 — Core Game System

🔮 Planned Features

Animated question transitions

Answer reveal animations

Countdown timer

Sound effects

Intro and outro screens

Custom stage themes

Score animations

Team spotlight

Round transitions

Custom fonts and assets

Question editor

Question set editor

Import and export

Session history

Autosave

Undo actions

Custom scoring rules

Game presets

Multiple round configurations

Random question selection

Buzzer system

External player devices

Remote control

OBS integration

Custom event themes

Tournament mode

Plugin architecture

🏗️ Architecture

TTS Studio uses a modular desktop architecture.

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


📐 Design Principles

Single source of truth: Game state is centrally managed.

Separation of concerns: UI, logic, data, and rendering are separated.

Event-driven: UI components communicate through signals and events.

Offline-first: The application does not require an internet connection.

Fail-safe: Operator actions should not unexpectedly destroy game state.

Extensible: New features should be added through isolated modules.

🛠️ Technology Stack

Component

Technology

Language

Python

GUI Framework

PySide6

UI System

Qt Widgets

Animation

Qt Animation Framework

State Management

Application-level Game State

Data Storage

JSON

Audio

Qt Multimedia

Testing

pytest

Packaging

PyInstaller

Version Control

Git

📂 Project Structure

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


💻 Requirements & Installation

📋 Requirements

Python 3.10 or newer

Windows, Linux, or macOS with Qt-compatible desktop environment

Optional second monitor, TV, or projector

Keyboard and mouse

Recommended Setup: Windows 10 or Windows 11, Python 3.11 or 3.12, and Two displays for live gameplay.

🚀 Installation

Clone the repository

git clone https://github.com/USERNAME/tts-studio.git
cd tts-studio


Create virtual environment

python -m venv .venv


Windows:

.venv\Scripts\activate


Linux/macOS:

source .venv/bin/activate


Install dependencies

pip install -r requirements.txt


Run application

python main.py


🎮 Basic Gameplay Workflow

Launch TTS Studio.

Select the stage display.

Load a question set.

Configure teams.

Start the game.

Select a question.

Display the question on stage.

Reveal the answer when appropriate.

Update team scores.

Continue to the next question.

End the game.

📄 Question Data Format

Questions are stored in JSON format.

Example

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


Question Schema

Field

Type

Description

id

string

Unique question identifier

number

integer

Display number

category

string

Question category

question

string

Question text

answer

string

Answer text

hint

string

Optional clue

notes

string

Operator notes

points

integer

Default score value

🎛️ Operator Controls

The operator console is designed for fast and predictable interaction.

Action

Description

Select Question

Select a question

Show Question

Display question on stage

Reveal Answer

Reveal the answer

Hide Answer

Hide answer

Next Question

Move to the next question

Previous Question

Return to the previous question

Add Score

Increase team score

Subtract Score

Decrease team score

Pause Game

Pause the session

Reset Game

Reset the current session

⌨️ Keyboard Shortcuts

Planned shortcuts:

Key

Action

Space

Reveal / advance configured action

Right Arrow

Next question

Left Arrow

Previous question

R

Reveal answer

P

Pause

Escape

Exit fullscreen or safe display mode

💡 Note: Keyboard shortcuts must avoid conflicting actions and should be configurable in a later version.

🖥️ Display Management

TTS Studio supports multiple displays through Qt's screen management.

Display Modes

Display Behavior

• Operator mode



• Stage mode



• Stage preview



• Fullscreen mode



• Single-screen mode

• Stage display can be assigned to a detected monitor.



• Stage window can enter fullscreen.



• Operator window remains accessible.



• Application should handle a missing secondary display.



• Display configuration should be recoverable.

⚙️ Game State

The game state is managed centrally.

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


The actual implementation will use appropriate Python data structures or typed models.

State Management Rules

UI components must not independently maintain authoritative game state.

State changes must go through the game controller.

Display components should render the current state.

Score changes should be validated.

Question progression should be deterministic.

Reset actions should be explicit.

🎨 UI Design Direction

🖌️ Visual Theme

Initial design direction:

Dark broadcast-inspired interface

Neutral dark background

Accent color for active actions

Separate visual states for locked, active, revealed, and completed questions

Typography optimized for large-screen readability

🛡️ Safety and Reliability

TTS Studio is designed for live operation.

Avoid accidental game resets.

Confirm destructive operations.

Preserve session state where possible.

Provide display fallback.

Avoid blocking the UI during operations.

Validate question data.

Keep score changes auditable within the session.

Handle missing assets gracefully.

Provide a safe way to exit fullscreen.

Allow the operator to recover from display errors.

🧪 Testing

The project should include tests for:

Question selection

Question progression

Answer reveal state

Game pause and resume

Score changes

Score validation

Session reset

JSON question loading

Invalid question data

Tests should prioritize core game logic before UI testing.

🗺️ Development Roadmap

[ ] Phase 1 — Foundation

Project setup, PySide6 application entry point, Main operator window, Secondary stage window, Screen detection, Basic UI theme.

[ ] Phase 2 — Core Engine

Game state, Game controller, Question model, Question selection, Question progression, Reveal logic.

[ ] Phase 3 — Gameplay

Stage question rendering, Answer reveal, Team management, Score engine, Scoreboard rendering.

[ ] Phase 4 — Live Experience

Fullscreen display, Animation system, Countdown, Sound effects, Keyboard shortcuts, Display recovery.

[ ] Phase 5 — Data Management

JSON question loading, JSON question export, Session saving, Session recovery, Question editor.

[ ] Phase 6 — Distribution

Windows packaging, Application icon, Build scripts, Release configuration, Smoke tests.

🧭 Development Principles

Build the core engine before adding visual effects.

Keep the operator UI and stage display independent.

Use a centralized game state.

Make operator actions predictable.

Keep the application offline-capable.

Prioritize readability over decorative design.

Build features incrementally.

Test gameplay logic independently of the UI.

Keep the codebase modular.

Avoid premature complexity.

📜 License & Status

License: License to be determined.

Project Status: Planning / Initial Development — TTS Studio is currently in the specification stage. Features and implementation details may change as development progresses.