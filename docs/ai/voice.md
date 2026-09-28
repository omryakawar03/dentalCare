# Voice workflow

Target pipeline: explicit microphone permission → speech-to-text provider adapter → typed intent/slot extraction → Zod/Pydantic validation → authenticated tool → organization/clinic/role check → availability or record validation → confirmation preview for a mutation → standard service transaction → audit event → spoken/text result.

Example: “Book Rahul tomorrow at six.” The assistant resolves patient identity, date/time, clinic and doctor, checks server-authoritative availability, and asks the user to confirm the exact slot. It creates the appointment only after confirmation. Ambiguous patient, clinic, timezone, or slot is a clarification request. The system never treats a transcript as consent or confirmation by itself.

Voice audio/transcripts are sensitive. Request microphone access only when the feature is used, avoid retaining raw audio by default, redact unnecessary identifiers, and expose provider/retention settings. If a provider or connectivity is unavailable, the user can continue with standard UI forms.
