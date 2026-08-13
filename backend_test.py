#!/usr/bin/env python3
"""
Backend API Tests for KennyPvtHax
Tests all endpoints at the external URL with /api prefix
"""

import requests
import json
import random
import string
from typing import Dict, Any

# Backend URL from frontend/.env
BASE_URL = "https://kenny-gaming-mods.preview.emergentagent.com/api"

# Test results tracking
test_results = {
    "passed": [],
    "failed": [],
    "total": 0
}


def random_string(length=8):
    """Generate random string for unique test data"""
    return ''.join(random.choices(string.ascii_lowercase + string.digits, k=length))


def log_test(name: str, passed: bool, details: str = ""):
    """Log test result"""
    test_results["total"] += 1
    status = "✅ PASS" if passed else "❌ FAIL"
    result = {"name": name, "details": details}
    
    if passed:
        test_results["passed"].append(result)
    else:
        test_results["failed"].append(result)
    
    print(f"{status}: {name}")
    if details:
        print(f"  Details: {details}")


def test_root_endpoint():
    """Test GET /api/"""
    print("\n=== Testing Root Endpoint ===")
    try:
        response = requests.get(f"{BASE_URL}/")
        if response.status_code == 200:
            data = response.json()
            if data.get("message") == "KennyPvtHax API online":
                log_test("GET /api/ returns correct message", True)
            else:
                log_test("GET /api/ returns correct message", False, f"Got: {data}")
        else:
            log_test("GET /api/ status code", False, f"Status: {response.status_code}, Body: {response.text}")
    except Exception as e:
        log_test("GET /api/ endpoint", False, f"Exception: {str(e)}")


def test_auth_signup():
    """Test POST /api/auth/signup with various scenarios"""
    print("\n=== Testing Auth Signup ===")
    
    # Test 1: Signup with email
    email = f"testuser_{random_string()}@example.com"
    password = "password123"
    try:
        response = requests.post(f"{BASE_URL}/auth/signup", json={
            "name": "Test User Email",
            "email": email,
            "password": password
        })
        if response.status_code == 200:
            data = response.json()
            if "token" in data and "user" in data:
                log_test("Signup with email", True, f"User created: {data['user'].get('email')}")
                # Store for later tests
                test_auth_signup.email_user = {"email": email, "password": password, "token": data["token"]}
            else:
                log_test("Signup with email", False, f"Missing token or user in response: {data}")
        else:
            log_test("Signup with email", False, f"Status: {response.status_code}, Body: {response.text}")
    except Exception as e:
        log_test("Signup with email", False, f"Exception: {str(e)}")
    
    # Test 2: Signup with telegram (without @)
    telegram = f"testuser_{random_string()}"
    try:
        response = requests.post(f"{BASE_URL}/auth/signup", json={
            "name": "Test User Telegram",
            "telegram": telegram,
            "password": password
        })
        if response.status_code == 200:
            data = response.json()
            if "token" in data and "user" in data:
                # Verify telegram is normalized with @
                user_telegram = data["user"].get("telegram")
                if user_telegram and user_telegram.startswith("@"):
                    log_test("Signup with telegram (normalized with @)", True, f"Telegram: {user_telegram}")
                    test_auth_signup.telegram_user = {"telegram": telegram, "password": password, "token": data["token"]}
                else:
                    log_test("Signup with telegram (normalized with @)", False, f"Telegram not normalized: {user_telegram}")
            else:
                log_test("Signup with telegram", False, f"Missing token or user: {data}")
        else:
            log_test("Signup with telegram", False, f"Status: {response.status_code}, Body: {response.text}")
    except Exception as e:
        log_test("Signup with telegram", False, f"Exception: {str(e)}")
    
    # Test 3: Signup with telegram (with @)
    telegram_with_at = f"@testuser_{random_string()}"
    try:
        response = requests.post(f"{BASE_URL}/auth/signup", json={
            "name": "Test User Telegram At",
            "telegram": telegram_with_at,
            "password": password
        })
        if response.status_code == 200:
            data = response.json()
            user_telegram = data.get("user", {}).get("telegram")
            if user_telegram == telegram_with_at:
                log_test("Signup with telegram (already has @)", True, f"Telegram: {user_telegram}")
            else:
                log_test("Signup with telegram (already has @)", False, f"Telegram changed: {user_telegram}")
        else:
            log_test("Signup with telegram (already has @)", False, f"Status: {response.status_code}")
    except Exception as e:
        log_test("Signup with telegram (already has @)", False, f"Exception: {str(e)}")
    
    # Test 4: Validation - missing both email and telegram
    try:
        response = requests.post(f"{BASE_URL}/auth/signup", json={
            "name": "Test User",
            "password": password
        })
        if response.status_code == 400:
            log_test("Signup validation: missing email and telegram returns 400", True)
        else:
            log_test("Signup validation: missing email and telegram returns 400", False, f"Status: {response.status_code}")
    except Exception as e:
        log_test("Signup validation: missing email and telegram", False, f"Exception: {str(e)}")
    
    # Test 5: Validation - password too short
    try:
        response = requests.post(f"{BASE_URL}/auth/signup", json={
            "name": "Test User",
            "email": f"short_{random_string()}@example.com",
            "password": "12345"  # Only 5 chars
        })
        if response.status_code == 400:
            log_test("Signup validation: password < 6 chars returns 400", True)
        else:
            log_test("Signup validation: password < 6 chars returns 400", False, f"Status: {response.status_code}")
    except Exception as e:
        log_test("Signup validation: password < 6 chars", False, f"Exception: {str(e)}")
    
    # Test 6: Validation - duplicate email
    if hasattr(test_auth_signup, 'email_user'):
        try:
            response = requests.post(f"{BASE_URL}/auth/signup", json={
                "name": "Duplicate User",
                "email": test_auth_signup.email_user["email"],
                "password": "password123"
            })
            if response.status_code == 409:
                log_test("Signup validation: duplicate email returns 409", True)
            else:
                log_test("Signup validation: duplicate email returns 409", False, f"Status: {response.status_code}")
        except Exception as e:
            log_test("Signup validation: duplicate email", False, f"Exception: {str(e)}")
    
    # Test 7: Validation - duplicate telegram
    if hasattr(test_auth_signup, 'telegram_user'):
        try:
            response = requests.post(f"{BASE_URL}/auth/signup", json={
                "name": "Duplicate User",
                "telegram": test_auth_signup.telegram_user["telegram"],
                "password": "password123"
            })
            if response.status_code == 409:
                log_test("Signup validation: duplicate telegram returns 409", True)
            else:
                log_test("Signup validation: duplicate telegram returns 409", False, f"Status: {response.status_code}")
        except Exception as e:
            log_test("Signup validation: duplicate telegram", False, f"Exception: {str(e)}")


