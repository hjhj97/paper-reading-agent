#!/usr/bin/env python3
"""
Test script to validate the new strict evaluation system.

This script tests:
1. A good summary (should score 7-8)
2. An average summary (should score 5-6)
3. A poor summary (should score 3-4)
"""

import asyncio
import sys
import os

# Add the parent directory to the path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from app.services.llm_service import LLMService


async def main():
    llm_service = LLMService()

    # Sample paper text (simplified for testing)
    paper_text = """
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

    Methodology:
    The Transformer follows the overall architecture using stacked self-attention and
    point-wise, fully connected layers for both the encoder and decoder. The encoder
    is composed of a stack of N = 6 identical layers. Each layer has two sub-layers:
    a multi-head self-attention mechanism, and a simple, position-wise fully connected
    feed-forward network.

    Results:
    On the WMT 2014 English-to-German translation task, the big transformer model
    outperforms the best previously reported models (including ensembles) by more than
    2.0 BLEU, establishing a new single-model state-of-the-art BLEU score of 28.4.
    On the WMT 2014 English-to-French translation task, our big model achieves a
    BLEU score of 41.8, outperforming all of the previously published single models.

    Conclusions:
    In this work, we presented the Transformer, the first sequence transduction model
    based entirely on attention, replacing the recurrent layers most commonly used in
    encoder-decoder architectures with multi-headed self-attention. The Transformer
    can be trained significantly faster than architectures based on recurrent or
    convolutional layers.
    """

    print("=" * 80)
    print("STRICT EVALUATION SYSTEM TEST")
    print("=" * 80)
    print()

    # Test 1: GOOD summary (should score 7-8)
    print("📝 TEST 1: GOOD SUMMARY (Expected: 7-8 overall)")
    print("-" * 80)

    good_summary = """
    This paper introduces the Transformer, a novel neural network architecture for
    sequence transduction that relies entirely on attention mechanisms, eliminating
    the need for recurrent and convolutional layers. The architecture consists of
    stacked self-attention and feed-forward layers in both encoder and decoder,
    with the encoder having 6 identical layers containing multi-head self-attention
    and position-wise feed-forward networks.

    The model was evaluated on WMT 2014 translation tasks, achieving state-of-the-art
    BLEU scores: 28.4 for English-to-German (2.0+ BLEU improvement) and 41.8 for
    English-to-French, outperforming all previous single models. The key advantage
    is significantly faster training compared to recurrent or convolutional architectures
    while maintaining superior translation quality and better parallelization.
    """

    evaluation = await llm_service.evaluate_summary(
        original_text=paper_text,
        summary=good_summary,
        model="gpt-5-mini",
        session_id="test_good_001"
    )

    print(f"\n✅ Overall Score: {evaluation['overall_score']}/10")
    print(f"\nDetailed Scores:")
    print(f"  - Faithfulness:  {evaluation['faithfulness']}/10")
    print(f"  - Completeness:  {evaluation['completeness']}/10")
    print(f"  - Conciseness:   {evaluation['conciseness']}/10")
    print(f"  - Coherence:     {evaluation['coherence']}/10")
    print(f"  - Clarity:       {evaluation['clarity']}/10")
    print(f"\nReasoning: {evaluation['reasoning']}")
    print(f"\nStrengths:")
    for strength in evaluation['strengths']:
        print(f"  ✓ {strength}")
    print(f"\nWeaknesses:")
    for weakness in evaluation['weaknesses']:
        print(f"  ✗ {weakness}")

    print("\n" + "=" * 80)
    print()

    # Test 2: AVERAGE summary (should score 5-6)
    print("📝 TEST 2: AVERAGE SUMMARY (Expected: 5-6 overall)")
    print("-" * 80)

    average_summary = """
    The paper discusses the Transformer model which is a new architecture for
    neural networks. It uses attention mechanisms instead of recurrent networks.
    The model has an encoder and decoder with multiple layers. Each layer has
    attention and feed-forward parts.

    The paper shows that the Transformer works well on translation tasks. It
    achieved good BLEU scores on English-to-German and English-to-French translation.
    The model trains faster than other models. It is important to note that this
    is a significant contribution to the field.
    """

    evaluation = await llm_service.evaluate_summary(
        original_text=paper_text,
        summary=average_summary,
        model="gpt-5-mini",
        session_id="test_average_001"
    )

    print(f"\n✅ Overall Score: {evaluation['overall_score']}/10")
    print(f"\nDetailed Scores:")
    print(f"  - Faithfulness:  {evaluation['faithfulness']}/10")
    print(f"  - Completeness:  {evaluation['completeness']}/10")
    print(f"  - Conciseness:   {evaluation['conciseness']}/10")
    print(f"  - Coherence:     {evaluation['coherence']}/10")
    print(f"  - Clarity:       {evaluation['clarity']}/10")
    print(f"\nReasoning: {evaluation['reasoning']}")
    print(f"\nStrengths:")
    for strength in evaluation['strengths']:
        print(f"  ✓ {strength}")
    print(f"\nWeaknesses:")
    for weakness in evaluation['weaknesses']:
        print(f"  ✗ {weakness}")

    print("\n" + "=" * 80)
    print()

    # Test 3: POOR summary (should score 3-4)
    print("📝 TEST 3: POOR SUMMARY (Expected: 3-4 overall)")
    print("-" * 80)

    poor_summary = """
    The Transformer is a machine learning model that uses attention. The paper
    talks about how it's better than RNNs. It has many layers that process data.
    The model achieved very high accuracy on benchmarks, with scores over 95% on
    all tests. The authors conclude that Transformers will replace all existing
    neural network architectures. The model is also 100 times faster than any
    previous approach.
    """

    evaluation = await llm_service.evaluate_summary(
        original_text=paper_text,
        summary=poor_summary,
        model="gpt-5-mini",
        session_id="test_poor_001"
    )

    print(f"\n✅ Overall Score: {evaluation['overall_score']}/10")
    print(f"\nDetailed Scores:")
    print(f"  - Faithfulness:  {evaluation['faithfulness']}/10")
    print(f"  - Completeness:  {evaluation['completeness']}/10")
    print(f"  - Conciseness:   {evaluation['conciseness']}/10")
    print(f"  - Coherence:     {evaluation['coherence']}/10")
    print(f"  - Clarity:       {evaluation['clarity']}/10")
    print(f"\nReasoning: {evaluation['reasoning']}")
    print(f"\nStrengths:")
    for strength in evaluation['strengths']:
        print(f"  ✓ {strength}")
    print(f"\nWeaknesses:")
    for weakness in evaluation['weaknesses']:
        print(f"  ✗ {weakness}")

    print("\n" + "=" * 80)
    print()
    print("🎯 SUMMARY OF RESULTS")
    print("=" * 80)
    print()
    print("If the strict evaluation is working correctly, you should see:")
    print("  • Good summary: 7-8 overall (not 9-10)")
    print("  • Average summary: 5-6 overall (not 7-8)")
    print("  • Poor summary: 3-4 overall (with clear identification of hallucinations)")
    print()
    print("The poor summary contains several hallucinations:")
    print("  • '95% accuracy' - not mentioned in paper")
    print("  • 'replace all existing architectures' - overstated claim")
    print("  • '100 times faster' - exaggerated speed claim")
    print()
    print("Check Langfuse for detailed traces: https://cloud.langfuse.com")
    print()


if __name__ == "__main__":
    asyncio.run(main())
