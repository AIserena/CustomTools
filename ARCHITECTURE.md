# CUSTOM Tools Architecture

The project follows a small MVC structure shared by the desktop and web entry points.

## Structure

```text
mvc/
  models/
    pdf_operations.py       # Core ID-based PDF operations
    pdf_all_operations.py   # Core ordered PDF operations
    pdf_model.py            # ID-based model facade
    pdf_all_model.py        # Ordered PDF model facade
  controllers/
    desktop_controller.py   # Tkinter navigation and view lifecycle
    web_controller.py       # Streamlit input-to-model coordination
  views/
    dashboard_view.py       # Tkinter dashboard
    web_guide.py            # Streamlit guide dialog
```

## Entry Points

- `main_app.py` starts the desktop application.
- `app_web.py` starts the Streamlit application.
- `ui_merge_pdf.py` and `ui_merge_all.py` are desktop views kept as stable import points.
- `pdf_logic.py` and `pdf_all_logic.py` are compatibility adapters for older imports.

## Responsibilities

- **Models** validate input and perform PDF/file operations.
- **Controllers** coordinate user input, model calls, and navigation/state transitions.
- **Views** render Tkinter or Streamlit UI and delegate operations to controllers/models.
