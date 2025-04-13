# Clinical Genome Assistant

**Clinical Genome Assistant** is a web-based application designed to assist clinicians and researchers in interpreting genomic variations. By inputting a genome variation string, users receive a detailed breakdown of the variation along with relevant clinical information.

## Features

- **Genome Variation Parsing**: Input genome variation strings in standard formats to receive structured interpretations.
- **Clinical Insights**: Obtain information related to gene functions, associated conditions, and potential clinical significance.
- **User-Friendly Interface**: Interactive frontend built with Streamlit for ease of use.
- **Modular Architecture**: Separation of frontend and backend components for scalability and maintainability.

## Getting Started

### Prerequisites

- Docker and Docker Compose installed on your system.

### Installation

1. **Clone the Repository**:
   ```bash
   git clone https://github.com/RohanSaeed-nbs/ClinicalGenomeAssistant.git
   cd ClinicalGenomeAssistant

2. **Build and Run the Application**:
   ```bash
   docker-compose up --build  

3. **Access the Application**:
   Open your browser and navigate to `http://localhost:8501` to use the Clinical Genome Assistant.

## Usage

1. Enter a genome variation string in the input field.
2. Click the "Submit" button.
3. View the parsed results and associated clinical information displayed on the page.  

## Project Structure

ClinicalGenomeAssistant/ 
├── backend/  # Flask backend handling API requests 
├── frontend/  # Streamlit frontend application 
├── docker-compose.yml  # Docker Compose configuration 
└── .gitignore  # Specifies intentionally untracked files to ignore


## Contributing

Contributions are welcome! Please fork the repository and submit a pull request for any enhancements or bug fixes.  
Before contributing, please ensure your code follows best practices and includes relevant documentation or comments where necessary.


## Acknowledgements

Special thanks to all contributors and the open-source community for their invaluable resources and support.

