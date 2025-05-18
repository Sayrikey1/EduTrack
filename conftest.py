import pytest  
  
from rest_framework.test import APIClient  
  
  
@pytest.fixture(scope="function")  
def api_client():  
    """  
    Fixture to provide an API client  
    :return: APIClient  
    """  
    yield APIClient()
