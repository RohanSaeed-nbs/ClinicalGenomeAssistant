from flask import Flask, request, jsonify

app = Flask(__name__)

# Dummy data for search
search_database = {
    "fever": ["Common Cold", "Flu", "COVID-19"],
    "cough": ["Bronchitis", "Asthma", "COVID-19"],
    "headache": ["Migraine", "Tension Headache", "Sinus Infection"]
}

# Dummy diagnosis logic
def diagnose_symptoms(symptoms):
    if "fever" in symptoms and "cough" in symptoms:
        return "You may have the flu or COVID-19."
    elif "headache" in symptoms:
        return "It might be a migraine or tension headache."
    else:
        return "No matching diagnosis found. Please consult a doctor."

@app.route('/api/search', methods=['GET'])
def search():
    ai_response = {
  "Answer": "The identified BRCA1 gene variant (c.68_69delAG) is a well-known pathogenic mutation linked to hereditary breast and ovarian cancer syndrome. The deletion results in a frameshift and premature stop codon, significantly affecting protein function.",
  "Genome_variation": "BRCA1 c.68_69delAG, deletion, Chr17:41276045-41276046",
  "Associated_Desieases": "Hereditary Breast Cancer, Ovarian Cancer",
  "patient_history": "Patient has a maternal history of breast cancer diagnosed at age 42. No other known genetic conditions in the family.",
  "Sources": [
    {
      "source": "ClinVar_JSON",
      "id": "VCV000000123.5",
      "text": "BRCA1 variant c.68_69delAG is classified as pathogenic and is associated with an increased risk for hereditary breast and ovarian cancers.",
      "metadata": {
        "VariationID": "VCV000000123.5",
        "GeneSymbol": "BRCA1",
        "Type": "Deletion",
        "ClinicalSignificance": "Pathogenic",
        "PhenotypeList": ["Hereditary Breast Cancer", "Ovarian Cancer"],
        "ReviewStatus": "Reviewed by expert panel",
        "Assembly": "GRCh38",
        "Chromosome": "17",
        "Start": 41276045,
        "Stop": 41276046,
        "ReferenceAllele": "AG",
        "AlternateAllele": "-"
      }
    },
     
    {
          "source": "Add source here (e.g., 'ClinVar_JSON' or 'History')",
          "id": "<VariationID>",
          "text": "<Summary of gene, variant, and clinical context>",
          "metadata": {
            "VariationID": "<string>",
            "GeneSymbol": "<string>",
            "Type": "<string>",
            "ClinicalSignificance": "<string>",
            "PhenotypeList": ["<string>", "<string>"],
            "ReviewStatus": "<string>",
            "Assembly": "<string>",
            "Chromosome": "<string>",
            "Start": "<int>",
            "Stop": "<int>",
            "ReferenceAllele": "<string>",
            "AlternateAllele": "<string>"
          }
        
    }
    ]
    }
    return jsonify(ai_response)
    # keyword = request.args.get('query', '').lower()
    # if not keyword:
    #     return jsonify({"error": "Query parameter 'query' is required."}), 400

    # results = search_database.get(keyword, [])
    # return jsonify({"query": keyword, "results": results})

@app.route('/api/diagnose', methods=['POST'])
def diagnose():
    data = request.get_json()
    symptoms = data.get("symptoms", [])
    
    if not isinstance(symptoms, list) or not symptoms:
        return jsonify({"error": "JSON body must contain a non-empty 'symptoms' list."}), 400

    diagnosis = diagnose_symptoms(symptoms)
    return jsonify({"symptoms": symptoms, "diagnosis": diagnosis})

if __name__ == '__main__':
    app.run(host="0.0.0.0", port=5000)
