#!/bin/bash

# HMDA Dashboard - Production Launcher
# Streamlit auto-reload enabled for development

echo "================================================"
echo "  HMDA Lending Analysis Dashboard v1.0"
echo "================================================"
echo ""
echo "🚀 Launching dashboard..."
echo "📊 Opening at http://localhost:8501"
echo ""
echo "Dashboard Features:"
echo "  ✓ Auto-discovered SQL analyses"
echo "  ✓ Interactive visualizations"
echo "  ✓ Multiple view modes"
echo "  ✓ Data export (CSV/JSON)"
echo ""
echo "Press Ctrl+C to stop the server"
echo ""

streamlit run dashboard.py --logger.level=info
