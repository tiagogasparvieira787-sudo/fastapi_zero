from locust import HttpUser, between, task


class FastAPIZero_User(HttpUser):
    wait_time = between(1, 2)

    @task
    def get_root(self):
        self.client.get('/')
