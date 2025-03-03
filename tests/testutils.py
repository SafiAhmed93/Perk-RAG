from azure.data.tables import TableServiceClient

table_service_client = TableServiceClient.from_connection_string("UseDevelopmentStorage=True")