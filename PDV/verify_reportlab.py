try:
    import reportlab
    from reportlab.pdfgen import canvas
    print("SUCCESS: reportlab imported successfully.")
except ImportError as e:
    print(f"FAILED: {e}")
except Exception as e:
    print(f"ERROR: {e}")