def test_auth_login():
    """Test POST /api/auth/login"""
    print("\n=== Testing Auth Login ===")
    
    if not hasattr(test_auth_signup, 'email_user'):
        print("Skipping login tests - no email user created")
        return
    
    # Test 1: Login with email
    try:
        response = requests.post(f"{BASE_URL}/auth/login", json={
            "identifier": test_auth_signup.email_user["email"],
            "password": test_auth_signup.email_user["password"]
        })
        if response.status_code == 200:
            data = response.json()
            if "token" in data and "user" in data:
                log_test("Login with email", True, f"User: {data['user'].get('email')}")
            else:
                log_test("Login with email", False, f"Missing token or user: {data}")
        else:
            log_test("Login with email", False, f"Status: {response.status_code}, Body: {response.text}")
    except Exception as e:
        log_test("Login with email", False, f"Exception: {str(e)}")
    
    # Test 2: Login with telegram (without @)
    if hasattr(test_auth_signup, 'telegram_user'):
        try:
            response = requests.post(f"{BASE_URL}/auth/login", json={
                "identifier": test_auth_signup.telegram_user["telegram"],
                "password": test_auth_signup.telegram_user["password"]
            })
            if response.status_code == 200:
                data = response.json()
                if "token" in data and "user" in data:
                    log_test("Login with telegram (without @)", True)
                else:
                    log_test("Login with telegram (without @)", False, f"Missing token or user: {data}")
            else:
                log_test("Login with telegram (without @)", False, f"Status: {response.status_code}")
        except Exception as e:
            log_test("Login with telegram (without @)", False, f"Exception: {str(e)}")
        
        # Test 3: Login with telegram (with @)
        try:
            response = requests.post(f"{BASE_URL}/auth/login", json={
                "identifier": f"@{test_auth_signup.telegram_user['telegram']}",
                "password": test_auth_signup.telegram_user["password"]
            })
            if response.status_code == 200:
                data = response.json()
                if "token" in data and "user" in data:
                    log_test("Login with telegram (with @)", True)
                else:
                    log_test("Login with telegram (with @)", False, f"Missing token or user: {data}")
            else:
                log_test("Login with telegram (with @)", False, f"Status: {response.status_code}")
        except Exception as e:
            log_test("Login with telegram (with @)", False, f"Exception: {str(e)}")
    
    # Test 4: Login with wrong password
    try:
        response = requests.post(f"{BASE_URL}/auth/login", json={
            "identifier": test_auth_signup.email_user["email"],
            "password": "wrongpassword"
        })
        if response.status_code == 401:
            log_test("Login with wrong password returns 401", True)
        else:
            log_test("Login with wrong password returns 401", False, f"Status: {response.status_code}")
    except Exception as e:
        log_test("Login with wrong password", False, f"Exception: {str(e)}")


