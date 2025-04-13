from flask import Flask, request, jsonify
import boto3
import json

app = Flask(__name__)

# Initialize boto3 Lambda client
client = boto3.client('lambda', region_name='us-west-2')  # change region if needed

@app.route('/api/genome_search_or_diagnose', methods=['POST'])
def genome_search_or_diagnose():
    data = request.get_json()
    action = data.get("action")
    genome_variation = data.get("genome variation")
    history = data.get("history")

     # Payload to send
    payload = {
          "query": f"{genome_variation} identified in {history} " ,
          "search":  True if action =="Search Genome Variation" else False
    }    
            # Invoke Lambda
    response = client.invoke(
                FunctionName='genomic-aws-agent',  # replace with your function name
                InvocationType='RequestResponse',  # or 'Event' for async
                Payload=json.dumps(payload)
            )

            # Read the response
    ai_response = json.loads(response['Payload'].read())
    print(ai_response)      
    return jsonify(ai_response)


@app.route('/api/diagnosis_confirmation', methods=['POST'])
def diagnosis_confirmation():
    data = request.get_json()
    decision = data.get("decision")  
    print(data)
    ai_response = data.get("ai_response")
    if decision=="Accept":
        # Payload to send
        payload = {
          "json":ai_response 
        } 
        
              # Invoke Lambda
        response = client.invoke(
                FunctionName='save-history-to-s3',  # replace with your function name
                InvocationType='RequestResponse',  # or 'Event' for async
                Payload=json.dumps(payload)
            )    
   
      # Read the response
    ai_response = json.loads(response['Payload'].read())
    print(ai_response)      
    return jsonify(ai_response)

if __name__ == '__main__':
    app.run(host="0.0.0.0", port=5000)
