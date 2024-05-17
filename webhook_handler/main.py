from aws_lambda_powertools import Logger
from aws_lambda_powertools.utilities.typing import LambdaContext
import json
import csv
import json
import os
import urllib3

# Set your workspace ID, project ID, and API key
# replace these values with your values
workspace_id = '018ede38-df55-7231-9c21-abbfecc88bf7'
project_id = '018f85d6-01d9-7a1b-8a2d-b2be84a996f9'
api_key = os.environ['API_KEY']

url = f"https://go.v7labs.com/api/workspaces/{workspace_id}/projects/{project_id}/entities"

# Headers for the request
headers = {
    "X-API-KEY": api_key,
    "Content-Type": "application/json"
}

logger = Logger()

# Load CSV file into memory, pretending it's a database
biomarkers_db = None
with open('Biomarkers.csv', 'r') as file:
    file = csv.reader(file, delimiter=',')
    next(file)  # Skip empty line
    next(file)  # Skip header

    # Example row in the biomarkers_db: ['', 'SODIUM', 'high', '["dementia", "diabetes", "dehydration", "fever"]']
    # Extract biomarker, high/low and associated diseases
    biomarkers_db = [(row[1], row[3]) for row in list(file)]


print(biomarkers_db[0])

@logger.inject_lambda_context(log_event=False)
def lambda_handler(event: dict, context: LambdaContext) -> dict:    
    try:
        # Log the entire event to inspect its structure
        logger.info("Event: %s", json.dumps(event, indent=4))
        
        body = event['body']
        body_dict = json.loads(body)

        # Extract the 'fields' key
        flags = json.loads(body_dict['entity']['fields']['flag']["data"]["value"])
        
        logger.info("Flags: %s", flags)
        # {'Blood Urea Nitrogen': 'high', 'AST': 'high', 'Chol/HDL Ratio': 'high'}

        return_fields = {}

        for biomarker, highlow in flags.items():
            print(f"Key: {biomarker}, Value: {highlow}")
            # Check if the biomarker exists in the database - does lowercase string comparison but 
            # need to be very careful to check with medical domain experts if lower case is ok as it could change the meaning
            # we should really query a medical database to get the correct biomarker here

            # Check if the biomarker exists in the database, and extract the associated diseases
            key = biomarker.lower()
            disease = [disease for biomarker, disease in biomarkers_db if key in biomarker.lower()]

            if not disease:
                logger.warning("Biomarker not found in database: %s", key)
                continue
            else:
                logger.info("Biomarker found: %s", key.lower())
                return_fields[key.lower()] = disease

        # Make the POST request to upload the entity back to V7 - how do you set the ID of the entity?
        http = urllib3.PoolManager()
        response = http.request(
            'POST',
            url,
            body=json.dumps({
                "fields": {
                    "diseases": json.dumps(return_fields)
                }
            }),
            headers=headers
        )

        if response.status != 200:
            logger.error("Failed to upload entity: %s", response.data.decode('utf-8'))
            return {
                'statusCode': 500,
                'body': 'Failed to upload entity'
            }

        return {
            'statusCode': 200,
            'body': 'Webhook processed successfully!'
        }

    except KeyError as e:
        logger.error("Missing key in event: %s", str(e))
        return {
            'statusCode': 400,
            'body': f"Bad Request: {str(e)}"
        }
    except Exception as e:
        logger.error("Error processing webhook: %s", str(e))
        return {
            'statusCode': 500,
            'body': 'Internal server error'
        }