def test_auth_me():
    """Test GET /api/auth/me"""
    print("\n=== Testing Auth Me ===")
    
    if not hasattr(test_auth_signup, 'email_user'):
        print("Skipping /auth/me tests - no user created")
        return
    
    # Test 1: Get user with valid token
    try:
        headers = {"Authorization": f"Bearer {test_auth_signup.email_user['token']}"}
        response = requests.get(f"{BASE_URL}/auth/me", headers=headers)
        if response.status_code == 200:
            data = response.json()
            if "user" in data:
                log_test("GET /auth/me with valid token", True, f"User: {data['user'].get('email')}")
            else:
                log_test("GET /auth/me with valid token", False, f"Missing user in response: {data}")
        else:
            log_test("GET /auth/me with valid token", False, f"Status: {response.status_code}, Body: {response.text}")
    except Exception as e:
        log_test("GET /auth/me with valid token", False, f"Exception: {str(e)}")
    
    # Test 2: Get user without token
    try:
        response = requests.get(f"{BASE_URL}/auth/me")
        if response.status_code == 401:
            log_test("GET /auth/me without token returns 401", True)
        else:
            log_test("GET /auth/me without token returns 401", False, f"Status: {response.status_code}")
    except Exception as e:
        log_test("GET /auth/me without token", False, f"Exception: {str(e)}")


