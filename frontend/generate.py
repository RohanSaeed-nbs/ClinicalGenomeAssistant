import streamlit as st
import requests
import re

def validate_and_breakdown_genome_variation(user_query):
    # Allow variations with or without parentheses, extra text, multiline, etc.
    pattern = re.compile(r"""
        (?P<refseq>NM_\d+\.\d+)               # RefSeq accession
        \((?P<gene>[A-Za-z0-9]+)\)            # Gene symbol in parentheses
        :
        (?P<cdna>                              # cDNA variation
            c\.
            (?:
                \d+[A-Z]>[A-Z] |               # substitution
                \d+del[A-Z]* |                 # deletion
                \d+dup[A-Z]* |                 # duplication
                \d+_\d+ins[A-Z]+ |             # insertion
                \d+_\d+delins[A-Z]+            # delins
            )
        )
        \s*                                    # optional space
        \(?p\.
        (?P<protein>                           # protein change
            [A-Za-z]{3}\d+[A-Za-z]{3}(fs)?     # e.g. Arg330Met, Leufs
        )
        \)?                                    # optional closing parenthesis
    """, re.VERBOSE | re.DOTALL)

    match = pattern.search(user_query)
    if match:
        parts = match.groupdict()
        print( (
            "✅ Valid genome variation string found!\n\n"
            f"**Breakdown:**\n"
            f"- **RefSeq accession number**: {parts['refseq']}\n"
            f"- **Gene symbol**: {parts['gene']}\n"
            f"- **cDNA variation**: {parts['cdna']}\n"
            f"- **Protein change**: {parts['protein']}"
        ))
        return True
    else:
        fail  =(
            "⚠️ Could not detect a valid genome variation string.\n"
            "Ensure it follows the format like:\n"
            "NM_000410.4(HFE):c.989G>T (p.Arg330Met)\n"
            "or NM_000218.2(KCNQ1):c.1893delC (p.Phe631Leufs)"
        )
        print( fail )
        return False 

st.set_page_config(page_title="Genomics AI Assistant", layout="centered")

st.title("🧬 Clinical Genomics AI Assistant")

st.markdown("""
    <style>
    textarea {
        background-color: ##262730 ;
    }
    text_input {
        background-color: ##262730 ;    
            }
    selectbox {
        background-color: ##262730 ;        
            }                
    </style>
""", unsafe_allow_html=True)

with st.form("patient_form"):
    st.header("1. Patient Information")
    col1, col2 = st.columns(2)
    with col1:
        patient_id = st.text_input("Case Id")
        age = st.text_input("Age")
        ethnicity = st.text_input("Ethnicity (optional)")
    with col2:
        family_history = st.text_input("Family History")
        sex = st.selectbox("Biological Sex", ["Male", "Female", "Other"])
        symptoms = st.text_input("Symptoms")

    st.divider()

    st.header("2. Genetic Data Input")
    raw_sequence = st.text_area("Input Genome Variation in HVGS Format")
    sequence_valid = raw_sequence   #validate_and_breakdown_genome_variation(raw_sequence)
    st.divider()

    st.header("3. Choose Action")
    action = st.radio("What do you want the AI to do?", ["Search Genome Variation", "Suggest Clinical Significance"])

    submitted = st.form_submit_button("Submit",use_container_width=True)
