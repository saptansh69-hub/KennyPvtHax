#!/usr/bin/env python3
"""
Backend API Testing for KennyPvtHax - NEW FEATURES
Tests: Admin by email (ADMIN_EMAILS) and Password reset flow
"""
import requests
import json
import random
import string
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


def random_suffix():
    """Generate random suffix for test data"""
    return ''.join(random.choices(string.ascii_lowercase + string.digits, k=8))


def main():
    runner = TestRunner()
    
    print("="*80)
    print("BACKEND API TESTING - KennyPvtHax NEW FEATURES")
    print("Testing: Admin by email + Password reset flow")
    print("="*80)
    
    # ========================================================================
    # PART 1: ADMIN BY EMAIL (ADMIN_EMAILS env)
    # ========================================================================
    print("\n" + "="*80)
    print("PART 1: ADMIN BY EMAIL (ADMIN_EMAILS)")
    print("="*80)
    
    admin_email = "saptanshtesting@gmail.com"
    admin_password = "admin123456"
    admin_token = None
    
    # Test 1: Signup with admin email
    print(f"\n[1] Testing signup with admin email: {admin_email}")
    try:
        payload = {
            "name": "Admin User",
            "email": admin_email,
            "password": admin_password
        }
        r = requests.post(f"{BASE_URL}/auth/signup", json=payload, timeout=10)
        
        # If 409, user exists - try forgot/reset flow to set known password
        if r.status_code == 409:
            print(f"   User {admin_email} already exists (409)")
            print("   Attempting forgot/reset flow to set known password...")
            
            # Forgot password
            forgot_payload = {"identifier": admin_email}
            r_forgot = requests.post(f"{BASE_URL}/auth/forgot", json=forgot_payload, timeout=10)
            
            if r_forgot.status_code == 200:
                forgot_data = r_forgot.json()
                if forgot_data.get("found") and forgot_data.get("reset_token"):
                    reset_token = forgot_data["reset_token"]
                    print(f"   Got reset token: {reset_token[:20]}...")
                    
                    # Reset password
                    reset_payload = {"token": reset_token, "password": admin_password}
                    r_reset = requests.post(f"{BASE_URL}/auth/reset", json=reset_payload, timeout=10)
                    
                    if r_reset.status_code == 200:
                        print(f"   Password reset successful, now have known password")
                        r = r_reset  # Use reset response as signup response
                    else:
                        print(f"   Reset failed: {r_reset.status_code}")
                        # Try login with old password
                        login_payload = {"identifier": admin_email, "password": admin_password}
                        r = requests.post(f"{BASE_URL}/auth/login", json=login_payload, timeout=10)
                else:
                    print(f"   Forgot returned found=false or no token")
                    # Try login anyway
                    login_payload = {"identifier": admin_email, "password": admin_password}
                    r = requests.post(f"{BASE_URL}/auth/login", json=login_payload, timeout=10)
            else:
                # Try login
                login_payload = {"identifier": admin_email, "password": admin_password}
                r = requests.post(f"{BASE_URL}/auth/login", json=login_payload, timeout=10)
        
        runner.test(
            f"Signup/login with {admin_email} successful",
            r.status_code in [200, 201],
            f"Status: {r.status_code}"
        )
        
        if r.status_code in [200, 201]:
            data = r.json()
            admin_token = data.get("token")
            print(f"   Got admin token: {admin_token[:30] if admin_token else 'None'}...")
    except Exception as e:
        runner.test(f"Signup/login {admin_email}", False, f"Exception: {e}")
    
    # Test 2: GET /api/auth/me with admin email - verify is_admin=true
    if admin_token:
        print(f"\n[2] Testing GET /api/auth/me with admin email token")
        try:
            headers = {"Authorization": f"Bearer {admin_token}"}
            r = requests.get(f"{BASE_URL}/auth/me", headers=headers, timeout=10)
            
            runner.test(
                "GET /api/auth/me returns 200",
                r.status_code == 200,
                f"Status: {r.status_code}"
            )
            
            if r.status_code == 200:
                me_data = r.json()
                user = me_data.get("user", {})
                
                runner.test(
                    f"User {admin_email} has is_admin=true",
                    user.get("is_admin") == True,
                    f"is_admin: {user.get('is_admin')}, email: {user.get('email')}"
                )
        except Exception as e:
            runner.test("GET /api/auth/me for admin email", False, f"Exception: {e}")
    else:
        print("\n[2] SKIPPED: No admin token available")
    
    # Test 3: Admin endpoints work with admin email account
    if admin_token:
        print(f"\n[3] Testing GET /api/admin/stats with admin email token")
        try:
            headers = {"Authorization": f"Bearer {admin_token}"}
            r = requests.get(f"{BASE_URL}/admin/stats", headers=headers, timeout=10)
            
            runner.test(
                "GET /api/admin/stats returns 200 with admin email token",
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
            runner.test("GET /api/admin/stats with admin email", False, f"Exception: {e}")
    else:
        print("\n[3] SKIPPED: No admin token available")
    
    # Test 4: Create random non-admin user and verify admin endpoint fails (403)
    print(f"\n[4] Testing admin endpoint with non-admin user (expect 403)")
    random_email = f"nonadmin_{random_suffix()}@example.com"
    random_password = "password123"
    non_admin_token = None
    
    try:
        payload = {
            "name": "Non-Admin User",
            "email": random_email,
            "password": random_password
        }
        r = requests.post(f"{BASE_URL}/auth/signup", json=payload, timeout=10)
        
        runner.test(
            f"Signup non-admin user {random_email} successful",
            r.status_code in [200, 201],
            f"Status: {r.status_code}"
        )
        
        if r.status_code in [200, 201]:
            data = r.json()
            non_admin_token = data.get("token")
            
            # Verify is_admin=false
            headers = {"Authorization": f"Bearer {non_admin_token}"}
            r_me = requests.get(f"{BASE_URL}/auth/me", headers=headers, timeout=10)
            
            if r_me.status_code == 200:
                user = r_me.json().get("user", {})
                runner.test(
                    f"Non-admin user has is_admin=false",
                    user.get("is_admin") == False,
                    f"is_admin: {user.get('is_admin')}"
                )
            
            # Try admin endpoint - should fail with 403
            r_admin = requests.get(f"{BASE_URL}/admin/stats", headers=headers, timeout=10)
            runner.test(
                "GET /api/admin/stats with non-admin token returns 403",
                r_admin.status_code == 403,
                f"Status: {r_admin.status_code}"
            )
    except Exception as e:
        runner.test("Non-admin user test", False, f"Exception: {e}")
    
    # ========================================================================
    # PART 2: PASSWORD RESET FLOW
    # ========================================================================
    print("\n" + "="*80)
    print("PART 2: PASSWORD RESET FLOW")
    print("="*80)
    
    # Test 5: Create user for reset testing
    print(f"\n[5] Creating test user for password reset flow")
    reset_email = f"reset_test_{random_suffix()}@example.com"
    old_password = "oldpass123"
    new_password = "newpass456"
    reset_user_token = None
    
    try:
        payload = {
            "name": "Reset Test User",
            "email": reset_email,
            "password": old_password
        }
        r = requests.post(f"{BASE_URL}/auth/signup", json=payload, timeout=10)
        
        runner.test(
            f"Create user {reset_email} for reset testing",
            r.status_code in [200, 201],
            f"Status: {r.status_code}, Email: {reset_email}"
        )
        
        if r.status_code in [200, 201]:
            data = r.json()
            reset_user_token = data.get("token")
    except Exception as e:
        runner.test("Create reset test user", False, f"Exception: {e}")
    
    # Test 6: POST /api/auth/forgot with valid email - expect found=true and reset_token
    print(f"\n[6] Testing POST /api/auth/forgot with valid email")
    reset_token = None
    
    try:
        payload = {"identifier": reset_email}
        r = requests.post(f"{BASE_URL}/auth/forgot", json=payload, timeout=10)
        
        runner.test(
            "POST /api/auth/forgot returns 200",
            r.status_code == 200,
            f"Status: {r.status_code}"
        )
        
        if r.status_code == 200:
            data = r.json()
            
            runner.test(
                "forgot response has found=true",
                data.get("found") == True,
                f"found: {data.get('found')}"
            )
            
            runner.test(
                "forgot response has reset_token",
                "reset_token" in data and data.get("reset_token") is not None,
                f"reset_token present: {'reset_token' in data}, value: {data.get('reset_token', 'N/A')[:20] if data.get('reset_token') else 'None'}..."
            )
            
            reset_token = data.get("reset_token")
            print(f"   Got reset token: {reset_token[:30] if reset_token else 'None'}...")
    except Exception as e:
        runner.test("POST /api/auth/forgot valid email", False, f"Exception: {e}")
    
    # Test 7: POST /api/auth/forgot with nonexistent email - expect found=false, NO reset_token
    print(f"\n[7] Testing POST /api/auth/forgot with nonexistent email")
    nonexistent_email = f"nonexistent_{random_suffix()}@example.com"
    
    try:
        payload = {"identifier": nonexistent_email}
        r = requests.post(f"{BASE_URL}/auth/forgot", json=payload, timeout=10)
        
        runner.test(
            "POST /api/auth/forgot with nonexistent email returns 200",
            r.status_code == 200,
            f"Status: {r.status_code}"
        )
        
        if r.status_code == 200:
            data = r.json()
            
            runner.test(
                "forgot response has found=false",
                data.get("found") == False,
                f"found: {data.get('found')}"
            )
            
            runner.test(
                "forgot response has NO reset_token",
                "reset_token" not in data or data.get("reset_token") is None,
                f"reset_token in response: {'reset_token' in data}, value: {data.get('reset_token', 'N/A')}"
            )
    except Exception as e:
        runner.test("POST /api/auth/forgot nonexistent email", False, f"Exception: {e}")
    
    # Test 8: POST /api/auth/reset with valid token and new password
    if reset_token:
        print(f"\n[8] Testing POST /api/auth/reset with valid token")
        new_token_after_reset = None
        
        try:
            payload = {"token": reset_token, "password": new_password}
            r = requests.post(f"{BASE_URL}/auth/reset", json=payload, timeout=10)
            
            runner.test(
                "POST /api/auth/reset returns 200",
                r.status_code == 200,
                f"Status: {r.status_code}"
            )
            
            if r.status_code == 200:
                data = r.json()
                
                runner.test(
                    "reset response has token",
                    "token" in data and data.get("token") is not None,
                    f"token present: {'token' in data}"
                )
                
                runner.test(
                    "reset response has user",
                    "user" in data and data.get("user") is not None,
                    f"user present: {'user' in data}"
                )
                
                new_token_after_reset = data.get("token")
                
                # Verify can use new token to access /api/auth/me
                if new_token_after_reset:
                    headers = {"Authorization": f"Bearer {new_token_after_reset}"}
                    r_me = requests.get(f"{BASE_URL}/auth/me", headers=headers, timeout=10)
                    
                    runner.test(
                        "GET /api/auth/me with new token after reset works",
                        r_me.status_code == 200,
                        f"Status: {r_me.status_code}"
                    )
        except Exception as e:
            runner.test("POST /api/auth/reset valid token", False, f"Exception: {e}")
    else:
        print("\n[8] SKIPPED: No reset token available")
    
    # Test 9: Verify OLD password no longer works
    print(f"\n[9] Testing login with OLD password (should fail)")
    
    try:
        payload = {"identifier": reset_email, "password": old_password}
        r = requests.post(f"{BASE_URL}/auth/login", json=payload, timeout=10)
        
        runner.test(
            "Login with OLD password returns 401",
            r.status_code == 401,
            f"Status: {r.status_code}"
        )
    except Exception as e:
        runner.test("Login with old password", False, f"Exception: {e}")
    
    # Test 10: Verify NEW password works
    print(f"\n[10] Testing login with NEW password (should succeed)")
    
    try:
        payload = {"identifier": reset_email, "password": new_password}
        r = requests.post(f"{BASE_URL}/auth/login", json=payload, timeout=10)
        
        runner.test(
            "Login with NEW password returns 200",
            r.status_code == 200,
            f"Status: {r.status_code}"
        )
        
        if r.status_code == 200:
            data = r.json()
            runner.test(
                "Login with new password returns token",
                "token" in data and data.get("token") is not None,
                f"token present: {'token' in data}"
            )
    except Exception as e:
        runner.test("Login with new password", False, f"Exception: {e}")
    
    # Test 11: Reuse SAME reset token (should fail - already used)
    if reset_token:
        print(f"\n[11] Testing reuse of SAME reset token (expect 400)")
        
        try:
            payload = {"token": reset_token, "password": "anotherpass789"}
            r = requests.post(f"{BASE_URL}/auth/reset", json=payload, timeout=10)
            
            runner.test(
                "Reusing same reset token returns 400",
                r.status_code == 400,
                f"Status: {r.status_code}"
            )
        except Exception as e:
            runner.test("Reuse reset token", False, f"Exception: {e}")
    else:
        print("\n[11] SKIPPED: No reset token available")
    
    # Test 12: POST /api/auth/reset with bogus token (should fail)
    print(f"\n[12] Testing POST /api/auth/reset with bogus token (expect 400)")
    
    try:
        bogus_token = "bogus_token_" + random_suffix()
        payload = {"token": bogus_token, "password": "somepass123"}
        r = requests.post(f"{BASE_URL}/auth/reset", json=payload, timeout=10)
        
        runner.test(
            "Reset with bogus token returns 400",
            r.status_code == 400,
            f"Status: {r.status_code}"
        )
    except Exception as e:
        runner.test("Reset with bogus token", False, f"Exception: {e}")
    
    # Test 13: POST /api/auth/reset with password < 6 chars (should fail)
    print(f"\n[13] Testing POST /api/auth/reset with short password (expect 400)")
    
    # First get a fresh reset token
    fresh_reset_token = None
    try:
        # Create another user for this test
        short_pass_email = f"shortpass_{random_suffix()}@example.com"
        payload = {
            "name": "Short Pass User",
            "email": short_pass_email,
            "password": "initial123"
        }
        r = requests.post(f"{BASE_URL}/auth/signup", json=payload, timeout=10)
        
        if r.status_code in [200, 201]:
            # Get reset token
            forgot_payload = {"identifier": short_pass_email}
            r_forgot = requests.post(f"{BASE_URL}/auth/forgot", json=forgot_payload, timeout=10)
            
            if r_forgot.status_code == 200:
                forgot_data = r_forgot.json()
                fresh_reset_token = forgot_data.get("reset_token")
                
                if fresh_reset_token:
                    # Try reset with short password
                    reset_payload = {"token": fresh_reset_token, "password": "short"}
                    r_reset = requests.post(f"{BASE_URL}/auth/reset", json=reset_payload, timeout=10)
                    
                    runner.test(
                        "Reset with password < 6 chars returns 400",
                        r_reset.status_code == 400,
                        f"Status: {r_reset.status_code}, Password length: 5"
                    )
                else:
                    runner.test("Reset with short password", False, "Could not get reset token")
            else:
                runner.test("Reset with short password", False, f"Forgot failed: {r_forgot.status_code}")
        else:
            runner.test("Reset with short password", False, f"Signup failed: {r.status_code}")
    except Exception as e:
        runner.test("Reset with short password", False, f"Exception: {e}")
    
    # Test 14: Forgot with Telegram identifier (with and without @)
    print(f"\n[14] Testing POST /api/auth/forgot with Telegram identifier")
    
    # Create user with telegram
    tg_username = f"resettest_{random_suffix()}"
    tg_with_at = f"@{tg_username}"
    
    try:
        payload = {
            "name": "Telegram Reset User",
            "telegram": tg_with_at,
            "password": "tgpass123"
        }
        r = requests.post(f"{BASE_URL}/auth/signup", json=payload, timeout=10)
        
        runner.test(
            f"Create user with telegram {tg_with_at}",
            r.status_code in [200, 201],
            f"Status: {r.status_code}"
        )
        
        if r.status_code in [200, 201]:
            # Test forgot WITHOUT @
            print(f"   Testing forgot with telegram WITHOUT @: {tg_username}")
            forgot_payload = {"identifier": tg_username}
            r_forgot = requests.post(f"{BASE_URL}/auth/forgot", json=forgot_payload, timeout=10)
            
            runner.test(
                f"Forgot with telegram WITHOUT @ finds user",
                r_forgot.status_code == 200 and r_forgot.json().get("found") == True,
                f"Status: {r_forgot.status_code}, found: {r_forgot.json().get('found') if r_forgot.status_code == 200 else 'N/A'}"
            )
            
            # Test forgot WITH @
            print(f"   Testing forgot with telegram WITH @: {tg_with_at}")
            forgot_payload = {"identifier": tg_with_at}
            r_forgot = requests.post(f"{BASE_URL}/auth/forgot", json=forgot_payload, timeout=10)
            
            runner.test(
                f"Forgot with telegram WITH @ finds user",
                r_forgot.status_code == 200 and r_forgot.json().get("found") == True,
                f"Status: {r_forgot.status_code}, found: {r_forgot.json().get('found') if r_forgot.status_code == 200 else 'N/A'}"
            )
    except Exception as e:
        runner.test("Forgot with telegram identifier", False, f"Exception: {e}")
    
    # Print summary
    success = runner.summary()
    return 0 if success else 1


if __name__ == "__main__":
    exit(main())
