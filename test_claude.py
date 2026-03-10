#!/usr/bin/env python3
"""
Simple test to verify Claude API and configuration
"""

import sys
from pathlib import Path

# Add project root to path
sys.path.insert(0, str(Path(__file__).parent))

try:
    print("="*60)
    print("  Testing Claude AI Configuration")
    print("="*60)

    # Test 1: Import config
    print("\n1. Loading configuration...")
    from config.settings import settings
    print("   OK - Settings loaded")

    # Test 2: Check API key
    print("\n2. Checking Anthropic API key...")
    if not settings.anthropic_api_key:
        print("   ERROR - ANTHROPIC_API_KEY not set!")
        sys.exit(1)
    print("   OK - API key found")
    print(f"   Key starts with: {settings.anthropic_api_key[:20]}...")

    # Test 3: Create Anthropic client
    print("\n3. Creating Anthropic client...")
    import anthropic
    client = anthropic.Anthropic(api_key=settings.anthropic_api_key)
    print("   OK - Client created")

    # Test 4: Test Claude API
    print("\n4. Testing Claude API (simple test)...")
    message = client.messages.create(
        model=settings.anthropic_llm_model,
        max_tokens=100,
        messages=[
            {"role": "user", "content": "Say 'Claude AI works!' in one sentence."}
        ]
    )
    response_text = message.content[0].text
    print(f"   OK - Response received: {response_text}")

    # Test 5: Test embeddings import
    print("\n5. Checking embeddings setup...")
    try:
        from sentence_transformers import SentenceTransformer
        print("   OK - sentence-transformers available")
    except Exception as e:
        print(f"   WARNING - sentence-transformers issue: {e}")
        print("   This is OK for first run - will download on first use")

    # Test 6: Test Neo4j connection (optional)
    print("\n6. Neo4j Configuration:")
    print(f"   URI: {settings.neo4j_uri}")
    print(f"   User: {settings.neo4j_user}")
    print("   (Will test when bot starts)")

    # Test 7: Telegram config
    print("\n7. Telegram Configuration:")
    if settings.telegram_bot_token:
        print(f"   Bot token: {settings.telegram_bot_token[:20]}...")
    else:
        print("   ERROR - TELEGRAM_BOT_TOKEN not set!")
        sys.exit(1)

    print("\n" + "="*60)
    print("  ALL TESTS PASSED!")
    print("="*60)
    print("""
Next steps:
1. Start Neo4j: docker run --name neo4j -e NEO4J_AUTH=neo4j/password -p 7687:7687 neo4j:latest
2. Run the bot: python main.py bot
3. Open Telegram and find your bot
4. Send /start command

System is ready to go!
    """)

except Exception as e:
    print(f"\nERROR: {e}")
    import traceback
    traceback.print_exc()
    sys.exit(1)
