import requests


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

        while url:
            if method.upper() == 'GET':
                response = requests.get(url, headers=headers, params=params)
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
                # print(f"Type of json_response: {type(json_response)}")
                # print(f"json_response content: {json_response}")

                # Handle when response is a list
                if isinstance(json_response, list):
                    # print("Response is a list, extending all_results.")

                    all_results.extend(json_response)
                    url = None
                    # print(json_response)

                # Handle when response is a dictionary with possible pagination
                elif isinstance(json_response, dict):
                    url = json_response.get('next')
                    if url:
                        print(f"Fetching next page: {url}")
                        if not url.startswith("http"):
                            url = f"{self.base_url}{url}"
                        params = None  # Reset params to avoid appending them to the URL repeatedly
                    else:
                        url = None



                    if 'results' in json_response:
                        # print(f"'results' found in json_response: {type(json_response['results'])}")
                        # If 'results' is a list, extend the results
                        if isinstance(json_response['results'], list):
                            all_results.extend(json_response['results'])
                        # If 'results' is a dictionary, append the entire dictionary
                        elif isinstance(json_response['results'], dict):
                            all_results.append(json_response['results'])
                        else:
                            print("Unexpected data type for 'results'.")
                    elif 'data' in json_response:  # Assuming 'data' might be a relevant key
                        # print("Extending with 'data'.")
                        all_results.extend(json_response['data'])
                    else:
                        print("Appending entire json_response to all_results.")
                        all_results.append(json_response)  # Append the whole response if nothing else matches

                    # Check if there's a next page


            else:
                print(f"API call failed. Status code: {response.status_code}")
                response.raise_for_status()

        return all_results

