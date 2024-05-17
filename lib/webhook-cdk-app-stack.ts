
import { Stack } from 'aws-cdk-lib';
import * as cdk from 'aws-cdk-lib';
import { Construct } from 'constructs';
import * as lambda from 'aws-cdk-lib/aws-lambda';
import { LayerVersion, Function, Runtime, Code } from 'aws-cdk-lib/aws-lambda';
import * as apigateway from 'aws-cdk-lib/aws-apigateway';

export class WebhookCdkAppStack extends cdk.Stack {
  constructor(scope: Construct, id: string, props?: cdk.StackProps) {
    super(scope, id, props);

    // Create a Layer with Powertools for AWS Lambda (Python)
    const powertoolsLayer = LayerVersion.fromLayerVersionArn(
      this,
      'PowertoolsLayer',
      `arn:aws:lambda:${Stack.of(this).region}:017000801446:layer:AWSLambdaPowertoolsPythonV2:69`
    );

    // Define the Lambda function
    const webhookLambda = new lambda.Function(this, 'WebhookHandler', {
      runtime: lambda.Runtime.PYTHON_3_12,
      code: lambda.Code.fromAsset('webhook_handler'),
      handler: 'main.lambda_handler',
      layers: [powertoolsLayer],
      environment: {
        api_key: 'API_KEY' // REPLACE WITH YOUR API KEY
      }
    });

    // Define the API Gateway
    const api = new apigateway.RestApi(this, 'WebhookAPI', {
      restApiName: 'Webhook Service',
      description: 'This service serves as a webhook receiver.'
    });

    const webhook = api.root.addResource('webhook');
    webhook.addMethod('POST', new apigateway.LambdaIntegration(webhookLambda));
    
    // output the API Gateway endpoint
    new cdk.CfnOutput(this, 'WebhookUrl', {
      value: api.url
    });
  }
}
