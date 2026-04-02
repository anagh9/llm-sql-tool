#!/usr/bin/env python3
"""
Debug script to test the chat endpoint flow without FastAPI
Tests the full query pipeline and checks for Decimal JSON serialization issues
"""

import asyncio
import sys
import json
import os
import importlib.util
from decimal import Decimal
from datetime import datetime
from pathlib import Path

# Setup environment
backend_dir = Path('/home/anaghk/Public/Code/llm_sql/backend')
qe_dir = backend_dir / 'query_engine'
os.chdir(str(qe_dir))
sys.path.insert(0, str(qe_dir))

# Load query_engine modules directly
db_spec = importlib.util.spec_from_file_location("database", str(qe_dir / 'database.py'))
database_module = importlib.util.module_from_spec(db_spec)
db_spec.loader.exec_module(database_module)

main_spec = importlib.util.spec_from_file_location("qe_main", str(qe_dir / 'main.py'))
main_module = importlib.util.module_from_spec(main_spec)
sys.modules['database'] = database_module
main_spec.loader.exec_module(main_module)

# Get the functions we need
convert_to_serializable = database_module.convert_to_serializable
ask_product_data = main_module.ask_product_data


def test_json_serialization(obj, label="Object"):
    """Test if an object is JSON serializable"""
    try:
        json_str = json.dumps(obj)
        print(f"✓ {label} is JSON serializable")
        return True
    except TypeError as e:
        print(f"✗ {label} is NOT JSON serializable - {str(e)}")
        return False


def find_decimals(obj, path="root"):
    """Recursively find all Decimal objects"""
    decimals = []
    if isinstance(obj, Decimal):
        decimals.append(f"  {path}: Decimal = {obj}")
    elif isinstance(obj, dict):
        for key, value in obj.items():
            decimals.extend(find_decimals(value, f"{path}['{key}']"))
    elif isinstance(obj, (list, tuple)):
        for i, item in enumerate(obj):
            decimals.extend(find_decimals(item, f"{path}[{i}]"))
    return decimals


async def test_query(message: str):
    """Test a single chat query"""
    print(f"\n{'=' * 80}")
    print(f"Testing: {message}")
    print('=' * 80)

    try:
        # Step 1: Call query engine
        print(f"\n[1] Calling ask_product_data()...")
        answer = await ask_product_data(message)
        print(f"✓ Got response (type: {type(answer).__name__})")
        if len(str(answer)) > 100:
            print(f"    Result: {str(answer)[:100]}...")
        else:
            print(f"    Result: {answer}")

        # Step 2: Build response like the /chat endpoint does
        print(f"\n[2] Building response object...")
        response = {
            "success": True,
            "message": message,
            "answer": answer,
            "cached": False,
            "timestamp": datetime.now().isoformat(),
            "source": "llm",
            "visualise": "month" in message.lower(),
        }
        print(f"✓ Response built")

        # Step 3: Check for Decimals
        print(f"\n[3] Checking for Decimal types...")
        decimals = find_decimals(response)
        if decimals:
            print(f"✗ Found {len(decimals)} Decimal object(s):")
            for d in decimals:
                print(d)
        else:
            print(f"✓ No Decimal types found")

        # Step 4: Test JSON serialization
        print(f"\n[4] Testing JSON serialization...")
        if test_json_serialization(response, "Response"):
            print(f"✓ SUCCESS - Response is JSON serializable!\n")
            return True
        else:
            # Try with conversion
            print(f"\n[5] Attempting to convert with convert_to_serializable()...")
            converted = convert_to_serializable(response)

            decimals = find_decimals(converted)
            if decimals:
                print(
                    f"✗ After conversion, still found {len(decimals)} Decimal(s)")

            if test_json_serialization(converted, "Converted Response"):
                print(f"✓ Conversion worked!\n")
                return True
            else:
                print(f"✗ Conversion did not help\n")
                return False

    except Exception as e:
        print(f"\n✗ Error: {str(e)}")
        import traceback
        traceback.print_exc()
        return False


async def main():
    """Run all debug tests"""
    print(f"\n{'#' * 80}")
    print(f"# DEBUG CHAT ENDPOINT - Testing JSON Serialization")
    print(f"{'#' * 80}")

    results = []
    queries = [
        "How many users are there?",
        "Plot total revenue per month with trends",
    ]

    for query in queries:
        result = await test_query(query)
        results.append((query, "PASS" if result else "FAIL"))

    # Summary
    print(f"\n{'=' * 80}")
    print("SUMMARY")
    print('=' * 80)
    for query, status in results:
        symbol = "✓" if status == "PASS" else "✗"
        print(f"{symbol} {status}: {query}")

    all_passed = all(s == "PASS" for _, s in results)

    print(f"\n{'=' * 80}")
    if all_passed:
        print("✓✓✓ ALL TESTS PASSED - ISSUE IS FIXED! ✓✓✓")
    else:
        print("✗✗✗ SOME TESTS FAILED - ISSUE STILL EXISTS ✗✗✗")
    print('=' * 80 + "\n")

    return all_passed


if __name__ == "__main__":
    success = asyncio.run(main())
    sys.exit(0 if success else 1)
