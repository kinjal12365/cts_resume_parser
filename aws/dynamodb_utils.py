def setup_dynamodb_table(dynamodb, dynamodb_resource, table_name):
    existing_tables = dynamodb.list_tables()['TableNames']
    if table_name not in existing_tables:
        dynamodb.create_table(
            TableName=table_name,
            KeySchema=[{'AttributeName': 'filename', 'KeyType': 'HASH'}],
            AttributeDefinitions=[{'AttributeName': 'filename', 'AttributeType': 'S'}],
            ProvisionedThroughput={'ReadCapacityUnits': 5, 'WriteCapacityUnits': 5}
        )
        print(f"⏳ Creating DynamoDB table '{table_name}'...")
        waiter = dynamodb.get_waiter('table_exists')
        waiter.wait(TableName=table_name)
        print(f"✅ DynamoDB table '{table_name}' created.")
    else:
        print(f"ℹ️ DynamoDB table '{table_name}' already exists.")
    
    return dynamodb_resource.Table(table_name)