def test_orders():
    """Test POST /api/orders and GET /api/orders/me"""
    print("\n=== Testing Orders ===")
    
    # Test 1: Create order without auth (guest)
    try:
        order_data = {
            "telegram": f"buyer_{random_string()}",
            "email": f"buyer_{random_string()}@example.com",
            "method": "upi",
            "currency": "inr",
            "items": [
                {
                    "projectId": "frozen-fire",
                    "project": "Frozen Fire",
                    "planId": "weekly",
                    "plan": "Weekly",
                    "duration": "7 days",
                    "inr": 299,
                    "usd": 4
                }
            ]
        }
        response = requests.post(f"{BASE_URL}/orders", json=order_data)
        if response.status_code == 200:
            data = response.json()
            # Check for license keys
            if "keys" in data and len(data["keys"]) > 0:
                key = data["keys"][0].get("key", "")
                if key.startswith("KENNY-") and len(key.split("-")) == 4:
                    log_test("Create order without auth (guest) with license key", True, f"Key format: {key}")
                else:
                    log_test("Create order without auth (guest) with license key", False, f"Invalid key format: {key}")
            else:
                log_test("Create order without auth (guest)", False, f"No license keys generated: {data}")
            
            # Check status is "paid"
            if data.get("status") == "paid":
                log_test("Order status is 'paid'", True)
            else:
                log_test("Order status is 'paid'", False, f"Status: {data.get('status')}")
        else:
            log_test("Create order without auth", False, f"Status: {response.status_code}, Body: {response.text}")
    except Exception as e:
        log_test("Create order without auth", False, f"Exception: {str(e)}")
    
    # Test 2: Create order with auth
    if hasattr(test_auth_signup, 'email_user'):
        try:
            headers = {"Authorization": f"Bearer {test_auth_signup.email_user['token']}"}
            order_data = {
                "telegram": f"@buyer_{random_string()}",
                "email": test_auth_signup.email_user["email"],
                "method": "upi",
                "currency": "inr",
                "items": [
                    {
                        "projectId": "og-cheats",
                        "project": "OG Cheats",
                        "planId": "monthly",
                        "plan": "Monthly",
                        "duration": "30 days",
                        "inr": 999,
                        "usd": 12
                    }
                ]
            }
            response = requests.post(f"{BASE_URL}/orders", json=order_data, headers=headers)
            if response.status_code == 200:
                data = response.json()
                if data.get("user_id"):
                    log_test("Create order with auth (linked to user)", True, f"User ID: {data.get('user_id')}")
                    test_orders.auth_order_id = data.get("id")
                else:
                    log_test("Create order with auth (linked to user)", False, f"No user_id in order: {data}")
            else:
                log_test("Create order with auth", False, f"Status: {response.status_code}, Body: {response.text}")
        except Exception as e:
            log_test("Create order with auth", False, f"Exception: {str(e)}")
    
    # Test 3: Create order with empty items
    try:
        order_data = {
            "telegram": "@buyer",
            "method": "upi",
            "currency": "inr",
            "items": []
        }
        response = requests.post(f"{BASE_URL}/orders", json=order_data)
        if response.status_code == 400:
            log_test("Create order with empty items returns 400", True)
        else:
            log_test("Create order with empty items returns 400", False, f"Status: {response.status_code}")
    except Exception as e:
        log_test("Create order with empty items", False, f"Exception: {str(e)}")
    
    # Test 4: Get user's orders
    if hasattr(test_auth_signup, 'email_user'):
        try:
            headers = {"Authorization": f"Bearer {test_auth_signup.email_user['token']}"}
            response = requests.get(f"{BASE_URL}/orders/me", headers=headers)
            if response.status_code == 200:
                data = response.json()
                if "orders" in data:
                    orders = data["orders"]
                    # Check if the order we created is in the list
                    if hasattr(test_orders, 'auth_order_id'):
                        order_ids = [o.get("id") for o in orders]
                        if test_orders.auth_order_id in order_ids:
                            log_test("GET /orders/me returns user's orders", True, f"Found {len(orders)} orders")
                        else:
                            log_test("GET /orders/me returns user's orders", False, f"Created order not found in list")
                    else:
                        log_test("GET /orders/me returns orders list", True, f"Found {len(orders)} orders")
                else:
                    log_test("GET /orders/me", False, f"No orders key in response: {data}")
            else:
                log_test("GET /orders/me", False, f"Status: {response.status_code}, Body: {response.text}")
        except Exception as e:
            log_test("GET /orders/me", False, f"Exception: {str(e)}")
    
    # Test 5: Get orders without auth
    try:
        response = requests.get(f"{BASE_URL}/orders/me")
        if response.status_code == 401:
            log_test("GET /orders/me without token returns 401", True)
        else:
            log_test("GET /orders/me without token returns 401", False, f"Status: {response.status_code}")
    except Exception as e:
        log_test("GET /orders/me without token", False, f"Exception: {str(e)}")


