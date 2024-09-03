
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
        print("API call returned data: ", data)
    except Exception as e:
        print(f"Error during API call: {e}")
        return None  # Exit the function if an error occurs

    if isinstance(data, list):
        # Convert the data into a pandas DataFrame
        df = pd.DataFrame(data)

        # Ensure the 'parent' key exists in the DataFrame
        if 'parent' in df.columns:
            print("Processing 'parent' field...")
            print("Sample 'parent' data: ", df['parent'].head())

            # Handle cases where 'parent' might be a dictionary or None
            df['parent_id'] = df['parent'].apply(lambda x: x.get('id') if isinstance(x, dict) else None)
            df['parent_name'] = df['parent'].apply(lambda x: x.get('name') if isinstance(x, dict) else None)

            # Drop the original 'parent' column
            df = df.drop(columns=['parent'])

        print("Final DataFrame: ")
        print(df)
        return df
    else:
        print("Unexpected data structure. Expected a list of categories.")
        return None
# get_categories(api)

def get_invoices(api):
    # Example of making a GET request to fetch company categories
    try:
        data = api.make_api_call("/invoices/")
        print(data)
    except Exception as e:
        print(f"Error during API call: {e}")


    invoices = []

    for item in data:
        # Assuming the response data is a list of dictionaries, where each dictionary is an invoice
        if isinstance(item, dict):
            if 'invoices' in item:
                invoices.extend(item['invoices'])  # if there's a nested 'invoices' key
            else:
                invoices.append(item)  # otherwise, treat the item as an invoice



    # Convert the list of invoices to a DataFrame
    df = pd.DataFrame(invoices)

    # Display the DataFrame
    df.head()
    print(df)

# get_invoices(api)

def get_banks(api):
    # Example of making a GET request to fetch company categories
    try:
        data = api.make_api_call("/banks/")
        print(data)
    except Exception as e:
        print(f"Error during API call: {e}")

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

    # Creating a DataFrame
    df = pd.DataFrame(flattened_data)

    # Display the DataFrame
    print(df)

# get_banks(api)


def get_transactions(api):


    try:
        data = api.make_api_call("/transactions/")
        # print(data)
    except Exception as e:
        print(f"Error during API call: {e}")
    # Flattening the JSON structure

    flattened_data = []

    for transaction in data:
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
            'conversion_date': transaction.get('conversion_date')
        }
        flattened_data.append(flattened_record)

    # Creating a DataFrame
    df = pd.DataFrame(flattened_data)

    # Display the DataFrame
    print(df)
    return df

