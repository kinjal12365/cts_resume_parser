import json
import boto3
from botocore.exceptions import ClientError
import urllib.parse
import os
import re
import uuid
from datetime import datetime

# --- Configuration ---
DESTINATION_BUCKET = "ENTER YOUR BUCKET"
# ----------------------------------------------------


# Initialize Boto3 clients.
s3_client = boto3.client('s3')
bedrock_runtime = boto3.client('bedrock-runtime') # Only Bedrock client is needed for AI tasks

# --- Skill & Language Libraries (unchanged) ---
TECHNICAL_SKILLS_LIBRARY = [
    # --- Programming Languages & Scripting (40+) ---
    "python", "java", "c++", "c#", "javascript", "typescript", "php", "ruby", "go", "swift", "kotlin", "rust",
    "sql", "pl/sql", "bash", "powershell", "linux shell scripting", "html", "css", "r", "perl", "scala", "haskell",
    "matlab", "fortran", "cobol", "delphi", "assembly", "objective-c", "dart", "groovy", "f#", "lua", "elixir",
    "erlang", "clojure", "scheme", "vba", "apex", "solidity", "rust", "coffeescript", "less", "sass", "jsx", "tsx",

    # --- Web Development - Frontend (30+) ---
    "react", "angular", "vue.js", "next.js", "node.js", "express", "jquery", "bootstrap", "tailwind css",
    "material-ui", "ant design", "redux", "mobx", "context api", "webpack", "babel", "parcel", "grunt", "gulp",
    "pwa", "spa", "responsive design", "web accessibility", "seo", "pug", "handlebars.js", "svelte", "ember.js",
    "webassembly", "html5", "css3", "sass", "less", "webgl",

    # --- Web Development - Backend & Frameworks (25+) ---
    "django", "flask", "ruby on rails", "asp.net", "spring boot", "laravel", "symfony", "cakephp", "phalcon",
    "gin", "fiber", "nestjs", "fastapi", "graphql", "rest api", "microservices", "nginx", "apache http server",
    "iis", "tomcat", "jetty", "weblogic", "websphere", "grpc", "message queues", "rabbitmq", "apache kafka",

    # --- Databases & Data Management (30+) ---
    "mysql", "postgresql", "mongodb", "redis", "microsoft sql server", "oracle", "sqlite", "cassandra", "couchbase",
    "dynamodb", "neo4j", "elasticsearch", "solr", "hbase", "teradata", "db2", "snowflake", "bigquery", "redshift",
    "data warehousing", "etl", "data modeling", "database administration", "sql optimization", "nosql",
    "in-memory databases", "time-series databases", "graph databases", "columnar databases", "data lakes",
    "lakehouse", "data bricks", "data governance", "data quality",

    # --- Cloud Platforms & DevOps (45+) ---
    "aws", "amazon web services", "azure", "google cloud", "gcp", "docker", "kubernetes", "terraform", "ansible",
    "jenkins", "git", "github", "gitlab", "ci/cd", "ec2", "s3", "lambda", "rds", "dynamodb", "iam", "vpc",
    "cloudformation", "cloudwatch", "ebs", "efs", "ecs", "eks", "fargate", "cloudtrail", "config", "route 53",
    "api gateway", "sns", "sqs", "step functions", "azure devops", "azure functions", "azure virtual machines",
    "google kubernetes engine", "google cloud functions", "google app engine", "serverless", "containerization",
    "helm", "prometheus", "grafana", "splunk", "logstash", "kibana", "packer", "vagrant", "chef", "puppet",
    "datadog", "new relic", "nagios", "zabbix", "mulesoft", "api management",

    # --- Data Science, Machine Learning & AI (40+) ---
    "pandas", "numpy", "scikit-learn", "tensorflow", "pytorch", "keras", "matplotlib", "seaborn", "nltk", "opencv",
    "power bi", "tableau", "spark", "hadoop", "apache hadoop", "databricks", "mlflow", "jupyter", "zeppelin",
    "scipy", "statsmodels", "xgboost", "lightgbm", "catboost", "dask", "airflow", "kubeflow", "aws sagemaker",
    "azure ml", "google ai platform", "machine learning", "deep learning", "natural language processing", "nlp",
    "computer vision", "reinforcement learning", "artificial intelligence", "ai", "data analysis", "data visualization",
    "big data", "predictive analytics", "statistical modeling", "time series analysis", "feature engineering",
    "model deployment", "model monitoring", "mlops", "data governance", "mle", "data engineering", "vector databases",

    # --- Operating Systems & Virtualization (15+) ---
    "linux", "windows server", "macos", "ubuntu", "centos", "red hat", "debian", "unix", "vmware", "hyper-v",
    "virtualbox", "kvm", "xen", "azure stack", "vmware vsphere",

    # --- Cybersecurity & Networking (20+) ---
    "network security", "firewalls", "intrusion detection systems", "ids", "intrusion prevention systems", "ips",
    "vpn", "encryption", "penetration testing", "ethical hacking", "vulnerability assessment", "security audits",
    "compliance", "gdpr", "hipaa", "iso 27001", "network protocols", "tcp/ip", "dns", "dhcp", "routing", "switching",
    "wireshark", "snort", "nmap", "kali linux", "endpoint security", "identity and access management", "ssm",

    # --- Project Management & Methodologies (10+) ---
    "agile", "scrum", "kanban", "jira", "confluence", "trello", "asana", "microsoft project", "versionone",
    "devsecops", "waterfall", "sdlc",

    # --- Testing & Quality Assurance (10+) ---
    "unit testing", "integration testing", "e2e testing", "regression testing", "performance testing", "load testing",
    "selenium", "cypress", "jest", "pytest", "jmeter", "test automation", "qa", "bug tracking",

    # --- Enterprise Software & CRM/ERP (10+) ---
    "salesforce", "sap", "oracle erp", "microsoft dynamics", "servicenow", "zendesk", "hubspot", "jira service management",
    "microsoft 365 administration", "google workspace administration", "sharepoint", "active directory",

    # --- Design & UI/UX (10+) ---
    "figma", "sketch", "adobe xd", "photoshop", "illustrator", "invision", "zeplin", "wireframing", "prototyping",
    "user research", "usability testing", "information architecture", "design systems",

    # --- Big Data Technologies (10+) ---
    "apache spark", "apache hadoop", "apache hive", "apache pig", "apache hbase", "apache flink", "apache impala",
    "data streaming", "apache storm", "apache samza", "apache kinesis", "google dataflow", "azure databricks",

    # --- Other / Miscellaneous (10+) ---
    "microsoft excel", "google sheets", "spreadsheet analysis", "data entry automation", "scripting",
    "technical support", "troubleshooting", "hardware maintenance", "system administration", "technical writing",
    "documentation", "api design", "sdk development", "blockchain", "cryptocurrency", "smart contracts", "ai ethics"
]
NON_TECHNICAL_SKILLS_LIBRARY = [
    "communication", "verbal communication", "written communication", "presentation skills", "public speaking",
    "teamwork", "collaboration", "leadership", "mentoring", "team management", "project management",
    "problem solving", "critical thinking", "analytical skills", "troubleshooting", "debugging",
    "time management", "adaptability", "creativity", "work ethic", "attention to detail", "customer service"
]
LANGUAGES_SPOKEN_LIBRARY = [
    "english", "mandarin", "chinese", "hindi", "spanish", "french", "arabic", "bengali", "russian",
    "portuguese", "urdu", "indonesian", "german", "japanese", "swahili", "marathi", "telugu",
    "turkish", "tamil", "vietnamese", "korean", "italian", "thai", "gujarati", "jin", "southern min",
    "persian", "polish", "pashto", "kannada", "malayalam", "dutch"
]

