# Gradebook CLI

A simple command-line gradebook built with Python. It manages students, courses, enrollments, and grades using a JSON file for storage.

## Overview

- Input validation via validators
- Clean table output for list commands
- Logging to logs/app.log
- Unit tests for core functionality

## Project Structure

```text
gradebook-cli/
├── LICENSE
├── README.md
├── main.py
├── data/
│   └── gradebook.json
├── gradebook/
│   ├── __init__.py
│   ├── models.py
│   ├── service.py
│   ├── storage.py
│   └── validators.py
├── logs/
│   └── app.log
├── scripts/
│   └── seed.py
└── tests/
    └── test_service.py
```

### Folder description:

- data/ → stores JSON data
- gradebook/ → core application logic
- logs/ → application logs
- scripts/ → helper scripts (e.g., seed data)
- tests/ → unit tests

## Setup

### Create and activate virtual environment

Windows:
```powershell
python -m venv venv
.\venv\Scripts\Activate.ps1
```

macOS/Linux:
```bash
python -m venv venv
source venv/bin/activate
```

No external dependencies required.

## Seed data

```powershell
python .\scripts\seed.py
```

## CLI Usage

Show all commands:
```powershell
python .\main.py --help
```

### Examples

Add student:
```powershell
python .\main.py add-student --name "Aladin Bajra"
```

Add course:
```powershell
python .\main.py add-course --code AA101 --title "AI Systems"
```

Enroll student:
```powershell
python .\main.py enroll --student-id 1 --course AA101
```

Add grade:
```powershell
python .\main.py add-grade --student-id 1 --course AA101 --grade 95
```

List data:
```powershell
python .\main.py list students
python .\main.py list courses --sort code
```

Compute average and GPA:
```powershell
python .\main.py avg --student-id 1 --course AA101
python .\main.py gpa --student-id 1
```

## Tests

```powershell
python -m unittest .\tests\test_service.py -v
```

## Design decisions

- Centralized validation in validators.py
- Simple GPA (mean of course averages)
- JSON storage for simplicity
- CLI-focused design with readable output

## Limitations

- No database (uses JSON)
- No concurrency handling
- GPA is unweighted

## Quick check

```powershell
python .\scripts\seed.py
python .\main.py list students
python .\main.py avg --student-id 1 --course AA101
python .\main.py gpa --student-id 1
```

## Demo Screenshots


- This example demonstrates the core lifecycle of the Gradebook CLI:
- Setup: Created student "John Doe" (ID 5) and course "AA111 - AI Systems".
- Action: Enrolled the student and added multiple grades ($95$ and $85$).
- Results: Automatically calculated a course Average of 90.00 and an overall GPA of 90.00.

<img width="1365" height="310" alt="image" src="https://github.com/user-attachments/assets/42160160-49e5-4173-bb93-a288d32eb77a" />


Automated Testing & Reliability

- This screenshot shows the successful execution of 20 unit tests, ensuring the system's stability:
- Logic Validation: Verifies that invalid grades (e.g., $>100$ or $<0$) and non-numeric inputs are correctly blocked.
- Data Integrity: Confirms unique IDs and prevents duplicate enrollments or courses.Calculation Accuracy: 
- Guarantees precise Average and GPA results across all edge cases.Status: All tests passed (OK), confirming 100% functional reliability.

<img width="1108" height="944" alt="automated tetsing" src="https://github.com/user-attachments/assets/b37112db-1546-4db7-b581-9eddec1a757a" />

