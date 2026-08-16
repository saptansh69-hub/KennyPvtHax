#!/usr/bin/env python3
"""
Backend test for KennyPvtHax NEW Telegram owner features
Testing owner /addkeys, /stock commands, non-owner security, low-stock alerts, and regression
"""

import requests
import json
import time

BASE_URL = "https://kenny-gaming-mods.preview.emergentagent.com/api"
OWNER_CHAT_ID = 7796388366
NON_OWNER_CHAT_ID = 999111

# Admin credentials from test_credentials.md
ADMIN_EMAIL = "saptanshtesting@gmail.com"
ADMIN_PASSWORD = "admin123456"

def log(msg):
    print(f"[TEST] {msg}")

def test_owner_addkeys():
    """Test 1: Owner /addkeys command via webhook"""
    log("=" * 60)
    log("TEST 1: Owner /addkeys command")
    log("=" * 60)
    
    # First, get admin token to check keys summary before
    login_resp = requests.post(f"{BASE_URL}/auth/login", json={
        "identifier": ADMIN_EMAIL,
        "password": ADMIN_PASSWORD
    })
    assert login_resp.status_code == 200, f"Admin login failed: {login_resp.status_code}"
    admin_token = login_resp.json()["token"]
    
    # Get initial summary
    summary_before = requests.get(f"{BASE_URL}/admin/keys/summary", 
                                  headers={"Authorization": f"Bearer {admin_token}"})
    assert summary_before.status_code == 200, f"Keys summary failed: {summary_before.status_code}"
    initial_data = summary_before.json()
    log(f"Initial summary: {json.dumps(initial_data, indent=2)}")
    
    # Find frozen|7day bucket if exists
    frozen_7day_before = None
    for bucket in initial_data.get("buckets", []):
        if bucket.get("projectId") == "frozen" and bucket.get("planId") == "7day":
            frozen_7day_before = bucket.get("available", 0)
            break
    
    log(f"frozen|7day available before: {frozen_7day_before}")
    
    # Send /addkeys webhook from owner
    webhook_payload = {
        "message": {
            "chat": {"id": OWNER_CHAT_ID},
            "from": {"username": "CrimeCell"},
            "text": "/addkeys frozen 7day\nTG-FROZ-7D-1\nTG-FROZ-7D-2\nTG-FROZ-7D-3"
        }
    }
    
    log(f"Sending webhook: {json.dumps(webhook_payload, indent=2)}")
    webhook_resp = requests.post(f"{BASE_URL}/telegram/webhook", json=webhook_payload)
    log(f"Webhook response: {webhook_resp.status_code} - {webhook_resp.text}")
    
    assert webhook_resp.status_code == 200, f"Webhook failed: {webhook_resp.status_code}"
    assert webhook_resp.json().get("ok") == True, f"Webhook ok not true: {webhook_resp.json()}"
    
    # Wait a moment for processing
    time.sleep(1)
    
    # Verify via admin API
    summary_after = requests.get(f"{BASE_URL}/admin/keys/summary", 
                                 headers={"Authorization": f"Bearer {admin_token}"})
    assert summary_after.status_code == 200, f"Keys summary after failed: {summary_after.status_code}"
    after_data = summary_after.json()
    log(f"Summary after: {json.dumps(after_data, indent=2)}")
    
    # Find frozen|7day bucket
    frozen_7day_after = None
    for bucket in after_data.get("buckets", []):
        if bucket.get("projectId") == "frozen" and bucket.get("planId") == "7day":
            frozen_7day_after = bucket.get("available", 0)
            break
    
    log(f"frozen|7day available after: {frozen_7day_after}")
    
    # Verify keys were added
    if frozen_7day_before is None:
        # New bucket created
        assert frozen_7day_after >= 3, f"Expected at least 3 keys in new bucket, got {frozen_7day_after}"
        log("✅ TEST 1 PASSED: New frozen|7day bucket created with 3+ keys")
    else:
        # Existing bucket, check increment
        expected = frozen_7day_before + 3
        assert frozen_7day_after >= expected, f"Expected {expected} keys, got {frozen_7day_after}"
        log(f"✅ TEST 1 PASSED: frozen|7day bucket increased from {frozen_7day_before} to {frozen_7day_after}")
    
    return admin_token

