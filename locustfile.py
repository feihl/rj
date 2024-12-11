from locust import HttpUser, task, between

class MyUser(HttpUser):
    wait_time = between(1,2)
    
    @task
    def get_all_rooms(self):
        """GET request to fetch all rooms."""
        self.client.get("/rooms")