#!/usr/bin/env python3
"""
Integration test for automatic evaluation on summarization

This script tests the complete flow:
1. Create a session with mock paper text
2. Generate a summary (which triggers automatic evaluation)
3. Verify that evaluation was logged to Langfuse
"""

import asyncio
import sys
import os

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from app.services.llm_service import llm_service, LANGFUSE_ENABLED
from app.services.session_manager import session_manager


async def test_auto_evaluation():
    """Test automatic evaluation on summarization"""

    print("=" * 80)
    print("Automatic Evaluation Integration Test")
    print("=" * 80)
    print()

    # Check Langfuse status
    if LANGFUSE_ENABLED:
        print("✅ Langfuse is ENABLED - all LLM calls will be logged")
    else:
        print("⚠️  Langfuse is DISABLED")
    print()

    # Sample paper text
    paper_text = """
    Title: Attention Is All You Need

    Authors: Ashish Vaswani, Noam Shazeer, Niki Parmar, Jakob Uszkoreit,
    Llion Jones, Aidan N. Gomez, Lukasz Kaiser, Illia Polosukhin

    Abstract:
    The dominant sequence transduction models are based on complex recurrent or
    convolutional neural networks that include an encoder and a decoder. The best
    performing models also connect the encoder and decoder through an attention
    mechanism. We propose a new simple network architecture, the Transformer,
    based solely on attention mechanisms, dispensing with recurrence and convolutions
    entirely. Experiments on two machine translation tasks show these models to be
    superior in quality while being more parallelizable and requiring significantly
    less time to train. Our model achieves 28.4 BLEU on the WMT 2014 English-to-German
    translation task, improving over the existing best results, including ensembles,
    by over 2 BLEU. On the WMT 2014 English-to-French translation task, our model
    establishes a new single-model state-of-the-art BLEU score of 41.8 after training
    for 3.5 days on eight GPUs, a small fraction of the training costs of the best
    models from the literature.

    1. Introduction
    Recurrent neural networks, long short-term memory [13] and gated recurrent [7]
    neural networks in particular, have been firmly established as state of the art
    approaches in sequence modeling and transduction problems such as language
    modeling and machine translation [35, 2, 5]. Numerous efforts have since continued
    to push the boundaries of recurrent language models and encoder-decoder architectures [38, 24, 15].

    Recurrent models typically factor computation along the symbol positions of the
    input and output sequences. Aligning the positions to steps in computation time,
    they generate a sequence of hidden states ht, as a function of the previous hidden
    state ht−1 and the input for position t. This inherently sequential nature precludes
    parallelization within training examples, which becomes critical at longer sequence
    lengths, as memory constraints limit batching across examples.

    2. Model Architecture
    Most competitive neural sequence transduction models have an encoder-decoder
    structure [5, 2, 35]. Here, the encoder maps an input sequence of symbol
    representations (x1, ..., xn) to a sequence of continuous representations z = (z1, ..., zn).
    Given z, the decoder then generates an output sequence (y1, ..., ym) of symbols one
    element at a time. At each step the model is auto-regressive [10], consuming the
    previously generated symbols as additional input when generating the next.

    The Transformer follows this overall architecture using stacked self-attention and
    point-wise, fully connected layers for both the encoder and decoder, shown in the
    left and right halves of Figure 1, respectively.
    """

    # Create a test session
    session_id = session_manager.create_session(
        filename="test_paper.pdf",
        text=paper_text,
        pdf_content=None
    )

    print(f"📄 Created test session: {session_id}")
    print()

    # Step 1: Generate summary (this should trigger automatic evaluation)
    print("📝 Step 1: Generating summary...")
    print("-" * 80)

    summary = await llm_service.summarize_paper(
        paper_text=paper_text,
        model="gpt-5-mini"
    )

    print("✅ Summary generated successfully!")
    print()
    print("Summary preview:")
    print(summary[:300] + "...")
    print()

    # Update session with summary
    session_manager.update_summary(session_id, summary)

    # Step 2: Automatically evaluate the summary
    print("🔍 Step 2: Automatically evaluating summary...")
    print("-" * 80)

    evaluation = await llm_service.evaluate_summary(
        original_text=paper_text,
        summary=summary,
        model="gpt-5-mini",
        session_id=session_id
    )

    print("✅ Evaluation completed!")
    print()
    print("Evaluation Results:")
    print(f"  Overall Score: {evaluation['overall_score']}/10")
    print()
    print("  Detailed Scores:")
    print(f"    - Faithfulness:  {evaluation['faithfulness']}/10")
    print(f"    - Completeness:  {evaluation['completeness']}/10")
    print(f"    - Conciseness:   {evaluation['conciseness']}/10")
    print(f"    - Coherence:     {evaluation['coherence']}/10")
    print(f"    - Clarity:       {evaluation['clarity']}/10")
    print()
    print(f"  Reasoning: {evaluation['reasoning']}")
    print()
    print(f"  Strengths:")
    for strength in evaluation['strengths']:
        print(f"    ✓ {strength}")
    print()
    print(f"  Weaknesses:")
    for weakness in evaluation['weaknesses']:
        print(f"    ✗ {weakness}")
    print()

    # Verify session was updated
    session = session_manager.get_session(session_id)
    assert session.summary is not None, "Summary was not saved to session!"

    print("=" * 80)
    print("✅ Integration test completed successfully!")
    print("=" * 80)
    print()

    if LANGFUSE_ENABLED:
        print("📊 Check Langfuse Dashboard:")
        print("   https://cloud.langfuse.com")
        print()
        print("   You should see TWO traces for this test:")
        print(f"   1. Summary generation (session: {session_id})")
        print(f"   2. Summary evaluation (name: evaluate_summary_{session_id})")
        print()
        print("   Both traces will be linked by the session_id metadata.")
    else:
        print("💡 Enable Langfuse to see automatic logging:")
        print("   Set LANGFUSE_SECRET_KEY and LANGFUSE_PUBLIC_KEY in .env")

    print()
    print(f"🧹 Test session ID: {session_id}")
    print("   (Session will remain in memory until server restart)")


if __name__ == "__main__":
    asyncio.run(test_auto_evaluation())
