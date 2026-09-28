# CUSTOM Tools Architecture

The project follows a small MVC structure shared by the desktop and web entry points.

## Structure

```text
mvc/
  models/
    pdf_operations.py         # Core ID-based PDF operations
    pdf_all_operations.py     # Core ordered PDF operations
    pdf_to_word_operations.py # Core PDF to Word (.docx) conversion operations
    media_enhancer_operations.py # Core operations for HD+ video & photo Colab AI
    pdf_model.py              # ID-based model facade
    pdf_all_model.py          # Ordered PDF model facade
    pdf_to_word_model.py      # PDF to Word conversion facade
    media_enhancer_model.py   # HD+ Video & Photo AI enhancer facade
  controllers/
    desktop_controller.py     # Tkinter navigation and registered view lifecycle
    web_controller.py         # Streamlit input-to-model coordination
  views/
    dashboard_view.py         # Tkinter dashboard
    web_guide.py              # Streamlit guide dialog
```

## Entry Points

- `main_app.py` starts the desktop application.
- `app_web.py` starts the Streamlit application.
- `api.py` exposes FastAPI endpoints for PDF merging and Word conversion.
- `colab_server_script.py` is the Google Colab GPU server backend script.
- `ui_merge_pdf.py`, `ui_merge_all.py`, `ui_pdf_to_word.py`, and `ui_media_enhancer.py` are desktop views kept as stable import points.
- `pdf_logic.py` and `pdf_all_logic.py` are compatibility adapters for older imports.

The desktop controller registers every view used by the dashboard, including the
media enhancer, before navigation is available.

## Responsibilities

- **Models** validate input and perform PDF/file operations.
- **Controllers** coordinate user input, model calls, and navigation/state transitions.
- **Views** render Tkinter or Streamlit UI and delegate operations to controllers/models.