def call_bedrock_nova_model(prompt: str, max_tokens: int) -> str:
    
    #  Calling the Bedrock Nova Pro model with a specific prompt.
    
    model_id = "amazon.nova-pro-v1:0"
    try:
        response = bedrock_runtime.converse(
            modelId=model_id,
            messages=[{"role": "user", "content": [{"text": prompt}]}],
            inferenceConfig={"maxTokens": max_tokens, "temperature": 0.1}
        )
        return response['output']['message']['content'][0]['text'].strip()
    except ClientError as e:
        print(f"AWS Bedrock ClientError: {e}")
        return f"API Request Error: {e}"
    except Exception as e:
        print(f"An unexpected error occurred in call_bedrock_nova_model: {e}")
        return f"An unexpected error occurred during API call: {e}"


def get_name_via_bedrock(resume_text: str) -> str:

    # Extracting the person's full name using the Bedrock Nova pro model with a strict prompt.

    if not resume_text: return "Could not extract name."

    # strict prompting is done to ensure only the name is returned.
    prompt = f"""
    From the following resume text, extract only the full name of the person. Do not add any extra text, titles, explanations, or punctuation. Just return the name.

    Resume Text:
    ---
    {resume_text}
    ---
    Name:"""

    # Call the generic Bedrock function with a low max_tokens for a name
    name = call_bedrock_nova_model(prompt, max_tokens=20)

    # Basic cleanup in case the model adds extra characters
    name = name.strip().strip('"').strip("'")
    
    # A simple check to see if the response is reasonable (not a long sentence)
    if len(name.split()) > 5: # If more than 5 words, it's likely not just a name
        print(f"Warning: Name extraction returned a long string: '{name}'. Falling back.")
        return "Could not extract name."

    return name if name else "Could not extract name."


