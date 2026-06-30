AGENT_NAME = "Job Application Filler"

SYSTEM_PROMPT = """You fill out and submit job application forms using a provided resume PDF.

1. Download the resume from %resumeUrl% into the sandbox workspace. Use shell curl -L if the browser download is awkward.
2. Read the PDF and extract: full name, email, phone, LinkedIn/portfolio URLs, education, and relevant work experience.
3. Open %applicationUrl%.
4. Dismiss cookie banners, region prompts, or modals that block the form.
5. Fill every required field using resume data. For optional fields with no resume data, leave them empty unless the form clearly requires a value.
6. Upload the downloaded resume PDF to the resume/CV file upload field. If the file input is hidden, use the visible upload button or drag-and-drop area.
7. Review the form for validation errors and fix any issues before submitting.
8. Click through any multi-step flow until you reach the final Submit or Apply button, then submit the application.
9. Confirm submission succeeded by checking for a confirmation message, thank-you page, or application-received screen. Capture what you see in confirmationMessage.
10. If a required field cannot be filled or submission fails, explain why in notes and set submitted to false.

Rules:
- Report only values you actually read from the resume or entered on the form.
- Never invent personal information.
- Complete the full application and submit it unless submission is blocked by a required field you cannot answer.
"""

RESULT_SCHEMA = {
    "type": "object",
    "properties": {
        "status": {
            "type": "string",
            "description": "submitted, partial, or failed",
        },
        "submitted": {
            "type": "boolean",
            "description": "Whether the application was successfully submitted",
        },
        "candidateName": {
            "type": "string",
            "description": "Name extracted from the resume",
        },
        "fieldsFilled": {
            "type": "number",
            "description": "Approximate count of form fields filled",
        },
        "resumeUploaded": {
            "type": "boolean",
            "description": "Whether the resume PDF was attached to the upload field",
        },
        "confirmationMessage": {
            "type": "string",
            "description": "Success or error text shown after attempting submission",
        },
        "notes": {
            "type": "string",
            "description": "Fields that could not be filled, upload issues, or other blockers",
        },
    },
    "required": ["status", "submitted", "resumeUploaded"],
}

DEFAULT_APPLICATION_URL = (
    "https://jobs.ashbyhq.com/reviserobotics/"
    "7b0426d4-cf8c-4fdf-98a8-5a0360706633/application"
)

DEFAULT_TASK = (
    "Fill out and submit the job application using the provided resume."
)

API_BASE = "https://api.browserbase.com/v1"
TERMINAL_STATUSES = {"COMPLETED", "FAILED", "STOPPED", "TIMED_OUT"}
