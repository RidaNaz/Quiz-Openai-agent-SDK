sequenceDiagram
    User->>Triage Agent: "I need an appointment"
    Triage Agent->>Verification Agent: Handoff (verify first)
    Verification Agent->>Google Sheets: Check records
    Google Sheets-->>Verification Agent: Verification status
    Verification Agent->>Triage Agent: Verification complete
    Triage Agent->>Appointment Agent: Handoff (with verified context)
    Appointment Agent->>Google Sheets: Book appointment
    Appointment Agent->>SMTP: Send confirmation
    Appointment Agent-->>User: Appointment details