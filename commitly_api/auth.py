import requests
import time
from api_logger import logger


class CommitlyAPI:
    def __init__(self, client_id, client_secret):
        self.client_id = client_id
        self.client_secret = client_secret
        self.base_url = "https://backend.commitly.com"
        self.token_url = f"{self.base_url}/auth/token/"
        self.access_token = None
        logger.info("CommitlyAPI instance initialized", base_url=self.base_url)

    def authenticate(self):
        logger.info("Attempting authentication")
        payload = {
            'client_id': self.client_id,
            'client_secret': self.client_secret,
            'grant_type': 'client_credentials'
        }

        try:
            response = requests.post(self.token_url, data=payload)
            logger.debug("Auth response received", status_code=response.status_code)

            if response.status_code in [200, 201]:
                self.access_token = response.json().get('access_token')
                if self.access_token:
                    logger.info("Authentication successful")
                else:
                    logger.error("Access token not found in response")
                    raise ValueError("Access token not found in response")
            else:
                logger.error("Authentication failed", 
                           status_code=response.status_code, 
                           response_content=response.content)
                response.raise_for_status()
        except requests.exceptions.RequestException as e:
            logger.error("Authentication request failed", error=str(e))
            raise

    def get_headers(self):
        """
        Get the headers required for making authorized API requests.
        """
        if not self.access_token:
            logger.error("Attempted to get headers without access token")
            raise Exception("No access token found. Please authenticate first.")

        logger.debug("Generated API request headers")
        return {
            'Authorization': f'Bearer {self.access_token}',
            'Content-Type': 'application/json'
        }

    def make_api_call(self, endpoint, method='GET', data=None, params=None):
        """Make an API call to the specified endpoint with the given method, and handle pagination."""
        url = f"{self.base_url}{endpoint}"
        headers = self.get_headers()
        all_results = []
        
        logger.info("Starting API call", 
                   endpoint=endpoint, 
                   method=method, 
                   params=params)
        
        # Add page size parameter to get maximum allowed records per request
        current_params = params.copy() if params else {}
        if 'page_size' not in current_params:
            current_params['page_size'] = 100
        
        page_count = 0
        max_pages = 1000

        while url and page_count < max_pages:
            page_count += 1
            logger.debug("Making paginated request", 
                        page=page_count, 
                        url=url)
            
            try:
                if method.upper() == 'GET':
                    current_request_params = current_params if url == f"{self.base_url}{endpoint}" else None
                    response = requests.get(url, headers=headers, params=current_request_params)
                elif method.upper() == 'POST':
                    response = requests.post(url, headers=headers, json=data)
                elif method.upper() == 'PATCH':
                    response = requests.patch(url, headers=headers, json=data)
                elif method.upper() == 'DELETE':
                    response = requests.delete(url, headers=headers)
                else:
                    logger.error("Invalid HTTP method", method=method)
                    raise ValueError("Invalid HTTP method specified.")

                if response.status_code in [200, 201]:
                    json_response = response.json()

                    if isinstance(json_response, list):
                        logger.debug("Received list response", items_count=len(json_response))
                        all_results.extend(json_response)
                        break

                    elif isinstance(json_response, dict):
                        url = json_response.get('next')
                        
                        if 'results' in json_response:
                            if isinstance(json_response['results'], list):
                                logger.debug("Received paginated list response", 
                                           items_count=len(json_response['results']),
                                           has_next=bool(url))
                                all_results.extend(json_response['results'])
                            elif isinstance(json_response['results'], dict):
                                all_results.append(json_response['results'])
                        elif 'data' in json_response:
                            all_results.extend(json_response['data'])
                        else:
                            all_results.append(json_response)
                            break

                else:
                    logger.error("API call failed", 
                               status_code=response.status_code,
                               response_content=response.content)
                    response.raise_for_status()
                    
            except Exception as e:
                logger.error("Error during API call", 
                           error=str(e),
                           endpoint=endpoint,
                           method=method)
                break
                
            if url:
                time.sleep(0.1)

        if page_count >= max_pages:
            logger.warning("Reached maximum page limit", 
                         max_pages=max_pages,
                         endpoint=endpoint)

        logger.info("API call completed", 
                   total_results=len(all_results),
                   pages_processed=page_count)
        return all_results