def get_experience_summary_via_bedrock(resume_text: str) -> str:
    """Creating a 1-2 line experience summary using the Bedrock Nova pro model."""
    if not resume_text: return "Not defined"

    prompt = f"""
    Act as an expert technical recruiter. Analyze the following resume text and provide a 1-2 line professional summary.
    Do not exceed more than 20 charecters just give a short crisp detail of the candidate and dont give double quotes before and after
    it should be like experience aiml or like experienced in front end or experienced in cloud
    - The summary should identify the candidate's main field or tech domain (e.g., "Full-Stack Developer", "Data Scientist", "Cloud Engineer").
    - If a total duration of experience is clearly mentioned (e.g., "5 years"), integrate it into the summary.
    - Example: "A Full-Stack Developer with 5 years of experience in React and Node.js."
    - Example: "A Data Scientist specializing in machine learning and natural language processing."
    - If you cannot confidently determine a professional summary or field, or if no experience is mentioned, return the single word "NONE".

    Resume Text:
    ---
    {resume_text}
    ---
    """

    # Call the generic Bedrock function with more tokens for a summary
    api_response = call_bedrock_nova_model(prompt, max_tokens=150)

    response_lower = api_response.lower()
    if "none" in response_lower or "sorry" in response_lower or "unable" in response_lower or not api_response or "error" in response_lower:
        return "Not defined"

    return api_response


def check_postgraduation_status_via_bedrock(resume_text: str) -> int:
    """
    Checks if a resume mentions a postgraduate degree using the Bedrock Nova Lite model.
    Returns 1 if a postgraduate degree is found, otherwise 0.
    """
    if not resume_text:
        return 0

    # A very specific prompt to get a binary (1/0) answer.
    prompt = f"""
    Analyze the following resume text to determine if the candidate has a postgraduate degree.
    Look for keywords like "Master's", "M.S.", "M.Sc.", "M.Tech", "MBA", "PhD", "Post Graduate", "PGDM", or similar advanced degrees.

    - If you find any mention of a postgraduate degree (completed or ongoing), your entire response must be only the single digit: 1
    - If you do not find any mention of a postgraduate degree, your entire response must be only the single digit: 0

    Do not add any other text, explanation, or punctuation.

    Resume Text:
    ---
    {resume_text}
    ---
    Result:"""

    # Call the generic Bedrock function with a very low token count for a single digit.
    api_response = call_bedrock_nova_model(prompt, max_tokens=5)

    # Clean up the response and ensure it's either 1 or 0.
    if api_response.strip() == '1':
        return 1
    else:
        # Default to 0 for any other response ("0", errors, or unexpected text).
        return 0