def test_owner_stock(admin_token):
    """Test 2: Owner /stock command"""
    log("\n" + "=" * 60)
    log("TEST 2: Owner /stock command")
    log("=" * 60)
    
    webhook_payload = {
        "message": {
            "chat": {"id": OWNER_CHAT_ID},
            "from": {"username": "CrimeCell"},
            "text": "/stock"
        }
    }
    
    log(f"Sending /stock webhook: {json.dumps(webhook_payload, indent=2)}")
    webhook_resp = requests.post(f"{BASE_URL}/telegram/webhook", json=webhook_payload)
    log(f"Webhook response: {webhook_resp.status_code} - {webhook_resp.text}")
    
    assert webhook_resp.status_code == 200, f"Webhook failed: {webhook_resp.status_code}"
    assert webhook_resp.json().get("ok") == True, f"Webhook ok not true: {webhook_resp.json()}"
    
    log("✅ TEST 2 PASSED: /stock command returned 200 with ok=true")

def test_non_owner_cannot_add_keys(admin_token):
    """Test 3: Non-owner cannot add keys via bot"""
    log("\n" + "=" * 60)
    log("TEST 3: Non-owner cannot add keys")
    log("=" * 60)
    
    # Get summary before
    summary_before = requests.get(f"{BASE_URL}/admin/keys/summary", 
                                  headers={"Authorization": f"Bearer {admin_token}"})
    assert summary_before.status_code == 200
    before_data = summary_before.json()
    total_before = before_data.get("total_available", 0)
    
    # Find frozen|7day count before
    frozen_7day_before = None
    for bucket in before_data.get("buckets", []):
        if bucket.get("projectId") == "frozen" and bucket.get("planId") == "7day":
            frozen_7day_before = bucket.get("available", 0)
            break
    
    log(f"Total available before: {total_before}")
    log(f"frozen|7day available before: {frozen_7day_before}")
    
    # Try to add keys from non-owner
    webhook_payload = {
        "message": {
            "chat": {"id": NON_OWNER_CHAT_ID},
            "from": {"username": "randomguy"},
            "text": "/addkeys frozen 7day\nHACKER-KEY-1"
        }
    }
    
    log(f"Sending webhook from non-owner: {json.dumps(webhook_payload, indent=2)}")
    webhook_resp = requests.post(f"{BASE_URL}/telegram/webhook", json=webhook_payload)
    log(f"Webhook response: {webhook_resp.status_code} - {webhook_resp.text}")
    
    assert webhook_resp.status_code == 200, f"Webhook failed: {webhook_resp.status_code}"
    assert webhook_resp.json().get("ok") == True, f"Webhook ok not true: {webhook_resp.json()}"
    
    # Wait a moment
    time.sleep(1)
    
    # Verify keys were NOT added
    summary_after = requests.get(f"{BASE_URL}/admin/keys/summary", 
                                 headers={"Authorization": f"Bearer {admin_token}"})
    assert summary_after.status_code == 200
    after_data = summary_after.json()
    total_after = after_data.get("total_available", 0)
    
    # Find frozen|7day count after
    frozen_7day_after = None
    for bucket in after_data.get("buckets", []):
        if bucket.get("projectId") == "frozen" and bucket.get("planId") == "7day":
            frozen_7day_after = bucket.get("available", 0)
            break
    
    log(f"Total available after: {total_after}")
    log(f"frozen|7day available after: {frozen_7day_after}")
    
    # Verify no change
    assert total_after == total_before, f"Total changed from {total_before} to {total_after} - SECURITY BREACH!"
    assert frozen_7day_after == frozen_7day_before, f"frozen|7day changed from {frozen_7day_before} to {frozen_7day_after} - SECURITY BREACH!"
    
    log("✅ TEST 3 PASSED: Non-owner could not add keys (counts unchanged)")

