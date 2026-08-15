#!/usr/bin/env python3
"""
Backend API Testing for KennyPvtHax
Tests new/changed endpoints: config, admin access, orders with planId, feedback with images
"""
import requests
import json
import base64
from typing import Dict, Optional

# Backend URL from frontend/.env
BASE_URL = "https://kenny-gaming-mods.preview.emergentagent.com/api"

class TestRunner:
    def __init__(self):
        self.passed = 0
        self.failed = 0
        self.tests = []
        
    def test(self, name: str, condition: bool, details: str = ""):
        """Record test result"""
        if condition:
            self.passed += 1
            status = "✅ PASS"
        else:
            self.failed += 1
            status = "❌ FAIL"
        
        result = f"{status}: {name}"
        if details:
            result += f"\n   Details: {details}"
        self.tests.append(result)
        print(result)
        
    def summary(self):
        """Print test summary"""
        total = self.passed + self.failed
        print("\n" + "="*80)
        print(f"TEST SUMMARY: {self.passed}/{total} passed")
        print("="*80)
        for test in self.tests:
            print(test)
        print("="*80)
        return self.failed == 0


def main():
    runner = TestRunner()
    
    print("="*80)
    print("BACKEND API TESTING - KennyPvtHax")
    print("="*80)
    
    # Test 1: GET /api/config
    print("\n[1] Testing GET /api/config")
    try:
        r = requests.get(f"{BASE_URL}/config", timeout=10)
        runner.test(
            "GET /api/config returns 200",
            r.status_code == 200,
            f"Status: {r.status_code}"
        )
        
        if r.status_code == 200:
            data = r.json()
            runner.test(
                "config.keyauth_enabled is false",
                data.get("keyauth_enabled") == False,
                f"keyauth_enabled: {data.get('keyauth_enabled')}"
            )
            runner.test(
                "config.telegram_enabled is false",
                data.get("telegram_enabled") == False,
                f"telegram_enabled: {data.get('telegram_enabled')}"
            )
    except Exception as e:
        runner.test("GET /api/config", False, f"Exception: {e}")
    
    # Test 2: Admin user signup with @CrimeCell
    print("\n[2] Testing Admin Access Control - Signup with @CrimeCell")
    admin_token = None
    admin_user_id = None
    try:
        payload = {
            "name": "Admin User",
            "telegram": "@CrimeCell",
            "password": "admin123456"
        }
        r = requests.post(f"{BASE_URL}/auth/signup", json=payload, timeout=10)
        
        # If 409, user exists, try login
        if r.status_code == 409:
            print("   Admin user exists, attempting login...")
            login_payload = {"identifier": "@CrimeCell", "password": "admin123456"}
            r = requests.post(f"{BASE_URL}/auth/login", json=login_payload, timeout=10)
        
        runner.test(
            "Admin signup/login successful",
            r.status_code in [200, 201],
            f"Status: {r.status_code}"
        )
        
        if r.status_code in [200, 201]:
            data = r.json()
            admin_token = data.get("token")
            admin_user = data.get("user")
            admin_user_id = admin_user.get("id") if admin_user else None
            
            # Test GET /api/auth/me with admin token
            headers = {"Authorization": f"Bearer {admin_token}"}
            r_me = requests.get(f"{BASE_URL}/auth/me", headers=headers, timeout=10)
            
            runner.test(
                "GET /api/auth/me returns 200 for admin",
                r_me.status_code == 200,
                f"Status: {r_me.status_code}"
            )
            
            if r_me.status_code == 200:
                me_data = r_me.json()
                user = me_data.get("user", {})
                runner.test(
                    "Admin user has is_admin=true",
                    user.get("is_admin") == True,
                    f"is_admin: {user.get('is_admin')}, telegram: {user.get('telegram')}"
                )
    except Exception as e:
        runner.test("Admin user setup", False, f"Exception: {e}")
    
    # Test 3: Normal user signup (not admin)
    print("\n[3] Testing Normal User - Should NOT be admin")
    normal_token = None
    try:
        payload = {
            "name": "Normal User",
            "email": "normaluser@example.com",
            "password": "normal123456"
        }
        r = requests.post(f"{BASE_URL}/auth/signup", json=payload, timeout=10)
        
        # If 409, user exists, try login
        if r.status_code == 409:
            print("   Normal user exists, attempting login...")
            login_payload = {"identifier": "normaluser@example.com", "password": "normal123456"}
            r = requests.post(f"{BASE_URL}/auth/login", json=login_payload, timeout=10)
        
        runner.test(
            "Normal user signup/login successful",
            r.status_code in [200, 201],
            f"Status: {r.status_code}"
        )
        
        if r.status_code in [200, 201]:
            data = r.json()
            normal_token = data.get("token")
            
            # Test GET /api/auth/me with normal token
            headers = {"Authorization": f"Bearer {normal_token}"}
            r_me = requests.get(f"{BASE_URL}/auth/me", headers=headers, timeout=10)
            
            if r_me.status_code == 200:
                me_data = r_me.json()
                user = me_data.get("user", {})
                runner.test(
                    "Normal user has is_admin=false",
                    user.get("is_admin") == False,
                    f"is_admin: {user.get('is_admin')}, email: {user.get('email')}"
                )
    except Exception as e:
        runner.test("Normal user setup", False, f"Exception: {e}")
    
    # Test 4: Admin endpoints with admin token
    if admin_token:
        print("\n[4] Testing Admin Endpoints with Admin Token")
        headers = {"Authorization": f"Bearer {admin_token}"}
        
        # GET /api/admin/stats
        try:
            r = requests.get(f"{BASE_URL}/admin/stats", headers=headers, timeout=10)
            runner.test(
                "GET /api/admin/stats returns 200",
                r.status_code == 200,
                f"Status: {r.status_code}"
            )
            
            if r.status_code == 200:
                stats = r.json()
                required_fields = ["orders", "users", "feedback", "keys_generated", "revenue_inr", "revenue_usd", "delivered"]
                has_all = all(field in stats for field in required_fields)
                runner.test(
                    "admin/stats has all required fields",
                    has_all,
                    f"Fields: {list(stats.keys())}"
                )
        except Exception as e:
            runner.test("GET /api/admin/stats", False, f"Exception: {e}")
        
        # GET /api/admin/orders
        try:
            r = requests.get(f"{BASE_URL}/admin/orders", headers=headers, timeout=10)
            runner.test(
                "GET /api/admin/orders returns 200",
                r.status_code == 200,
                f"Status: {r.status_code}"
            )
            
            if r.status_code == 200:
                data = r.json()
                runner.test(
                    "admin/orders returns orders array",
                    "orders" in data and isinstance(data["orders"], list),
                    f"Has 'orders' key: {'orders' in data}, is list: {isinstance(data.get('orders'), list)}"
                )
        except Exception as e:
            runner.test("GET /api/admin/orders", False, f"Exception: {e}")
        
        # GET /api/admin/feedback
        try:
            r = requests.get(f"{BASE_URL}/admin/feedback", headers=headers, timeout=10)
            runner.test(
                "GET /api/admin/feedback returns 200",
                r.status_code == 200,
                f"Status: {r.status_code}"
            )
            
            if r.status_code == 200:
                data = r.json()
                runner.test(
                    "admin/feedback returns feedback array",
                    "feedback" in data and isinstance(data["feedback"], list),
                    f"Has 'feedback' key: {'feedback' in data}, is list: {isinstance(data.get('feedback'), list)}"
                )
        except Exception as e:
            runner.test("GET /api/admin/feedback", False, f"Exception: {e}")
    else:
        print("\n[4] SKIPPED: Admin endpoints (no admin token)")
    
    # Test 5: Admin endpoints with non-admin token (should return 403)
    if normal_token:
        print("\n[5] Testing Admin Endpoints with Non-Admin Token (expect 403)")
        headers = {"Authorization": f"Bearer {normal_token}"}
        
        try:
            r = requests.get(f"{BASE_URL}/admin/stats", headers=headers, timeout=10)
            runner.test(
                "GET /api/admin/stats with non-admin token returns 403",
                r.status_code == 403,
                f"Status: {r.status_code}"
            )
        except Exception as e:
            runner.test("admin/stats with non-admin token", False, f"Exception: {e}")
        
        try:
            r = requests.get(f"{BASE_URL}/admin/orders", headers=headers, timeout=10)
            runner.test(
                "GET /api/admin/orders with non-admin token returns 403",
                r.status_code == 403,
                f"Status: {r.status_code}"
            )
        except Exception as e:
            runner.test("admin/orders with non-admin token", False, f"Exception: {e}")
        
        try:
            r = requests.get(f"{BASE_URL}/admin/feedback", headers=headers, timeout=10)
            runner.test(
                "GET /api/admin/feedback with non-admin token returns 403",
                r.status_code == 403,
                f"Status: {r.status_code}"
            )
        except Exception as e:
            runner.test("admin/feedback with non-admin token", False, f"Exception: {e}")
    else:
        print("\n[5] SKIPPED: Non-admin access tests (no normal token)")
    
    # Test 6: Admin endpoints without token (should return 403)
    print("\n[6] Testing Admin Endpoints without Token (expect 403)")
    try:
        r = requests.get(f"{BASE_URL}/admin/stats", timeout=10)
        runner.test(
            "GET /api/admin/stats without token returns 403",
            r.status_code == 403,
            f"Status: {r.status_code}"
        )
    except Exception as e:
        runner.test("admin/stats without token", False, f"Exception: {e}")
    
    # Test 7: DELETE /api/admin/feedback/{id} as admin
    if admin_token:
        print("\n[7] Testing DELETE /api/admin/feedback/{id} as Admin")
        headers = {"Authorization": f"Bearer {admin_token}"}
        
        # First create a feedback to delete
        try:
            feedback_payload = {
                "name": "Test Feedback for Deletion",
                "rating": 5,
                "message": "This feedback will be deleted"
            }
            r = requests.post(f"{BASE_URL}/feedback", json=feedback_payload, headers=headers, timeout=10)
            
            if r.status_code in [200, 201]:
                feedback_data = r.json()
                feedback_id = feedback_data.get("id")
                
                runner.test(
                    "Created test feedback for deletion",
                    feedback_id is not None,
                    f"Feedback ID: {feedback_id}"
                )
                
                # Now delete it
                r_del = requests.delete(f"{BASE_URL}/admin/feedback/{feedback_id}", headers=headers, timeout=10)
                runner.test(
                    "DELETE /api/admin/feedback/{id} returns 200",
                    r_del.status_code == 200,
                    f"Status: {r_del.status_code}"
                )
                
                # Verify it's gone from GET /api/feedback
                r_list = requests.get(f"{BASE_URL}/feedback", timeout=10)
                if r_list.status_code == 200:
                    feedback_list = r_list.json().get("feedback", [])
                    deleted = not any(f.get("id") == feedback_id for f in feedback_list)
                    runner.test(
                        "Deleted feedback not in GET /api/feedback",
                        deleted,
                        f"Feedback ID {feedback_id} found in list: {not deleted}"
                    )
            else:
                runner.test("Create feedback for deletion", False, f"Status: {r.status_code}")
        except Exception as e:
            runner.test("DELETE feedback test", False, f"Exception: {e}")
    else:
        print("\n[7] SKIPPED: Delete feedback test (no admin token)")
    
    # Test 8: POST /api/admin/keyauth/generate as admin (expect 400 - not configured)
    if admin_token:
        print("\n[8] Testing POST /api/admin/keyauth/generate as Admin (expect 400)")
        headers = {"Authorization": f"Bearer {admin_token}"}
        
        try:
            payload = {"expiry_days": 7, "amount": 1, "note": "test"}
            r = requests.post(f"{BASE_URL}/admin/keyauth/generate", json=payload, headers=headers, timeout=10)
            runner.test(
                "POST /api/admin/keyauth/generate returns 400 (not configured)",
                r.status_code == 400,
                f"Status: {r.status_code}, Response: {r.text[:100]}"
            )
            
            if r.status_code == 400:
                data = r.json()
                has_detail = "detail" in data and "KeyAuth" in data.get("detail", "")
                runner.test(
                    "Error message mentions KeyAuth not configured",
                    has_detail,
                    f"Detail: {data.get('detail', 'N/A')}"
                )
        except Exception as e:
            runner.test("POST /api/admin/keyauth/generate", False, f"Exception: {e}")
    else:
        print("\n[8] SKIPPED: KeyAuth generate test (no admin token)")
    
    # Test 9: POST /api/admin/keyauth/generate as non-admin (expect 403)
    if normal_token:
        print("\n[9] Testing POST /api/admin/keyauth/generate as Non-Admin (expect 403)")
        headers = {"Authorization": f"Bearer {normal_token}"}
        
        try:
            payload = {"expiry_days": 7, "amount": 1, "note": "test"}
            r = requests.post(f"{BASE_URL}/admin/keyauth/generate", json=payload, headers=headers, timeout=10)
            runner.test(
                "POST /api/admin/keyauth/generate with non-admin returns 403",
                r.status_code == 403,
                f"Status: {r.status_code}"
            )
        except Exception as e:
            runner.test("keyauth/generate with non-admin", False, f"Exception: {e}")
    else:
        print("\n[9] SKIPPED: KeyAuth non-admin test (no normal token)")
    
    # Test 10: Orders with planId values and key fallback
    print("\n[10] Testing POST /api/orders with planId values (guest)")
    try:
        order_payload = {
            "telegram": "@testbuyer123",
            "email": "testbuyer@example.com",
            "method": "upi",
            "currency": "inr",
            "items": [
                {
                    "projectId": "frozen-fire",
                    "project": "Frozen Fire",
                    "planId": "1day",
                    "plan": "1 Day",
                    "duration": "1 day",
                    "inr": 99,
                    "usd": 1
                },
                {
                    "projectId": "og-cheats",
                    "project": "OG Cheats",
                    "planId": "7day",
                    "plan": "7 Days",
                    "duration": "7 days",
                    "inr": 499,
                    "usd": 6
                },
                {
                    "projectId": "kenny-admin",
                    "project": "Kenny Admin",
                    "planId": "month",
                    "plan": "1 Month",
                    "duration": "30 days",
                    "inr": 1499,
                    "usd": 18
                },
                {
                    "projectId": "test-admin",
                    "project": "Test Admin",
                    "planId": "admin-week",
                    "plan": "Admin Week",
                    "duration": "7 days",
                    "inr": 699,
                    "usd": 8
                }
            ]
        }
        
        r = requests.post(f"{BASE_URL}/orders", json=order_payload, timeout=10)
        runner.test(
            "POST /api/orders with planId values returns 200",
            r.status_code in [200, 201],
            f"Status: {r.status_code}"
        )
        
        if r.status_code in [200, 201]:
            order = r.json()
            
            runner.test(
                "Order status is 'paid'",
                order.get("status") == "paid",
                f"Status: {order.get('status')}"
            )
            
            runner.test(
                "Order has 4 keys",
                len(order.get("keys", [])) == 4,
                f"Keys count: {len(order.get('keys', []))}"
            )
            
            # Check each key
            keys = order.get("keys", [])
            all_local = all(k.get("source") == "local" for k in keys)
            runner.test(
                "All keys have source='local' (KeyAuth disabled)",
                all_local,
                f"Sources: {[k.get('source') for k in keys]}"
            )
            
            all_kenny_format = all(k.get("key", "").startswith("KENNY-") for k in keys)
            runner.test(
                "All keys have KENNY-XXXXXX-XXXXXX format",
                all_kenny_format,
                f"Keys: {[k.get('key')[:20] for k in keys]}"
            )
            
            runner.test(
                "Order delivered is false (Telegram not configured)",
                order.get("delivered") == False,
                f"Delivered: {order.get('delivered')}"
            )
    except Exception as e:
        runner.test("POST /api/orders with planId", False, f"Exception: {e}")
    
    # Test 11: Orders with authenticated token
    if normal_token:
        print("\n[11] Testing POST /api/orders with authenticated token")
        headers = {"Authorization": f"Bearer {normal_token}"}
        
        try:
            order_payload = {
                "telegram": "@authedbuyer",
                "email": "authed@example.com",
                "method": "upi",
                "currency": "inr",
                "items": [
                    {
                        "projectId": "test-project",
                        "project": "Test Project",
                        "planId": "7day",
                        "plan": "7 Days",
                        "duration": "7 days",
                        "inr": 299,
                        "usd": 4
                    }
                ]
            }
            
            r = requests.post(f"{BASE_URL}/orders", json=order_payload, headers=headers, timeout=10)
            runner.test(
                "POST /api/orders with auth token returns 200",
                r.status_code in [200, 201],
                f"Status: {r.status_code}"
            )
            
            if r.status_code in [200, 201]:
                order = r.json()
                
                # Verify order is retrievable via /api/orders/me
                r_me = requests.get(f"{BASE_URL}/orders/me", headers=headers, timeout=10)
                if r_me.status_code == 200:
                    my_orders = r_me.json().get("orders", [])
                    order_found = any(o.get("id") == order.get("id") for o in my_orders)
                    runner.test(
                        "Order retrievable via GET /api/orders/me",
                        order_found,
                        f"Order ID {order.get('id')} found: {order_found}"
                    )
        except Exception as e:
            runner.test("POST /api/orders with auth", False, f"Exception: {e}")
    else:
        print("\n[11] SKIPPED: Authenticated order test (no normal token)")
    
    # Test 12: Feedback with valid image (base64 data URL)
    print("\n[12] Testing POST /api/feedback with valid image")
    try:
        # Create a small base64 image (1x1 red pixel PNG)
        small_png = "iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAADUlEQVR42mP8z8DwHwAFBQIAX8jx0gAAAABJRU5ErkJggg=="
        image_data_url = f"data:image/png;base64,{small_png}"
        
        feedback_payload = {
            "name": "Image Tester",
            "rating": 5,
            "message": "Testing feedback with image",
            "image": image_data_url
        }
        
        r = requests.post(f"{BASE_URL}/feedback", json=feedback_payload, timeout=10)
        runner.test(
            "POST /api/feedback with valid image returns 200",
            r.status_code in [200, 201],
            f"Status: {r.status_code}"
        )
        
        if r.status_code in [200, 201]:
            feedback = r.json()
            
            runner.test(
                "Feedback image field is populated",
                feedback.get("image") is not None and feedback.get("image").startswith("data:image"),
                f"Image starts with 'data:image': {str(feedback.get('image', ''))[:30]}"
            )
            
            # Verify it appears in GET /api/feedback
            r_list = requests.get(f"{BASE_URL}/feedback", timeout=10)
            if r_list.status_code == 200:
                feedback_list = r_list.json().get("feedback", [])
                found = any(f.get("id") == feedback.get("id") for f in feedback_list)
                runner.test(
                    "Feedback with image appears in GET /api/feedback",
                    found,
                    f"Feedback ID {feedback.get('id')} found: {found}"
                )
    except Exception as e:
        runner.test("POST /api/feedback with image", False, f"Exception: {e}")
    
    # Test 13: Feedback with invalid image (not data:image)
    print("\n[13] Testing POST /api/feedback with invalid image format")
    try:
        feedback_payload = {
            "name": "Invalid Image Tester",
            "rating": 4,
            "message": "Testing feedback with invalid image",
            "image": "notanimage"
        }
        
        r = requests.post(f"{BASE_URL}/feedback", json=feedback_payload, timeout=10)
        runner.test(
            "POST /api/feedback with invalid image returns 200",
            r.status_code in [200, 201],
            f"Status: {r.status_code}"
        )
        
        if r.status_code in [200, 201]:
            feedback = r.json()
            
            runner.test(
                "Feedback image saved as null (invalid format)",
                feedback.get("image") is None,
                f"Image value: {feedback.get('image')}"
            )
    except Exception as e:
        runner.test("POST /api/feedback with invalid image", False, f"Exception: {e}")
    
    # Test 14: Feedback with rating out of range
    print("\n[14] Testing POST /api/feedback with rating out of range")
    
    # Test rating = 0 (below range)
    try:
        feedback_payload = {
            "name": "Rating Test",
            "rating": 0,
            "message": "Testing rating validation"
        }
        
        r = requests.post(f"{BASE_URL}/feedback", json=feedback_payload, timeout=10)
        runner.test(
            "POST /api/feedback with rating=0 returns 422",
            r.status_code == 422,
            f"Status: {r.status_code}"
        )
    except Exception as e:
        runner.test("POST /api/feedback rating=0", False, f"Exception: {e}")
    
    # Test rating = 6 (above range)
    try:
        feedback_payload = {
            "name": "Rating Test",
            "rating": 6,
            "message": "Testing rating validation"
        }
        
        r = requests.post(f"{BASE_URL}/feedback", json=feedback_payload, timeout=10)
        runner.test(
            "POST /api/feedback with rating=6 returns 422",
            r.status_code == 422,
            f"Status: {r.status_code}"
        )
    except Exception as e:
        runner.test("POST /api/feedback rating=6", False, f"Exception: {e}")
    
    # Print summary
    success = runner.summary()
    return 0 if success else 1


if __name__ == "__main__":
    exit(main())
