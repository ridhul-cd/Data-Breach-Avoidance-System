# behavior_analytics.py

class UserEntityBehaviorAnalytics:
    def __init__(self):
        # Sample database of known user behaviors
        # In a real-world scenario, this would be more complex and dynamic
        self.known_behaviors = {
            'DBA707': {
                'password': 'Mercury80',
                'usual_login_times': range(9, 18)  # 9 AM to 6 PM
            },
            # ... add other users and their behaviors here
        }

    def analyze_behavior(self, user_code, password):
        """
        Analyze user behavior based on the provided user_code and password.
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

            return "normal"
        else:
            # If user_code is not known, it's suspicious
            return "suspicious"