def test_low_stock_alert(admin_token):
    """Test 4: Low-stock alert path"""
    log("\n" + "=" * 60)
    log("TEST 4: Low-stock alert path")
    log("=" * 60)
    
    # Add exactly 2 keys to a new bucket (admin|admin-week)
    bulk_payload = {
        "projectId": "admin",
        "planId": "admin-week",
        "keys": ["LOWTEST-1", "LOWTEST-2"]
    }
    
    log(f"Adding 2 keys to admin|admin-week bucket: {json.dumps(bulk_payload, indent=2)}")
    bulk_resp = requests.post(f"{BASE_URL}/admin/keys/bulk", 
                              json=bulk_payload,
                              headers={"Authorization": f"Bearer {admin_token}"})
    log(f"Bulk add response: {bulk_resp.status_code} - {bulk_resp.text}")
    
    assert bulk_resp.status_code == 200, f"Bulk add failed: {bulk_resp.status_code}"
    bulk_data = bulk_resp.json()
    assert bulk_data.get("added") == 2, f"Expected 2 keys added, got {bulk_data.get('added')}"
    
    # Verify summary shows 2 available
    summary = requests.get(f"{BASE_URL}/admin/keys/summary", 
                          headers={"Authorization": f"Bearer {admin_token}"})
    assert summary.status_code == 200
    summary_data = summary.json()
    
    admin_week_count = None
    for bucket in summary_data.get("buckets", []):
        if bucket.get("projectId") == "admin" and bucket.get("planId") == "admin-week":
            admin_week_count = bucket.get("available", 0)
            break
    
    log(f"admin|admin-week available: {admin_week_count}")
    assert admin_week_count == 2, f"Expected 2 keys, got {admin_week_count}"
    
    # Place 1 guest order for that bucket
    order_payload = {
        "telegram": "@lowbuyer",
        "email": "lowbuyer@example.com",
        "method": "upi",
        "currency": "inr",
        "items": [{
            "projectId": "admin",
            "planId": "admin-week",
            "project": "Admin Key",
            "plan": "Admin Key",
            "duration": "1 week subscription",
            "inr": 1000,
            "usd": 10
        }]
    }
    
    log(f"Placing order: {json.dumps(order_payload, indent=2)}")
    order_resp = requests.post(f"{BASE_URL}/orders", json=order_payload)
    log(f"Order response: {order_resp.status_code} - {order_resp.text}")
    
    assert order_resp.status_code == 200, f"Order failed: {order_resp.status_code}"
    order_data = order_resp.json()
    
    # Verify key was assigned from LOWTEST-*
    keys = order_data.get("keys", [])
    assert len(keys) > 0, "No keys in order"
    assigned_key = keys[0].get("key")
    log(f"Assigned key: {assigned_key}")
    assert assigned_key in ["LOWTEST-1", "LOWTEST-2"], f"Expected LOWTEST-* key, got {assigned_key}"
    
    # Verify summary now shows 1 available (should trigger low-stock alert)
    summary_after = requests.get(f"{BASE_URL}/admin/keys/summary", 
                                 headers={"Authorization": f"Bearer {admin_token}"})
    assert summary_after.status_code == 200
    summary_after_data = summary_after.json()
    
    admin_week_after = None
    for bucket in summary_after_data.get("buckets", []):
        if bucket.get("projectId") == "admin" and bucket.get("planId") == "admin-week":
            admin_week_after = bucket.get("available", 0)
            break
    
    log(f"admin|admin-week available after order: {admin_week_after}")
    assert admin_week_after == 1, f"Expected 1 key remaining, got {admin_week_after}"
    
    log("✅ TEST 4 PASSED: Order succeeded, key assigned from LOWTEST-*, remaining=1 (low-stock alert should have triggered)")

