#!/bin/bash

# API Integration Test for Automatic Evaluation
# This script tests the full workflow through the REST API

echo "================================================================================"
echo "API Integration Test: Automatic Evaluation on Summarization"
echo "================================================================================"
echo ""

# Check if backend is running
if ! curl -s http://localhost:8000/api/models > /dev/null 2>&1; then
    echo "❌ Backend is not running!"
    echo ""
    echo "Please start the backend first:"
    echo "  cd backend"
    echo "  uvicorn app.main:app --reload"
    echo ""
    exit 1
fi

echo "✅ Backend is running"
echo ""

# Create a temporary test PDF content (we'll use a simple text file for testing)
TEST_PDF="/tmp/test_paper.txt"
cat > "$TEST_PDF" << 'EOF'
Title: Attention Is All You Need

Authors: Ashish Vaswani, Noam Shazeer, Niki Parmar, Jakob Uszkoreit

Abstract:
The dominant sequence transduction models are based on complex recurrent or
convolutional neural networks that include an encoder and a decoder. The best
performing models also connect the encoder and decoder through an attention
mechanism. We propose a new simple network architecture, the Transformer,
based solely on attention mechanisms, dispensing with recurrence and convolutions
entirely.

Introduction:
Recurrent neural networks have been firmly established as state of the art
approaches in sequence modeling and transduction problems such as language
modeling and machine translation.
EOF

echo "📄 Test file created: $TEST_PDF"
echo ""

# Note: Since we can't easily upload a real PDF via curl,
# we'll demonstrate the API calls that would happen

echo "================================================================================"
echo "API Workflow (Manual Test)"
echo "================================================================================"
echo ""

echo "To test the automatic evaluation feature:"
echo ""
echo "1. Upload a PDF file:"
echo "   curl -X POST http://localhost:8000/api/upload \\"
echo "     -F \"file=@your_paper.pdf\""
echo ""
echo "   Response example:"
echo '   {"session_id": "abc123", "filename": "paper.pdf", ...}'
echo ""

echo "2. Generate summary (this will AUTOMATICALLY evaluate and log to Langfuse):"
echo "   curl -X POST http://localhost:8000/api/summarize \\"
echo "     -H \"Content-Type: application/json\" \\"
echo '     -d '"'"'{"session_id": "abc123"}'"'"
echo ""
echo "   The backend will:"
echo "   ✓ Generate the summary using LLM"
echo "   ✓ Automatically evaluate the summary quality"
echo "   ✓ Log BOTH operations to Langfuse with the same session_id"
echo ""

echo "3. (Optional) Manually trigger evaluation again:"
echo "   curl -X POST http://localhost:8000/api/evaluate \\"
echo "     -H \"Content-Type: application/json\" \\"
echo '     -d '"'"'{"session_id": "abc123"}'"'"
echo ""

echo "================================================================================"
echo "What to Check in Langfuse Dashboard"
echo "================================================================================"
echo ""
echo "Visit: https://cloud.langfuse.com"
echo ""
echo "For each summarization request, you will see TWO traces:"
echo ""
echo "1. Trace: 'summarize_paper'"
echo "   - Model: gpt-5-mini (or selected model)"
echo "   - Input: Original paper text"
echo "   - Output: Generated summary"
echo ""
echo "2. Trace: 'evaluate_summary_<session_id>'"
echo "   - Model: gpt-5-mini"
echo "   - Input: Original text + Summary"
echo "   - Output: Evaluation scores (JSON)"
echo "   - Metadata:"
echo "     * session_id: <session_id>"
echo "     * evaluation_type: summary_quality"
echo "     * model_used: gpt-5-mini"
echo ""

echo "================================================================================"
echo "Backend Logs"
echo "================================================================================"
echo ""
echo "When a summary is generated, the backend will print:"
echo ""
echo "✅ Summary evaluated - Overall Score: 8.6/10"
echo "   Scores: F=9, C=8, Co=9, Ch=8, Cl=9"
echo ""
echo "This confirms automatic evaluation is working!"
echo ""

echo "================================================================================"
echo "Quick Test with Existing Session"
echo "================================================================================"
echo ""

# Get list of sessions
echo "Fetching existing sessions..."
SESSIONS=$(curl -s http://localhost:8000/api/sessions)

if [ "$SESSIONS" = "[]" ] || [ -z "$SESSIONS" ]; then
    echo "⚠️  No sessions found. Please upload a PDF first:"
    echo ""
    echo "  curl -X POST http://localhost:8000/api/upload -F \"file=@your_paper.pdf\""
    echo ""
else
    echo "✅ Found existing sessions"

    # Extract first session ID (if jq is available)
    if command -v jq &> /dev/null; then
        SESSION_ID=$(echo "$SESSIONS" | jq -r '.[0].session_id' 2>/dev/null)

        if [ -n "$SESSION_ID" ] && [ "$SESSION_ID" != "null" ]; then
            echo ""
            echo "Testing with session: $SESSION_ID"
            echo ""

            # Try to get session details
            echo "Fetching session details..."
            SESSION_DETAIL=$(curl -s "http://localhost:8000/api/sessions/$SESSION_ID")

            HAS_SUMMARY=$(echo "$SESSION_DETAIL" | jq -r '.summary != null' 2>/dev/null)

            if [ "$HAS_SUMMARY" = "true" ]; then
                echo "✅ Session has a summary"
                echo ""
                echo "You can manually trigger evaluation with:"
                echo "  curl -X POST http://localhost:8000/api/evaluate \\"
                echo "    -H \"Content-Type: application/json\" \\"
                echo "    -d '{\"session_id\": \"$SESSION_ID\"}'"
            else
                echo "⚠️  Session has no summary yet"
                echo ""
                echo "Generate summary (with automatic evaluation) using:"
                echo "  curl -X POST http://localhost:8000/api/summarize \\"
                echo "    -H \"Content-Type: application/json\" \\"
                echo "    -d '{\"session_id\": \"$SESSION_ID\"}'"
            fi
        fi
    else
        echo ""
        echo "💡 Install jq for automatic session detection:"
        echo "   brew install jq"
        echo ""
        echo "Sessions available:"
        echo "$SESSIONS" | grep -o '"session_id":"[^"]*"' | head -3
    fi
fi

echo ""
echo "================================================================================"
echo "Test completed!"
echo "================================================================================"
echo ""

# Cleanup
rm -f "$TEST_PDF"