#  Post-submit logic outside the form
if submitted:
    if not sequence_valid:
        st.error("Enter a valid sequence")
    else:

        if patient_id and age and family_history and symptoms:
        
            history = ""

            age_str= f"Family History: {age} years old {ethnicity or ''} {sex or ''}."
            history_str = ""
            symptoms_str = ""
            if family_history == "None":
                history_str  = ""
            else:   
                history_str = f"Family History of {family_history}" 

            if symptoms =="None":
                symptoms_str = ""
            else:    
                symptoms_str = f"Symptoms include {symptoms}"

            history = age_str+history_str+symptoms_str

            search_or_diagnose = {
                "action": action,
                "genome variation": f"Variation: {raw_sequence}",
                "history": history
            }

            st.session_state['submitted_data'] = {
                "case_id":patient_id,
                "age": age,
                "ethnicity": ethnicity,
                "sex": sex,
                "history": history,
                "symptoms": symptoms,
                "action": action,
                "sequence": raw_sequence,
            }

            response = requests.post("http://localhost:5000/api/genome_search_or_diagnose",json=search_or_diagnose)
            ai_response = {}
            if response.status_code == 200:
                ai_response = response.json()  # Convert response to dict
                st.session_state["ai_response"] = ai_response
                st.success("✅ Submitted successfully!")
            else:
                st.error(response.text)

            st.session_state['ai_response'] = ai_response    
            st.subheader("📋 Patient Summary")
            st.markdown(f"**Patient ID**: {patient_id}")
            st.markdown(f"**Age**: {age}")
            st.markdown(f"**Sex**: {sex}")
            st.markdown(f"**Ethnicity**: {ethnicity or 'Not provided'}")
            st.markdown(f"**Family Medical History**: {family_history}")
            st.markdown(f"**Symptoms**: {symptoms}")
            st.markdown(f"**Selected Action**: {action}")

            st.subheader("🧬 Genome Variation")
            st.code(raw_sequence[:500] + ("..." if len(raw_sequence) > 500 else ""), language="text")
            st.divider()

            st.subheader("🧠 AI Assistant Response")
    
            if action == "Suggest Clinical Significance":
                st.markdown(ai_response["Answer"])
                st.subheader("🧬 Genomic Variation")
                st.markdown(f"**Variation**: {ai_response['Genome_variation']}")

                st.subheader("🩺 Associated Conditions")
                diseases = ai_response["Associated_Desieases"].split(",")
                for d in diseases:
                    st.markdown(f"- {d.strip()}")

                st.subheader("📋 Patient History")
                st.markdown(ai_response["patient_history"])

            st.subheader("📚 Sources")

            if "Sources" in ai_response:
                for source in ai_response.get("Sources",''):
                    if isinstance(source, dict):
                        print("INSIDE FORloop==>", source)
                        st.markdown(f"**Source**: {source.get('source','')}")
                        st.markdown(f"**ID**: {source.get('id','')}")
                        st.markdown(f"**Summary**: {source.get('text','')}")

                        meta = source.get("metadata", '')
                        if isinstance(meta, dict):
                 
                            with st.expander("**Metadata**", expanded=True):
                                st.markdown(f"**Gene**: {meta.get('GeneSymbol','')}")
                                st.markdown(f"**Type**: {meta.get('Type','')}")
                                st.markdown(f"**Clinical Significance**: {meta.get('ClinicalSignificance','')}")
                                st.markdown(f"**Phenotypes**: {', '.join(meta.get('PhenotypeList',''))}")
                                st.markdown(f"**Review Status**: {meta.get('ReviewStatus','')}")
                                st.markdown(f"**Assembly**: {meta.get('Assembly','')}")
                                st.markdown(f"**Location**: Chr{meta.get('Chromosome','')}:{meta.get('Start','')}-{meta.get('Stop','')}")
                                st.markdown(f"**Ref/Alt**: {meta.get('ReferenceAllele','')} → {meta.get('AlternateAllele','')}")
                        st.divider()

                if action == "Suggest Clinical Significance":
                    st.subheader("📝 Confirm Clinical Significance")
                    confirm_submitted = ""
                    with st.form("confirm_significance_form"):
                        significance_response = st.radio(
                            "Do you accept the clinical significance provided by the AI?",
                            ["Accept", "Decline"],
                            horizontal=True
                    )

                        confirm_submitted = st.form_submit_button("Confirm")

                    if confirm_submitted:
                        print(confirm_submitted)
                        print(st.session_state["ai_response"] )
                        clinical_significance_response = {
                                                "decision": significance_response,
                                                "ai_response" : st.session_state["ai_response"]    
                                            }

                        st.success(f"✅ You chose to **{significance_response}** the clinical significance.")
                        try:
                            requests.post("http://backend:5000/api/diagnosis_confirmation", json=clinical_significance_response)
                        except Exception as e:
                            st.error(f"Error contacting server: {e}")
                            
            else:
                st.error("No sources found in the response.")
        else:
            st.error(f"Enter missing Inputs First!")
    # Process the confirmation
