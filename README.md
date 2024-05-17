


curl -X POST  -d '{"key":"value"}'

curl --request POST \
     --url https://go.v7labs.com/api/workspaces/018ede38-df55-7231-9c21-abbfecc88bf7/triggers \
     --header 'X-API-KEY: ' \
     --header 'accept: application/json' \
     --header 'content-type: application/json' \
     --data '
{
  "action": {
    "type": "webhook",
    "url": ""
  },
  "events": {
    "entity.field_completed": {
      "property_id": "018f85e4-312e-7778-b235-d1a48a133022"
    }
  },
  "project_id": "018f85d6-01d9-7a1b-8a2d-b2be84a996f9"
}
'

## Prompts

### Test Item

Extract all the blood test results line by line. Return the test name, the test result, the test units and the test range.

For example:
{
      "test_name": "Hemoglobin (Hb)",
      "test_result": "12.5",
      "test_units": "g/dL",
      "test_range": "Low 13.0 - 17.0"
}

### Flag
Look at @Test Item. Check the value against the range for each item. If the value is outside the range then return a key with "high", otherwise return  the key with "low", otherwise leave it out. Only the items outside of the range should be returned.