def test_feedback():
    """Test GET /api/feedback and POST /api/feedback"""
    print("\n=== Testing Feedback ===")
    
    # Test 1: Get feedback list (should have seeded data)
    try:
        response = requests.get(f"{BASE_URL}/feedback")
        if response.status_code == 200:
            data = response.json()
            if "feedback" in data:
                feedback_list = data["feedback"]
                if len(feedback_list) >= 4:
                    # Check if all are approved
                    all_approved = all(f.get("approved") for f in feedback_list)
                    if all_approved:
                        log_test("GET /feedback returns seeded feedback (4+ items, all approved)", True, f"Found {len(feedback_list)} items")
                    else:
                        log_test("GET /feedback returns approved feedback", False, "Some feedback not approved")
                else:
                    log_test("GET /feedback returns seeded feedback", False, f"Expected 4+ items, got {len(feedback_list)}")
                
                test_feedback.initial_count = len(feedback_list)
            else:
                log_test("GET /feedback", False, f"No feedback key in response: {data}")
        else:
            log_test("GET /feedback", False, f"Status: {response.status_code}, Body: {response.text}")
    except Exception as e:
        log_test("GET /feedback", False, f"Exception: {str(e)}")
    
    # Test 2: Create feedback with valid rating
    try:
        feedback_data = {
            "name": f"TestUser_{random_string()}",
            "rating": 5,
            "message": "This is a test feedback message. Great service!"
        }
        response = requests.post(f"{BASE_URL}/feedback", json=feedback_data)
        if response.status_code == 200:
            data = response.json()
            if data.get("approved") == True:
                log_test("POST /feedback creates auto-approved feedback", True, f"ID: {data.get('id')}")
                test_feedback.created_id = data.get("id")
            else:
                log_test("POST /feedback creates feedback", False, f"Not auto-approved: {data}")
        else:
            log_test("POST /feedback", False, f"Status: {response.status_code}, Body: {response.text}")
    except Exception as e:
        log_test("POST /feedback", False, f"Exception: {str(e)}")
    
    # Test 3: Create feedback with rating out of range (< 1)
    try:
        feedback_data = {
            "name": "TestUser",
            "rating": 0,
            "message": "Invalid rating test"
        }
        response = requests.post(f"{BASE_URL}/feedback", json=feedback_data)
        if response.status_code == 422:
            log_test("POST /feedback with rating < 1 returns 422", True)
        else:
            log_test("POST /feedback with rating < 1 returns 422", False, f"Status: {response.status_code}")
    except Exception as e:
        log_test("POST /feedback with rating < 1", False, f"Exception: {str(e)}")
    
    # Test 4: Create feedback with rating out of range (> 5)
    try:
        feedback_data = {
            "name": "TestUser",
            "rating": 6,
            "message": "Invalid rating test"
        }
        response = requests.post(f"{BASE_URL}/feedback", json=feedback_data)
        if response.status_code == 422:
            log_test("POST /feedback with rating > 5 returns 422", True)
        else:
            log_test("POST /feedback with rating > 5 returns 422", False, f"Status: {response.status_code}")
    except Exception as e:
        log_test("POST /feedback with rating > 5", False, f"Exception: {str(e)}")
    
    # Test 5: Verify new feedback appears in list
    if hasattr(test_feedback, 'created_id') and hasattr(test_feedback, 'initial_count'):
        try:
            response = requests.get(f"{BASE_URL}/feedback")
            if response.status_code == 200:
                data = response.json()
                feedback_list = data.get("feedback", [])
                new_count = len(feedback_list)
                if new_count > test_feedback.initial_count:
                    # Check if our feedback is in the list
                    feedback_ids = [f.get("id") for f in feedback_list]
                    if test_feedback.created_id in feedback_ids:
                        log_test("New feedback appears in GET /feedback list", True)
                    else:
                        log_test("New feedback appears in GET /feedback list", False, "Created feedback not found")
                else:
                    log_test("New feedback appears in GET /feedback list", False, f"Count didn't increase: {test_feedback.initial_count} -> {new_count}")
            else:
                log_test("Verify new feedback in list", False, f"Status: {response.status_code}")
        except Exception as e:
            log_test("Verify new feedback in list", False, f"Exception: {str(e)}")


def print_summary():
    """Print test summary"""
    print("\n" + "="*60)
    print("TEST SUMMARY")
    print("="*60)
    print(f"Total Tests: {test_results['total']}")
    print(f"Passed: {len(test_results['passed'])}")
    print(f"Failed: {len(test_results['failed'])}")
    print(f"Success Rate: {len(test_results['passed'])/test_results['total']*100:.1f}%")
    
    if test_results['failed']:
        print("\n" + "="*60)
        print("FAILED TESTS:")
        print("="*60)
        for test in test_results['failed']:
            print(f"\n❌ {test['name']}")
            if test['details']:
                print(f"   {test['details']}")
    
    print("\n" + "="*60)


if __name__ == "__main__":
    print("="*60)
    print("KennyPvtHax Backend API Tests")
    print(f"Testing: {BASE_URL}")
    print("="*60)
    
    # Run all tests in order
    test_root_endpoint()
    test_auth_signup()
    test_auth_login()
    test_auth_me()
    test_orders()
    test_feedback()
    
    # Print summary
    print_summary()
    
    # Exit with appropriate code
    exit(0 if len(test_results['failed']) == 0 else 1)
