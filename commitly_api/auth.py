import requests
import time


class CommitlyAPI:
    def __init__(self, client_id, client_secret):
        self.client_id = client_id
        self.client_secret = client_secret
        self.base_url = "https://backend.commitly.com"
        self.token_url = f"{self.base_url}/auth/token/"
        self.access_token = None

    def authenticate(self):
        payload = {
            'client_id': self.client_id,
            'client_secret': self.client_secret,
            'grant_type': 'client_credentials'
        }

        response = requests.post(self.token_url, data=payload)

        print("Response status code:", response.status_code)
        print("Response content:", response.content)  # Add this line to inspect the response content

        if response.status_code in [200, 201]:  # Treat 201 as success for now
            self.access_token = response.json().get('access_token')
            if self.access_token:
                print("Authentication successful. Access token obtained.")
            else:
                print("Access token not found in the response.")
        else:
            print(f"Failed to authenticate. Status code: {response.status_code}")
            response.raise_for_status()

    def get_headers(self):
        """
        Get the headers required for making authorized API requests.
        """
        if not self.access_token:
            raise Exception("No access token found. Please authenticate first.")

        return {
            'Authorization': f'Bearer {self.access_token}',
            'Content-Type': 'application/json'
        }

    def make_api_call(self, endpoint, method='GET', data=None, params=None):
        """Make an API call to the specified endpoint with the given method, and handle pagination."""
        url = f"{self.base_url}{endpoint}"
        headers = self.get_headers()
        all_results = []
        
        # Add page size parameter to get maximum allowed records per request
        current_params = params.copy() if params else {}
        if 'page_size' not in current_params:
            current_params['page_size'] = 100  # Maximum page size to reduce number of requests
        
        page_count = 0
        max_pages = 1000  # Safety limit to prevent infinite loops

        while url and page_count < max_pages:
            page_count += 1
            try:
                if method.upper() == 'GET':
                    # Only use params for the first request, subsequent requests use the full next URL
                    current_request_params = current_params if url == f"{self.base_url}{endpoint}" else None
                    response = requests.get(url, headers=headers, params=current_request_params)
                elif method.upper() == 'POST':
                    response = requests.post(url, headers=headers, json=data)
                elif method.upper() == 'PATCH':
                    response = requests.patch(url, headers=headers, json=data)
                elif method.upper() == 'DELETE':
                    response = requests.delete(url, headers=headers)
                else:
                    raise ValueError("Invalid HTTP method specified.")

                if response.status_code in [200, 201]:
                    json_response = response.json()

                    # Handle when response is a list
                    if isinstance(json_response, list):
                        all_results.extend(json_response)
                        break

                    # Handle when response is a dictionary with possible pagination
                    elif isinstance(json_response, dict):
                        # Get the next page URL if it exists
                        url = json_response.get('next')
                        
                        # Process the results
                        if 'results' in json_response:
                            if isinstance(json_response['results'], list):
                                all_results.extend(json_response['results'])
                            elif isinstance(json_response['results'], dict):
                                all_results.append(json_response['results'])
                        elif 'data' in json_response:
                            all_results.extend(json_response['data'])
                        else:
                            all_results.append(json_response)
                            break  # If no pagination structure found, exit after first request

                else:
                    print(f"API call failed. Status code: {response.status_code}")
                    response.raise_for_status()
                    
            except Exception as e:
                print(f"Error during API call: {str(e)}")
                break  # Exit on error to return partial results
                
            # Add a small delay between requests to avoid overwhelming the API
            if url:
                time.sleep(0.1)  # 100ms delay between requests

        if page_count >= max_pages:
            print(f"Warning: Reached maximum page limit of {max_pages}")

        return all_results

