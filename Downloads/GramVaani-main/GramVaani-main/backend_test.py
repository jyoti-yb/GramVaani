import requests
import sys
import json
from datetime import datetime

class SNSAuthAPITester:
    def __init__(self, base_url="https://sns-phone-auth.preview.emergentagent.com"):
        self.base_url = base_url
        self.token = None
        self.tests_run = 0
        self.tests_passed = 0
        self.session_id = None

    def run_test(self, name, method, endpoint, expected_status, data=None, params=None):
        """Run a single API test"""
        url = f"{self.base_url}/{endpoint}" if not endpoint.startswith('http') else endpoint
        headers = {'Content-Type': 'application/json'}
        if self.token:
            headers['Authorization'] = f'Bearer {self.token}'

        self.tests_run += 1
        print(f"\n🔍 Testing {name}...")
        print(f"   URL: {url}")
        if data:
            print(f"   Data: {json.dumps(data, indent=2)}")
        
        try:
            if method == 'GET':
                response = requests.get(url, headers=headers, params=params, timeout=10)
            elif method == 'POST':
                response = requests.post(url, json=data, headers=headers, timeout=10)

            print(f"   Response Status: {response.status_code}")
            
            try:
                response_data = response.json()
                print(f"   Response Body: {json.dumps(response_data, indent=2)}")
            except:
                print(f"   Response Body (text): {response.text}")
                response_data = {}

            success = response.status_code == expected_status
            if success:
                self.tests_passed += 1
                print(f"✅ Passed - Status: {response.status_code}")
            else:
                print(f"❌ Failed - Expected {expected_status}, got {response.status_code}")

            return success, response_data

        except Exception as e:
            print(f"❌ Failed - Error: {str(e)}")
            return False, {}

    def test_health_endpoint(self):
        """Test health endpoint - try both /health and /api/health"""
        # Try /api/health first (per Kubernetes ingress rules)
        success, response = self.run_test(
            "Health Check (/api/health)",
            "GET",
            "api/health",
            200
        )
        
        if not success:
            # Fallback to /health
            success, response = self.run_test(
                "Health Check (/health)",
                "GET",
                "health",
                200
            )
        
        return success

    def test_phone_validation_valid(self):
        """Test OTP request with valid phone number"""
        test_phone = "+919876543210"  # Valid format
        success, response = self.run_test(
            f"Request OTP - Valid Phone ({test_phone})",
            "POST",
            "api/request-otp",
            200,
            data={"phone": test_phone}
        )
        
        if success and 'session_id' in response:
            self.session_id = response['session_id']
            print(f"   Session ID received: {self.session_id}")
        
        return success

    def test_phone_validation_invalid(self):
        """Test OTP request with invalid phone numbers"""
        invalid_phones = [
            "919876543210",      # Missing +
            "+91987654321",      # Too short
            "+9198765432101",    # Too long
            "+919876543abc",     # Contains letters
            "+919876543210 ",    # Contains space
            "+91587654321",      # Invalid prefix (5)
            "",                  # Empty
            "abc"                # Invalid format
        ]
        
        all_failed_as_expected = True
        
        for phone in invalid_phones:
            success, response = self.run_test(
                f"Request OTP - Invalid Phone ({phone})",
                "POST",
                "api/request-otp",
                422,  # Validation error expected
                data={"phone": phone}
            )
            
            # For invalid phone numbers, we expect failure (success = False for our test)
            if success:  # If API returned 422, that's what we wanted
                print(f"✅ Correctly rejected invalid phone: {phone}")
            else:
                print(f"❌ Failed to reject invalid phone: {phone}")
                all_failed_as_expected = False
        
        return all_failed_as_expected

    def test_location_endpoint(self):
        """Test location endpoint"""
        success, response = self.run_test(
            "Location Detection",
            "GET",
            "api/location",
            200
        )
        return success

    def test_reverse_geocode(self):
        """Test reverse geocode endpoint"""
        success, response = self.run_test(
            "Reverse Geocoding",
            "POST",
            "api/reverse-geocode",
            200,
            data={
                "latitude": 28.6139,
                "longitude": 77.2090
            }
        )
        return success

def main():
    """Main test execution"""
    print("🚀 Starting SNS Phone Authentication API Tests")
    print("=" * 50)
    
    # Setup
    tester = SNSAuthAPITester()
    
    # Run tests
    print("\n📋 BACKEND API TESTS")
    print("-" * 30)
    
    # Basic health check
    health_ok = tester.test_health_endpoint()
    if not health_ok:
        print("❌ Health check failed, stopping critical tests")
        return 1
    
    # Test location endpoints
    tester.test_location_endpoint()
    tester.test_reverse_geocode()
    
    # Test phone validation - valid
    valid_phone_ok = tester.test_phone_validation_valid()
    
    # Test phone validation - invalid (should be rejected)
    invalid_phone_ok = tester.test_phone_validation_invalid()
    
    # Print results
    print("\n" + "=" * 50)
    print(f"📊 RESULTS: {tester.tests_passed}/{tester.tests_run} tests passed")
    
    critical_tests = [health_ok, valid_phone_ok]
    critical_passed = sum(critical_tests)
    
    print(f"🔥 Critical Tests: {critical_passed}/{len(critical_tests)} passed")
    
    if critical_passed < len(critical_tests):
        print("❌ CRITICAL BACKEND ISSUES FOUND")
        return 1
    else:
        print("✅ BACKEND CORE FUNCTIONALITY WORKING")
        return 0

if __name__ == "__main__":
    sys.exit(main())