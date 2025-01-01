# behavior_analytics.py
from datetime import datetime

class UserEntityBehaviorAnalytics:
    def __init__(self):
        # Sample database of known user behaviors
        # In a real-world scenario, this would be more complex and dynamic
        self.known_behaviors = {
            'DBA707': {
                'password': 'Mercury80',
                'usual_login_times': range(9, 18),  # 9 AM to 6 PM
                'known_locations': ['127.0.0.1'],  # Known IP addresses
            },
            # ... add other users and their behaviors here
        }
        self.login_attempts = {}

    def analyze_behavior(self, user_code, password, ip_address=None):
        """
        Analyze user behavior based on the provided user_code, password, and IP address.
        This is a simulated function, and its decision is based on a sample database of known behaviors.
        """
        # Check if the user_code exists in the known_behaviors
        if user_code in self.known_behaviors:
            user_data = self.known_behaviors[user_code]

            # If password doesn't match or if the login time is unusual, return suspicious
            if password != user_data['password']:
                return "suspicious"

            current_hour = int(datetime.now().strftime('%H'))
            if current_hour not in user_data['usual_login_times']:
                return "suspicious"

            # Check if the login attempt is from a known location
            if ip_address and ip_address not in user_data['known_locations']:
                return "suspicious"

            # Check frequency of login attempts
            if user_code not in self.login_attempts:
                self.login_attempts[user_code] = datetime.now()
            else:
                last_attempt = self.login_attempts[user_code]
                current_time = datetime.now()
                if (current_time - last_attempt).seconds < 60:  # If the last attempt was less than a minute ago
                    return "suspicious"
                self.login_attempts[user_code] = current_time

            return "normal"
        else:
            # If user_code is not known, it's suspicious
            return "suspicious"

    def add_known_behavior(self, user_code, behavior_data):
        """
        Add a known behavior for a user to the database.
        """
        self.known_behaviors[user_code] = behavior_data

    def get_behavior_history(self, user_code):
        """
        Retrieve the behavior history for a specific user.
        """
        return self.known_behaviors.get(user_code, {})