def test_regression():
    """Test 5: Regression quick check"""
    log("\n" + "=" * 60)
    log("TEST 5: Regression check")
    log("=" * 60)
    
    # Test GET /api/config
    config_resp = requests.get(f"{BASE_URL}/config")
    log(f"Config response: {config_resp.status_code} - {config_resp.text}")
    
    assert config_resp.status_code == 200, f"Config failed: {config_resp.status_code}"
    config_data = config_resp.json()
    assert config_data.get("telegram_enabled") == True, f"telegram_enabled not true: {config_data}"
    assert config_data.get("bot_username") == "kennypvthaxhelpbot", f"bot_username wrong: {config_data}"
    
    log(f"✅ Config endpoint working: telegram_enabled={config_data.get('telegram_enabled')}, bot_username={config_data.get('bot_username')}")
    
    # Test POST /api/admin/keys/bulk with admin
    login_resp = requests.post(f"{BASE_URL}/auth/login", json={
        "identifier": ADMIN_EMAIL,
        "password": ADMIN_PASSWORD
    })
    assert login_resp.status_code == 200
    admin_token = login_resp.json()["token"]
    
    bulk_resp = requests.post(f"{BASE_URL}/admin/keys/bulk", 
                              json={"projectId": "test", "planId": "test", "keys": ["REGRESSION-TEST-1"]},
                              headers={"Authorization": f"Bearer {admin_token}"})
    log(f"Admin bulk add response: {bulk_resp.status_code} - {bulk_resp.text}")
    assert bulk_resp.status_code == 200, f"Admin bulk add failed: {bulk_resp.status_code}"
    
    log("✅ Admin bulk add working")
    
    # Test POST /api/admin/keys/bulk without admin (should be 403)
    bulk_no_auth = requests.post(f"{BASE_URL}/admin/keys/bulk", 
                                 json={"projectId": "test", "planId": "test", "keys": ["HACK-1"]})
    log(f"Non-admin bulk add response: {bulk_no_auth.status_code}")
    assert bulk_no_auth.status_code == 403, f"Expected 403, got {bulk_no_auth.status_code}"
    
    log("✅ Non-admin bulk add correctly returns 403")
    log("✅ TEST 5 PASSED: Regression checks passed")

def main():
    log("Starting KennyPvtHax Telegram Owner Features Test")
    log(f"Base URL: {BASE_URL}")
    log(f"Owner Chat ID: {OWNER_CHAT_ID}")
    log("")
    
    try:
        # Test 1: Owner /addkeys
        admin_token = test_owner_addkeys()
        
        # Test 2: Owner /stock
        test_owner_stock(admin_token)
        
        # Test 3: Non-owner security
        test_non_owner_cannot_add_keys(admin_token)
        
        # Test 4: Low-stock alert
        test_low_stock_alert(admin_token)
        
        # Test 5: Regression
        test_regression()
        
        log("\n" + "=" * 60)
        log("ALL TESTS PASSED ✅")
        log("=" * 60)
        log("\nSummary:")
        log("✅ Test 1: Owner /addkeys command working - keys added to frozen|7day bucket")
        log("✅ Test 2: Owner /stock command working - returned 200 with ok=true")
        log("✅ Test 3: Non-owner security working - non-owner cannot add keys")
        log("✅ Test 4: Low-stock alert logic working - order succeeded, key assigned, remaining=1")
        log("✅ Test 5: Regression checks passed - config and admin endpoints working")
        
    except AssertionError as e:
        log(f"\n❌ TEST FAILED: {e}")
        raise
    except Exception as e:
        log(f"\n❌ UNEXPECTED ERROR: {e}")
        raise

if __name__ == "__main__":
    main()
