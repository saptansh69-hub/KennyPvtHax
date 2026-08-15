#!/usr/bin/env python3
"""
Backend API Testing for KennyPvtHax - KeyAuth Removal + Key Inventory + Telegram Delivery
Tests based on review request requirements
"""
import requests
import json
import time
from typing import Dict, Optional

# Backend URL from frontend/.env
BASE_URL = "https://kenny-gaming-mods.preview.emergentagent.com/api"

class TestRunner:
    def __init__(self):
        self.passed = 0
        self.failed = 0
        self.tests = []
        self.critical_failures = []
        
    def test(self, name: str, condition: bool, details: str = "", critical: bool = False):
        """Record test result"""
        if condition:
            self.passed += 1
            status = "✅ PASS"
        else:
            self.failed += 1
            status = "❌ FAIL"
            if critical:
                self.critical_failures.append(f"{name}: {details}")
        
        result = f"{status}: {name}"
        if details:
            result += f"\n   Details: {details}"
        self.tests.append(result)
        print(result)
        return condition
        
    def summary(self):
        """Print test summary"""
        total = self.passed + self.failed
        print("\n" + "="*80)
        print(f"TEST SUMMARY: {self.passed}/{total} passed ({self.failed} failed)")
        print("="*80)
        if self.critical_failures:
            print("\n🚨 CRITICAL FAILURES:")
            for failure in self.critical_failures:
                print(f"  - {failure}")
            print()
        return self.failed == 0


