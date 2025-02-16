import auth
import pandas as pd
from api_logger import logger

pd.set_option('display.width', 400)
pd.set_option('display.max_columns', None)
pd.set_option('display.max_rows', None)


def get_categories(api):
    logger.op.info("Starting category retrieval")
    # Initialize data to avoid UnboundLocalError
    data = []

    try:
        logger.conn.info("Making API call to /categories/")
        data = api.make_api_call("/categories/")
        logger.conn.debug("API response received", count=len(data) if isinstance(data, list) else 0)
    except Exception as e:
        logger.conn.error("API call to /categories/ failed", error=str(e))
        return None

    if isinstance(data, list):
        logger.op.debug("Converting categories data to DataFrame")
        # Convert the data into a pandas DataFrame
        df = pd.DataFrame(data)
        
        # Ensure the 'parent' key exists in the DataFrame
        if 'parent' in df.columns:
            logger.op.debug("Processing parent category relationships")
            # Handle cases where 'parent' might be a dictionary or None
            df['parent_id'] = df['parent'].apply(lambda x: x.get('id') if isinstance(x, dict) else None)
            df['parent_name'] = df['parent'].apply(lambda x: x.get('name') if isinstance(x, dict) else None)
            
            # Drop the original 'parent' column
            df = df.drop(columns=['parent'])
            
        logger.op.info("Category processing completed", 
                      row_count=len(df),
                      column_count=len(df.columns))
        return df
    else:
        logger.op.error("Invalid data structure received", 
                       data_type=type(data).__name__)
        return None

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
    logger.op.info("Starting invoice retrieval", 
                   start_date=start_date,
                   end_date=end_date,
                   modified_since=modified_since,
                   page_size=page_size)
    
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
        logger.conn.info("Making API call to /invoices/", params=params)
        data = api.make_api_call("/invoices/", params=params)
        logger.conn.debug("API response received", count=len(data) if isinstance(data, list) else 0)
    except Exception as e:
        logger.conn.error("API call to /invoices/ failed", error=str(e), params=params)
        return pd.DataFrame()

    logger.op.debug("Processing invoice data")
    invoices = []
    for item in data:
        if isinstance(item, dict):
            if 'invoices' in item:
                invoices.extend(item['invoices'])
            else:
                invoices.append(item)

    df = pd.DataFrame(invoices)
    logger.op.info("Invoice processing completed", 
                   row_count=len(df),
                   column_count=len(df.columns))
    return df

def get_banks(api, start_date=None, end_date=None, page_size=None):
    """
    Fetch bank data with optional date filtering and pagination
    
    Args:
        api: CommitlyAPI instance
        start_date: Optional ISO format date string for filtering bank data after this date
        end_date: Optional ISO format date string for filtering bank data before this date
        page_size: Optional integer for number of records per page
    """
    logger.op.info("Starting bank data retrieval", 
                   start_date=start_date,
                   end_date=end_date,
                   page_size=page_size)
    
    params = {}
    if start_date:
        params['from'] = start_date
    if end_date:
        params['to'] = end_date
    if page_size:
        params['page_size'] = page_size

    try:
        logger.conn.info("Making API call to /banks/", params=params)
        data = api.make_api_call("/banks/", params=params)
        logger.conn.debug("API response received", count=len(data) if isinstance(data, list) else 0)
    except Exception as e:
        logger.conn.error("API call to /banks/ failed", error=str(e), params=params)
        return pd.DataFrame()

    logger.op.debug("Processing bank data")
    flattened_data = []
    for result in data:
        try:
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
        except Exception as e:
            logger.op.error("Error processing bank record", 
                           error=str(e),
                           bank_id=result.get('id'),
                           bank_name=result.get('name'))
            continue

    df = pd.DataFrame(flattened_data)
    logger.op.info("Bank data processing completed", 
                   row_count=len(df),
                   column_count=len(df.columns))
    return df

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
    logger.op.info("Starting transaction retrieval", 
                   start_date=start_date,
                   end_date=end_date,
                   modified_since=modified_since,
                   page_size=page_size)
    
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
        logger.conn.info("Making API call to /transactions/", params=params)
        data = api.make_api_call("/transactions/", params=params)
        logger.conn.debug("API response received", 
                         count=len(data) if isinstance(data, list) else 0)
    except Exception as e:
        logger.conn.error("API call to /transactions/ failed", error=str(e), params=params)
        return pd.DataFrame()
        
    logger.op.debug("Processing transaction data")
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
            logger.op.error("Error processing transaction record", 
                           error=str(e),
                           transaction_id=transaction.get('id'))
            continue

    df = pd.DataFrame(flattened_data)
    logger.op.info("Transaction processing completed", 
                   row_count=len(df),
                   column_count=len(df.columns))
    return df

