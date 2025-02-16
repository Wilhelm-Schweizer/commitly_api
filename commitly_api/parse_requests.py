import auth




import pandas as pd
pd.set_option('display.width', 400)
pd.set_option('display.max_columns', None)
pd.set_option('display.max_rows', None)


def get_categories(api):
    # Initialize data to avoid UnboundLocalError
    data = []

    # Example of making a GET request to fetch company categories
    try:
        data = api.make_api_call("/categories/")
        # print("API call returned data: ", data)
    except Exception as e:
        print(f"Error during API call: {e}")
        return None  # Exit the function if an error occurs

    if isinstance(data, list):
        # Convert the data into a pandas DataFrame
        df = pd.DataFrame(data)

        # Ensure the 'parent' key exists in the DataFrame
        if 'parent' in df.columns:
            # print("Processing 'parent' field...")
            # print("Sample 'parent' data: ", df['parent'].head())

            # Handle cases where 'parent' might be a dictionary or None
            df['parent_id'] = df['parent'].apply(lambda x: x.get('id') if isinstance(x, dict) else None)
            df['parent_name'] = df['parent'].apply(lambda x: x.get('name') if isinstance(x, dict) else None)

            # Drop the original 'parent' column
            df = df.drop(columns=['parent'])

        # print("Final DataFrame: ")
        # print(df)
        return df
    else:
        print("Unexpected data structure. Expected a list of categories.")
        return None
# get_categories(api)

def get_invoices(api, start_date=None, end_date=None, modified_since=None, page_size=None):
    """
    Fetch invoices with optional date filtering and pagination
    
    Args:
        api: CommitlyAPI instance
        start_date: Optional ISO format date string for filtering invoices after this date
        end_date: Optional ISO format date string for filtering invoices before this date
        modified_since: Optional ISO format date string for filtering invoices modified after this date
        page_size: Optional integer for number of records per page
    """
    params = {}
    if start_date:
        params['from'] = start_date
    if end_date:
        params['to'] = end_date
    if modified_since:
        params['modified_since'] = modified_since
    if page_size:
        params['page_size'] = page_size

    try:
        data = api.make_api_call("/invoices/", params=params)
    except Exception as e:
        print(f"Error during API call: {e}")
        return pd.DataFrame()  # Return empty DataFrame on error

    invoices = []
    for item in data:
        if isinstance(item, dict):
            if 'invoices' in item:
                invoices.extend(item['invoices'])
            else:
                invoices.append(item)

    return pd.DataFrame(invoices)

# get_invoices(api)

def get_banks(api, start_date=None, end_date=None, page_size=None):
    """
    Fetch bank data with optional date filtering and pagination
    
    Args:
        api: CommitlyAPI instance
        start_date: Optional ISO format date string for filtering bank data after this date
        end_date: Optional ISO format date string for filtering bank data before this date
        page_size: Optional integer for number of records per page
    """
    params = {}
    if start_date:
        params['from'] = start_date
    if end_date:
        params['to'] = end_date
    if page_size:
        params['page_size'] = page_size

    try:
        data = api.make_api_call("/banks/", params=params)
    except Exception as e:
        print(f"Error during API call: {e}")
        return pd.DataFrame()  # Return empty DataFrame on error

    flattened_data = []
    for result in data:
        for account in result['accounts']:
            flattened_record = {
                'bank_connection_id': result['id'],
                'bank_name': result['name'],
                'bank_bic': result['bic'],
                'account_id': account['id'],
                'account_name': account['name'],
                'account_iban': account['iban'],
                'currency': account['currency'],
                'balance': account['balance'],
                'transaction_count': account['transaction_count'],
                'date_created': account['date_created'],
                'date_updated': account['date_updated'],
                'status': account['status'],
                'last_successful_update': account['last_successful_update'],
                'last_update_attempt': account['last_update_attempt']
            }
            flattened_data.append(flattened_record)

    return pd.DataFrame(flattened_data)

# get_banks(api)


def get_transactions(api, start_date=None, end_date=None, modified_since=None, page_size=None):
    """
    Fetch transactions with optional date filtering and pagination
    
    Args:
        api: CommitlyAPI instance
        start_date: Optional ISO format date string for filtering transactions after this date
        end_date: Optional ISO format date string for filtering transactions before this date
        modified_since: Optional ISO format date string for filtering transactions modified after this date
        page_size: Optional integer for number of records per page
    """
    params = {}
    if start_date:
        params['from'] = start_date
    if end_date:
        params['to'] = end_date
    if modified_since:
        params['modified_since'] = modified_since
    if page_size:
        params['page_size'] = page_size

    try:
        data = api.make_api_call("/transactions/", params=params)
    except Exception as e:
        print(f"Error during API call: {e}")
        return pd.DataFrame()  # Return empty DataFrame on error
        
    flattened_data = []

    for transaction in data:
        try:
            flattened_record = {
                'transaction_id': transaction.get('id'),
                'account_id': transaction.get('account', {}).get('id'),
                'bank_name': transaction.get('account', {}).get('bank'),
                'account_name': transaction.get('account', {}).get('name'),
                'currency': transaction.get('account', {}).get('currency'),
                'category_id': transaction.get('category', {}).get('id'),
                'category_name': transaction.get('category', {}).get('name'),
                'value_date': transaction.get('value_date'),
                'bank_booking_date': transaction.get('bank_booking_date'),
                'amount': transaction.get('amount'),
                'purpose': transaction.get('purpose'),
                'counterpart_name': transaction.get('counterpart_name'),
                'counterpart_iban': transaction.get('counterpart_iban'),
                'is_payment': transaction.get('is_payment'),
                'reporting_amount': transaction.get('reporting_amount'),
                'reporting_currency': transaction.get('reporting_currency'),
                'exchange_rate': transaction.get('exchange_rate'),
                'conversion_date': transaction.get('conversion_date'),
                'tags': transaction.get('tags'),
                'modified_at': transaction.get('modified_at'),
            }
            flattened_data.append(flattened_record)
        except Exception as e:
            print(f'Error processing transaction: {str(e)}')
            print(transaction)
            continue

    return pd.DataFrame(flattened_data)