def main():
    runner = TestRunner()
    
    print("="*80)
    print("BACKEND API TESTING - KennyPvtHax (KeyAuth Removal + Key Inventory)")
    print("="*80)
    
    # ========== 1. GET /api/config ==========
    print("\n[1] Testing GET /api/config")
    bot_username = None
    try:
        r = requests.get(f"{BASE_URL}/config", timeout=10)
        runner.test(
            "GET /api/config returns 200",
            r.status_code == 200,
            f"Status: {r.status_code}",
            critical=True
        )
        
        if r.status_code == 200:
            data = r.json()
            runner.test(
                "config.telegram_enabled is true",
                data.get("telegram_enabled") == True,
                f"telegram_enabled: {data.get('telegram_enabled')}",
                critical=True
            )
            bot_username = data.get("bot_username")
            runner.test(
                "config.bot_username is present",
                bot_username is not None and len(bot_username) > 0,
                f"bot_username: {bot_username}",
                critical=True
            )
            print(f"   ℹ️  Bot username: {bot_username}")
    except Exception as e:
        runner.test("GET /api/config", False, f"Exception: {e}", critical=True)
    
    # ========== 2. Admin Authentication ==========
    print("\n[2] Testing Admin Authentication (saptanshtesting@gmail.com)")
    admin_token = None
    non_admin_token = None
    
    # First, try to reset password for admin user
    try:
        forgot_payload = {"identifier": "saptanshtesting@gmail.com"}
        r = requests.post(f"{BASE_URL}/auth/forgot", json=forgot_payload, timeout=10)
        if r.status_code == 200:
            data = r.json()
            if data.get("found") and data.get("reset_token"):
                reset_token = data["reset_token"]
                print(f"   ℹ️  Got reset token for admin user")
                
                # Reset password
                reset_payload = {"token": reset_token, "password": "admin123456"}
                r = requests.post(f"{BASE_URL}/auth/reset", json=reset_payload, timeout=10)
                if r.status_code == 200:
                    admin_token = r.json().get("token")
                    print(f"   ℹ️  Password reset successful, got admin token")
    except Exception as e:
        print(f"   ℹ️  Password reset attempt: {e}")
    
    # If reset didn't work, try login
    if not admin_token:
        try:
            login_payload = {"identifier": "saptanshtesting@gmail.com", "password": "admin123456"}
            r = requests.post(f"{BASE_URL}/auth/login", json=login_payload, timeout=10)
            if r.status_code == 200:
                admin_token = r.json().get("token")
                print(f"   ℹ️  Login successful")
            elif r.status_code == 401:
                # Try signup
                print(f"   ℹ️  Login failed, trying signup...")
                signup_payload = {
                    "name": "Admin User",
                    "email": "saptanshtesting@gmail.com",
                    "password": "admin123456"
                }
                r = requests.post(f"{BASE_URL}/auth/signup", json=signup_payload, timeout=10)
                if r.status_code == 200:
                    admin_token = r.json().get("token")
                    print(f"   ℹ️  Signup successful")
        except Exception as e:
            print(f"   ℹ️  Login/signup attempt: {e}")
    
    runner.test(
        "Admin user authenticated",
        admin_token is not None,
        f"Token obtained: {admin_token is not None}",
        critical=True
    )
    
    # Create a non-admin user for testing
    print("\n[3] Creating non-admin user for testing")
    try:
        import random
        import string
        rand_suffix = ''.join(random.choices(string.ascii_lowercase + string.digits, k=8))
        non_admin_email = f"testuser_{rand_suffix}@example.com"
        
        signup_payload = {
            "name": "Test User",
            "email": non_admin_email,
            "password": "test123456"
        }
        r = requests.post(f"{BASE_URL}/auth/signup", json=signup_payload, timeout=10)
        if r.status_code == 200:
            non_admin_token = r.json().get("token")
            runner.test(
                "Non-admin user created",
                True,
                f"Email: {non_admin_email}"
            )
    except Exception as e:
        runner.test("Non-admin user creation", False, f"Exception: {e}")
    
    # ========== 3. Admin Key Inventory - Bulk Upload ==========
    print("\n[4] Testing POST /api/admin/keys/bulk")
    
    if not admin_token:
        print("   ⚠️  Skipping admin tests - no admin token")
        runner.test("Admin key bulk upload", False, "No admin token available", critical=True)
    else:
        # Test 1: Add og|1day keys
        try:
            headers = {"Authorization": f"Bearer {admin_token}"}
            payload = {
                "projectId": "og",
                "planId": "1day",
                "keys": ["KENNY-OG1-AAAA", "KENNY-OG1-BBBB"]
            }
            r = requests.post(f"{BASE_URL}/admin/keys/bulk", json=payload, headers=headers, timeout=10)
            runner.test(
                "POST /api/admin/keys/bulk returns 200",
                r.status_code == 200,
                f"Status: {r.status_code}",
                critical=True
            )
            
            if r.status_code == 200:
                data = r.json()
                runner.test(
                    "First bulk upload: added=2, skipped=0",
                    data.get("added") == 2 and data.get("skipped") == 0,
                    f"added: {data.get('added')}, skipped: {data.get('skipped')}"
                )
        except Exception as e:
            runner.test("POST /api/admin/keys/bulk (first)", False, f"Exception: {e}", critical=True)
        
        # Test 2: Add same keys again (deduplication)
        try:
            headers = {"Authorization": f"Bearer {admin_token}"}
            payload = {
                "projectId": "og",
                "planId": "1day",
                "keys": ["KENNY-OG1-AAAA", "KENNY-OG1-BBBB"]
            }
            r = requests.post(f"{BASE_URL}/admin/keys/bulk", json=payload, headers=headers, timeout=10)
            
            if r.status_code == 200:
                data = r.json()
                runner.test(
                    "Second bulk upload (deduplication): added=0, skipped=2",
                    data.get("added") == 0 and data.get("skipped") == 2,
                    f"added: {data.get('added')}, skipped: {data.get('skipped')}"
                )
        except Exception as e:
            runner.test("POST /api/admin/keys/bulk (deduplication)", False, f"Exception: {e}")
        
        # Test 3: Add uncategorized key (no project/plan)
        try:
            headers = {"Authorization": f"Bearer {admin_token}"}
            payload = {
                "keys": ["GLOBAL-KEY-1"]
            }
            r = requests.post(f"{BASE_URL}/admin/keys/bulk", json=payload, headers=headers, timeout=10)
            
            if r.status_code == 200:
                data = r.json()
                runner.test(
                    "Uncategorized key upload: added=1",
                    data.get("added") == 1,
                    f"added: {data.get('added')}, skipped: {data.get('skipped')}"
                )
        except Exception as e:
            runner.test("POST /api/admin/keys/bulk (uncategorized)", False, f"Exception: {e}")
        
        # Test 4: Non-admin access should fail (403)
        if non_admin_token:
            try:
                headers = {"Authorization": f"Bearer {non_admin_token}"}
                payload = {
                    "projectId": "og",
                    "planId": "1day",
                    "keys": ["KENNY-TEST-1"]
                }
                r = requests.post(f"{BASE_URL}/admin/keys/bulk", json=payload, headers=headers, timeout=10)
                runner.test(
                    "Non-admin bulk upload returns 403",
                    r.status_code == 403,
                    f"Status: {r.status_code}"
                )
            except Exception as e:
                runner.test("Non-admin bulk upload", False, f"Exception: {e}")
        
        # Test 5: No token should fail (403)
        try:
            payload = {
                "projectId": "og",
                "planId": "1day",
                "keys": ["KENNY-TEST-2"]
            }
            r = requests.post(f"{BASE_URL}/admin/keys/bulk", json=payload, timeout=10)
            runner.test(
                "Bulk upload without token returns 403",
                r.status_code == 403,
                f"Status: {r.status_code}"
            )
        except Exception as e:
            runner.test("Bulk upload without token", False, f"Exception: {e}")
    
    # ========== 4. Admin Key Summary ==========
    print("\n[5] Testing GET /api/admin/keys/summary")
    
    if not admin_token:
        print("   ⚠️  Skipping - no admin token")
    else:
        try:
            headers = {"Authorization": f"Bearer {admin_token}"}
            r = requests.get(f"{BASE_URL}/admin/keys/summary", headers=headers, timeout=10)
            runner.test(
                "GET /api/admin/keys/summary returns 200",
                r.status_code == 200,
                f"Status: {r.status_code}",
                critical=True
            )
            
            if r.status_code == 200:
                data = r.json()
                buckets = data.get("buckets", [])
                total_available = data.get("total_available", 0)
                
                runner.test(
                    "Summary has buckets array",
                    isinstance(buckets, list),
                    f"Buckets count: {len(buckets)}"
                )
                
                # Check for og|1day bucket
                og_1day_bucket = next((b for b in buckets if b.get("projectId") == "og" and b.get("planId") == "1day"), None)
                runner.test(
                    "og|1day bucket exists with available>=2",
                    og_1day_bucket is not None and og_1day_bucket.get("available", 0) >= 2,
                    f"og|1day available: {og_1day_bucket.get('available') if og_1day_bucket else 0}"
                )
                
                # Check for any|any bucket (uncategorized)
                any_any_bucket = next((b for b in buckets if b.get("projectId") == "any" and b.get("planId") == "any"), None)
                runner.test(
                    "any|any bucket exists (uncategorized keys)",
                    any_any_bucket is not None,
                    f"any|any available: {any_any_bucket.get('available') if any_any_bucket else 0}"
                )
                
                runner.test(
                    "total_available reflects count",
                    total_available >= 3,
                    f"total_available: {total_available}"
                )
                
                print(f"   ℹ️  Summary: {len(buckets)} buckets, {total_available} keys available")
        except Exception as e:
            runner.test("GET /api/admin/keys/summary", False, f"Exception: {e}", critical=True)
        
        # Test non-admin access (403)
        if non_admin_token:
            try:
                headers = {"Authorization": f"Bearer {non_admin_token}"}
                r = requests.get(f"{BASE_URL}/admin/keys/summary", headers=headers, timeout=10)
                runner.test(
                    "Non-admin summary returns 403",
                    r.status_code == 403,
                    f"Status: {r.status_code}"
                )
            except Exception as e:
                runner.test("Non-admin summary", False, f"Exception: {e}")
        
        # Test without token (403)
        try:
            r = requests.get(f"{BASE_URL}/admin/keys/summary", timeout=10)
            runner.test(
                "Summary without token returns 403",
                r.status_code == 403,
                f"Status: {r.status_code}"
            )
        except Exception as e:
            runner.test("Summary without token", False, f"Exception: {e}")
    
    # ========== 5. Order Key Assignment from Inventory ==========
    print("\n[6] Testing Order Key Assignment from Inventory")
    
    order_ids = []
    
    # Test 1: Order og|1day (should get KENNY-OG1-*)
    try:
        payload = {
            "telegram": "@buyer1",
            "items": [
                {
                    "projectId": "og",
                    "project": "OG Cheats",
                    "planId": "1day",
                    "plan": "1 Day",
                    "duration": "24 hours",
                    "inr": 120,
                    "usd": 1
                }
            ]
        }
        r = requests.post(f"{BASE_URL}/orders", json=payload, timeout=10)
        runner.test(
            "POST /api/orders (og|1day) returns 200",
            r.status_code == 200,
            f"Status: {r.status_code}",
            critical=True
        )
        
        if r.status_code == 200:
            data = r.json()
            order_ids.append(data.get("id"))
            keys = data.get("keys", [])
            
            if keys:
                key_value = keys[0].get("key")
                source = keys[0].get("source")
                stock_ok = data.get("stock_ok")
                delivered = data.get("delivered")
                telegram_deeplink = data.get("telegram_deeplink")
                bot_username_in_order = data.get("bot_username")
                
                runner.test(
                    "Order key is from og|1day inventory (KENNY-OG1-*)",
                    key_value and key_value.startswith("KENNY-OG1-"),
                    f"key: {key_value}"
                )
                
                runner.test(
                    "Order key source is 'inventory'",
                    source == "inventory",
                    f"source: {source}"
                )
                
                runner.test(
                    "Order stock_ok is true",
                    stock_ok == True,
                    f"stock_ok: {stock_ok}"
                )
                
                runner.test(
                    "Order delivered is false (no chat mapping yet)",
                    delivered == False,
                    f"delivered: {delivered}"
                )
                
                runner.test(
                    "Order has telegram_deeplink",
                    telegram_deeplink and "t.me/" in telegram_deeplink and "?start=" in telegram_deeplink,
                    f"telegram_deeplink: {telegram_deeplink}"
                )
                
                runner.test(
                    "Order has bot_username",
                    bot_username_in_order is not None,
                    f"bot_username: {bot_username_in_order}"
                )
                
                print(f"   ℹ️  Order 1: key={key_value}, source={source}, deeplink={telegram_deeplink}")
    except Exception as e:
        runner.test("POST /api/orders (og|1day #1)", False, f"Exception: {e}", critical=True)
    
    # Test 2: Order og|1day again (should get second KENNY-OG1-*)
    try:
        payload = {
            "telegram": "@buyer2",
            "items": [
                {
                    "projectId": "og",
                    "project": "OG Cheats",
                    "planId": "1day",
                    "plan": "1 Day",
                    "duration": "24 hours",
                    "inr": 120,
                    "usd": 1
                }
            ]
        }
        r = requests.post(f"{BASE_URL}/orders", json=payload, timeout=10)
        
        if r.status_code == 200:
            data = r.json()
            order_ids.append(data.get("id"))
            keys = data.get("keys", [])
            
            if keys:
                key_value = keys[0].get("key")
                source = keys[0].get("source")
                
                runner.test(
                    "Order 2: key is from og|1day inventory",
                    key_value and key_value.startswith("KENNY-OG1-"),
                    f"key: {key_value}"
                )
                
                print(f"   ℹ️  Order 2: key={key_value}, source={source}")
    except Exception as e:
        runner.test("POST /api/orders (og|1day #2)", False, f"Exception: {e}")
    
    # Test 3: Order og|1day again (should fall back to GLOBAL-KEY-1)
    try:
        payload = {
            "telegram": "@buyer3",
            "items": [
                {
                    "projectId": "og",
                    "project": "OG Cheats",
                    "planId": "1day",
                    "plan": "1 Day",
                    "duration": "24 hours",
                    "inr": 120,
                    "usd": 1
                }
            ]
        }
        r = requests.post(f"{BASE_URL}/orders", json=payload, timeout=10)
        
        if r.status_code == 200:
            data = r.json()
            order_ids.append(data.get("id"))
            keys = data.get("keys", [])
            
            if keys:
                key_value = keys[0].get("key")
                source = keys[0].get("source")
                
                runner.test(
                    "Order 3: key falls back to uncategorized (GLOBAL-KEY-1)",
                    key_value == "GLOBAL-KEY-1",
                    f"key: {key_value}"
                )
                
                runner.test(
                    "Order 3: source is still 'inventory'",
                    source == "inventory",
                    f"source: {source}"
                )
                
                print(f"   ℹ️  Order 3: key={key_value}, source={source} (fallback to global)")
    except Exception as e:
        runner.test("POST /api/orders (og|1day #3 - fallback)", False, f"Exception: {e}")
    
    # Test 4: Order og|1day when all keys exhausted (should get null)
    try:
        payload = {
            "telegram": "@buyer4",
            "items": [
                {
                    "projectId": "og",
                    "project": "OG Cheats",
                    "planId": "1day",
                    "plan": "1 Day",
                    "duration": "24 hours",
                    "inr": 120,
                    "usd": 1
                }
            ]
        }
        r = requests.post(f"{BASE_URL}/orders", json=payload, timeout=10)
        
        if r.status_code == 200:
            data = r.json()
            order_ids.append(data.get("id"))
            keys = data.get("keys", [])
            stock_ok = data.get("stock_ok")
            
            if keys:
                key_value = keys[0].get("key")
                source = keys[0].get("source")
                
                runner.test(
                    "Order 4: key is null (out of stock)",
                    key_value is None,
                    f"key: {key_value}"
                )
                
                runner.test(
                    "Order 4: source is 'pending'",
                    source == "pending",
                    f"source: {source}"
                )
                
                runner.test(
                    "Order 4: stock_ok is false",
                    stock_ok == False,
                    f"stock_ok: {stock_ok}"
                )
                
                print(f"   ℹ️  Order 4: key={key_value}, source={source}, stock_ok={stock_ok} (out of stock)")
    except Exception as e:
        runner.test("POST /api/orders (og|1day #4 - out of stock)", False, f"Exception: {e}")
    
    # ========== 6. GET /api/orders/me ==========
    print("\n[7] Testing GET /api/orders/me (authenticated orders)")
    
    # Create an authenticated order
    if admin_token:
        try:
            headers = {"Authorization": f"Bearer {admin_token}"}
            payload = {
                "telegram": "@admin_buyer",
                "items": [
                    {
                        "projectId": "frozen",
                        "project": "Frozen Fire",
                        "planId": "7day",
                        "plan": "7 Days",
                        "duration": "7 days",
                        "inr": 500,
                        "usd": 6
                    }
                ]
            }
            r = requests.post(f"{BASE_URL}/orders", json=payload, headers=headers, timeout=10)
            
            if r.status_code == 200:
                data = r.json()
                auth_order_id = data.get("id")
                
                # Now get orders
                r = requests.get(f"{BASE_URL}/orders/me", headers=headers, timeout=10)
                runner.test(
                    "GET /api/orders/me returns 200",
                    r.status_code == 200,
                    f"Status: {r.status_code}"
                )
                
                if r.status_code == 200:
                    data = r.json()
                    orders = data.get("orders", [])
                    
                    runner.test(
                        "Orders list is not empty",
                        len(orders) > 0,
                        f"Orders count: {len(orders)}"
                    )
                    
                    if orders:
                        order = orders[0]
                        runner.test(
                            "Order has telegram_deeplink",
                            "telegram_deeplink" in order,
                            f"telegram_deeplink present: {'telegram_deeplink' in order}"
                        )
                        
                        runner.test(
                            "Order has bot_username",
                            "bot_username" in order,
                            f"bot_username present: {'bot_username' in order}"
                        )
        except Exception as e:
            runner.test("GET /api/orders/me", False, f"Exception: {e}")
    
    # ========== 7. Telegram Webhook Simulation ==========
    print("\n[8] Testing POST /api/telegram/webhook")
    
    # Test 1: /start without payload (stores chat mapping)
    try:
        payload = {
            "message": {
                "chat": {"id": 123456},
                "from": {"username": "buyer1"},
                "text": "/start"
            }
        }
        r = requests.post(f"{BASE_URL}/telegram/webhook", json=payload, timeout=10)
        runner.test(
            "Webhook /start (no payload) returns 200",
            r.status_code == 200,
            f"Status: {r.status_code}"
        )
        
        if r.status_code == 200:
            data = r.json()
            runner.test(
                "Webhook response has ok:true",
                data.get("ok") == True,
                f"ok: {data.get('ok')}"
            )
    except Exception as e:
        runner.test("Webhook /start (no payload)", False, f"Exception: {e}")
    
    # Test 2: /start with order ID (delivers order)
    if order_ids:
        try:
            order_id = order_ids[0]  # Use first order
            payload = {
                "message": {
                    "chat": {"id": 123456},
                    "from": {"username": "buyer1"},
                    "text": f"/start {order_id}"
                }
            }
            r = requests.post(f"{BASE_URL}/telegram/webhook", json=payload, timeout=10)
            runner.test(
                "Webhook /start with order ID returns 200",
                r.status_code == 200,
                f"Status: {r.status_code}"
            )
            
            if r.status_code == 200:
                data = r.json()
                runner.test(
                    "Webhook response has ok:true",
                    data.get("ok") == True,
                    f"ok: {data.get('ok')}"
                )
                
                print(f"   ℹ️  Webhook processed order delivery for {order_id}")
        except Exception as e:
            runner.test("Webhook /start with order ID", False, f"Exception: {e}")
    
    # ========== 8. Regression Tests ==========
    print("\n[9] Regression Testing")
    
    # Test auth endpoints still work
    try:
        import random
        import string
        rand_suffix = ''.join(random.choices(string.ascii_lowercase + string.digits, k=8))
        test_email = f"regression_{rand_suffix}@example.com"
        
        # Signup
        payload = {
            "name": "Regression Test",
            "email": test_email,
            "password": "test123456"
        }
        r = requests.post(f"{BASE_URL}/auth/signup", json=payload, timeout=10)
        runner.test(
            "Regression: POST /api/auth/signup works",
            r.status_code == 200,
            f"Status: {r.status_code}"
        )
        
        if r.status_code == 200:
            token = r.json().get("token")
            
            # Login
            login_payload = {"identifier": test_email, "password": "test123456"}
            r = requests.post(f"{BASE_URL}/auth/login", json=login_payload, timeout=10)
            runner.test(
                "Regression: POST /api/auth/login works",
                r.status_code == 200,
                f"Status: {r.status_code}"
            )
            
            # Me
            headers = {"Authorization": f"Bearer {token}"}
            r = requests.get(f"{BASE_URL}/auth/me", headers=headers, timeout=10)
            runner.test(
                "Regression: GET /api/auth/me works",
                r.status_code == 200,
                f"Status: {r.status_code}"
            )
    except Exception as e:
        runner.test("Regression: Auth endpoints", False, f"Exception: {e}")
    
    # Test feedback endpoints still work
    try:
        # GET feedback
        r = requests.get(f"{BASE_URL}/feedback", timeout=10)
        runner.test(
            "Regression: GET /api/feedback works",
            r.status_code == 200,
            f"Status: {r.status_code}"
        )
        
        # POST feedback
        payload = {
            "name": "Regression Tester",
            "rating": 5,
            "message": "Testing feedback after KeyAuth removal"
        }
        r = requests.post(f"{BASE_URL}/feedback", json=payload, timeout=10)
        runner.test(
            "Regression: POST /api/feedback works",
            r.status_code == 200,
            f"Status: {r.status_code}"
        )
    except Exception as e:
        runner.test("Regression: Feedback endpoints", False, f"Exception: {e}")
    
    # Test /api/admin/keyauth/generate does NOT exist
    if admin_token:
        try:
            headers = {"Authorization": f"Bearer {admin_token}"}
            payload = {"count": 1, "plan": "1day"}
            r = requests.post(f"{BASE_URL}/admin/keyauth/generate", json=payload, headers=headers, timeout=10)
            runner.test(
                "Regression: /api/admin/keyauth/generate removed (404/405)",
                r.status_code in [404, 405],
                f"Status: {r.status_code} (expected 404 or 405)"
            )
        except Exception as e:
            runner.test("Regression: KeyAuth endpoint removed", False, f"Exception: {e}")
    
    # ========== Summary ==========
    success = runner.summary()
    return 0 if success else 1


if __name__ == "__main__":
    exit(main())