def extract_contact_info(resume_text: str) -> dict:
    """Extracts email and phone number using regex."""
    email_match = re.search(r'[\w\.-]+@[\w\.-]+', resume_text)

    # or can be like \d{10} but went with more advanced regex

    phone_match = re.search(r'(\+?\d{1,3}[-.\s]?)?\(?\d{3}\)?[-.\s]?\d{3}[-.\s]?\d{4}', resume_text)

    return {
        "email": email_match.group(0) if email_match else None,
        "phone_number": phone_match.group(0).strip() if phone_match else None,
    }


def extract_items_from_library(resume_text: str, library: list) -> list:
    """Generic function to find items from a given library within the resume text."""
    found_items = set()
    lower_resume = resume_text.lower()
    for item in library:
        if re.search(r'\b' + re.escape(item) + r'\b', lower_resume):
            found_items.add(item.title())
    return sorted(list(found_items))


def lambda_handler(event, context):
    """Main AWS Lambda handler function triggered by S3 file upload."""
    try:
        source_bucket = event['Records'][0]['s3']['bucket']['name']
        source_key = urllib.parse.unquote_plus(event['Records'][0]['s3']['object']['key'], encoding='utf-8')
        print(f"New file detected: '{source_key}' in bucket '{source_bucket}'.")

        s3_object = s3_client.get_object(Bucket=source_bucket, Key=source_key)
        resume_text = s3_object['Body'].read().decode('utf-8')

        print("Extracting details using Amazon Bedrock...")
        # Use Bedrock for name, summary, and post-graduation status
        extracted_name = get_name_via_bedrock(resume_text)
        experience_summary = get_experience_summary_via_bedrock(resume_text)
        is_post_graduate = check_postgraduation_status_via_bedrock(resume_text)

        print("Extracting contact info and skills...")
        contact_info = extract_contact_info(resume_text)
        technical_skills = extract_items_from_library(resume_text, TECHNICAL_SKILLS_LIBRARY)
        non_technical_skills = extract_items_from_library(resume_text, NON_TECHNICAL_SKILLS_LIBRARY)
        languages_spoken = extract_items_from_library(resume_text, LANGUAGES_SPOKEN_LIBRARY)
        print("Extraction complete.")

        # Get current UTC time in ISO 8601 format
        upload_timestamp = datetime.utcnow().isoformat() + "Z"

        output_data = {
            'candidateId': f"CAND_{uuid.uuid4().hex[:12].upper()}",
            'uploadDate': upload_timestamp,
            'name': extracted_name,
            'email': contact_info['email'],
            'phoneNumber': contact_info['phone_number'],
            'skills': {
                'technical': technical_skills,
                'nonTechnical': non_technical_skills
            },
            'languages': languages_spoken if languages_spoken else "Not defined",
            'experienceSummary': experience_summary,
            'isPostGraduate': is_post_graduate
        }

        output_key = os.path.splitext(source_key)[0] + '.json'

        s3_client.put_object(
            Bucket=DESTINATION_BUCKET,
            Key=output_key,
            Body=json.dumps(output_data, indent=4),
            ContentType='application/json'
        )
        success_message = f"Successfully processed '{source_key}' and saved result to '{output_key}' in bucket '{DESTINATION_BUCKET}'."
        print(success_message)

        return {'statusCode': 200, 'body': json.dumps(success_message)}

    except Exception as e:
        print(f"ERROR: An unexpected error occurred. {e}")
        return {'statusCode': 500, 'body': json.dumps(f"An unexpected error occurred: {str(e)}")}