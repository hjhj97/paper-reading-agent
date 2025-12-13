#!/usr/bin/env python3
"""
Test script for LLM-as-a-judge evaluation with Langfuse logging

Usage:
    python test_evaluation.py

This script demonstrates how to:
1. Create a mock paper summary
2. Evaluate it using the LLM-as-a-judge approach
3. Verify Langfuse logging is working
"""

import asyncio
import sys
import os

# Add backend to path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from app.services.llm_service import llm_service, LANGFUSE_ENABLED


async def test_evaluation():
    """Test the evaluation service"""

    print("=" * 80)
    print("LLM-as-a-Judge Evaluation Test")
    print("=" * 80)
    print()

    # Check Langfuse status
    if LANGFUSE_ENABLED:
        print("✅ Langfuse is ENABLED - evaluations will be logged")
    else:
        print("⚠️  Langfuse is DISABLED - evaluations will NOT be logged")
    print()

    # Sample paper text (shortened for testing)
    original_text = """
    Title: Attention Is All You Need

    Abstract:
    The dominant sequence transduction models are based on complex recurrent or
    convolutional neural networks that include an encoder and a decoder. The best
    performing models also connect the encoder and decoder through an attention
    mechanism. We propose a new simple network architecture, the Transformer,
    based solely on attention mechanisms, dispensing with recurrence and convolutions
    entirely. Experiments on two machine translation tasks show these models to be
    superior in quality while being more parallelizable and requiring significantly
    less time to train.

    Introduction:
    Recurrent neural networks, long short-term memory and gated recurrent neural
    networks in particular, have been firmly established as state of the art approaches
    in sequence modeling and transduction problems such as language modeling and
    machine translation. Numerous efforts have since continued to push the boundaries
    of recurrent language models and encoder-decoder architectures.
    """

    # Sample summary (good quality)
    good_summary = """
    ## Overview
    This paper introduces the Transformer, a novel neural network architecture for
    sequence transduction tasks that relies entirely on attention mechanisms.

    ## Research Objectives
    To develop a simpler, more parallelizable alternative to recurrent and convolutional
    neural networks for sequence modeling tasks.

    ## Methodology
    The Transformer uses self-attention mechanisms to process sequences without
    recurrence or convolution, enabling better parallelization.

    ## Key Findings
    The model achieves superior performance on machine translation tasks while
    requiring less training time.

    ## Conclusions & Implications
    Attention mechanisms alone are sufficient for high-quality sequence transduction,
    opening new possibilities for parallel processing in NLP.
    """

    # Sample summary (poor quality - missing details)
    poor_summary = """
    This paper talks about a new model called Transformer. It's better than old models
    and works faster. They tested it on translation tasks.
    """

    print("Testing GOOD summary evaluation...")
    print("-" * 80)

    try:
        good_eval = await llm_service.evaluate_summary(
            original_text=original_text,
            summary=good_summary,
            session_id="test-good-summary"
        )

        print("✅ Evaluation completed successfully!")
        print()
        print("Scores:")
        print(f"  Faithfulness:  {good_eval['faithfulness']}/10")
        print(f"  Completeness:  {good_eval['completeness']}/10")
        print(f"  Conciseness:   {good_eval['conciseness']}/10")
        print(f"  Coherence:     {good_eval['coherence']}/10")
        print(f"  Clarity:       {good_eval['clarity']}/10")
        print(f"  Overall Score: {good_eval['overall_score']:.1f}/10")
        print()
        print(f"Reasoning: {good_eval['reasoning']}")
        print()
        print(f"Strengths: {', '.join(good_eval['strengths'])}")
        print(f"Weaknesses: {', '.join(good_eval['weaknesses'])}")
        print()

    except Exception as e:
        print(f"❌ Error evaluating good summary: {e}")
        return

    print()
    print("Testing POOR summary evaluation...")
    print("-" * 80)

    try:
        poor_eval = await llm_service.evaluate_summary(
            original_text=original_text,
            summary=poor_summary,
            session_id="test-poor-summary"
        )

        print("✅ Evaluation completed successfully!")
        print()
        print("Scores:")
        print(f"  Faithfulness:  {poor_eval['faithfulness']}/10")
        print(f"  Completeness:  {poor_eval['completeness']}/10")
        print(f"  Conciseness:   {poor_eval['conciseness']}/10")
        print(f"  Coherence:     {poor_eval['coherence']}/10")
        print(f"  Clarity:       {poor_eval['clarity']}/10")
        print(f"  Overall Score: {poor_eval['overall_score']:.1f}/10")
        print()
        print(f"Reasoning: {poor_eval['reasoning']}")
        print()
        print(f"Strengths: {', '.join(poor_eval['strengths'])}")
        print(f"Weaknesses: {', '.join(poor_eval['weaknesses'])}")
        print()

    except Exception as e:
        print(f"❌ Error evaluating poor summary: {e}")
        return

    print()
    print("=" * 80)
    print("Test completed!")
    print("=" * 80)

    if LANGFUSE_ENABLED:
        print()
        print("📊 Check your Langfuse dashboard to see the logged evaluations:")
        print("   https://cloud.langfuse.com")
        print()
        print("   Look for traces with session IDs:")
        print("   - test-good-summary")
        print("   - test-poor-summary")
    else:
        print()
        print("💡 To enable Langfuse logging, set these environment variables:")
        print("   LANGFUSE_SECRET_KEY=sk-lf-...")
        print("   LANGFUSE_PUBLIC_KEY=pk-lf-...")
        print("   LANGFUSE_BASE_URL=https://cloud.langfuse.com")


if __name__ == "__main__":
    asyncio.run(test_evaluation())
