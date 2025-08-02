import re
import json
import random
from collections import defaultdict
from typing import Dict, List, Tuple, Optional
from name_extractor import extract_name_from_resume
from phone_extractor import extract_phone_number_from_text
from contact_extractor import extract_contact_info
from skill_scorer import score_and_categorize_skills
from resume_pipeline import process_resume

class EnhancedResumeAnalyzer:
    def __init__(self):
        self.skill_categories = {
    "Technical Skills": [
        "python", "java", "javascript", "typescript", "c++", "c#", "c", "php", "ruby", 
        "go", "rust", "swift", "kotlin", "scala", "r", "matlab", "perl", "shell", 
        "bash", "powershell", "vba", "cobol", "fortran", "assembly", "dart", "elixir",
        "haskell", "lua", "objective-c", "pascal", "prolog", "smalltalk", "tcl", "vhdl",
        
        "html", "css", "sass", "less", "bootstrap", "tailwind", "react", "angular", 
        "vue", "svelte", "jquery", "node.js", "express", "django", "flask", "fastapi",
        "spring", "laravel", "rails", "asp.net", "blazor", "next.js", "nuxt.js", 
        "gatsby", "webpack", "vite", "babel", "graphql", "rest api",
        "android", "ios", "react native", "flutter", "xamarin", "ionic", "cordova",
        "unity", "unreal engine",
        "mysql", "postgresql", "mongodb", "sqlite", "oracle", "sql server", "redis",
        "cassandra", "elasticsearch", "dynamodb", "firestore", "couchdb", "neo4j",
        "influxdb", "mariadb", "db2", "sybase", "teradata", "snowflake", "bigquery",
        
        "aws", "azure", "gcp", "google cloud", "heroku", "digitalocean", "linode",
        "cloudflare", "vercel", "netlify", "firebase", "supabase", "railway",
        
        "docker", "kubernetes", "jenkins", "gitlab ci", "github actions", "terraform",
        "ansible", "chef", "puppet", "vagrant", "helm", "istio", "prometheus",
        "grafana", "elk stack", "splunk", "nagios", "zabbix", "consul", "vault",
        
        "pandas", "numpy", "scipy", "scikit-learn", "tensorflow", "pytorch", "keras",
        "jupyter", "matplotlib", "seaborn", "plotly", "tableau", "power bi", "qlik",
        "apache spark", "hadoop", "hive", "pig", "storm", "kafka", "airflow", "mlflow",
        
        "machine learning", "deep learning", "neural networks", "nlp", "computer vision",
        "reinforcement learning", "xgboost", "lightgbm", "catboost", "opencv", "nltk", 
        "spacy", "transformers", "bert", "gpt",
        "selenium", "cypress", "jest", "mocha", "chai", "junit", "testng", "pytest",
        "unittest", "rspec", "jasmine", "karma", "protractor", "appium", "postman",
        "insomnia", "jmeter", "loadrunner", "sonarqube", "checkmarx",
        "git", "github", "gitlab", "bitbucket", "svn", "mercurial", "perforce", "cvs",
        "linux", "ubuntu", "centos", "redhat", "debian", "fedora", "suse", "windows",
        "macos", "unix", "solaris", "aix", "freebsd", "openbsd", "alpine",
        
        "jira", "confluence", "trello", "asana", "monday", "notion", "slack", "teams",
        "zoom", "basecamp", "clickup", "airtable", "smartsheet", "wrike",
        "photoshop", "illustrator", "indesign", "sketch", "figma", "adobe xd", "canva",
        "after effects", "premiere pro", "blender", "maya", "3ds max", "cinema 4d",
        "zbrush", "substance painter",
        "looker", "sisense", "pentaho", "cognos", "microstrategy", "domo", "chartio", 
        "metabase", "superset",
        "sap", "oracle erp", "dynamics 365", "salesforce", "hubspot", "pipedrive",
        "zoho", "netsuite", "workday", "servicenow", "jde", "peoplesoft",
        
        "agile", "scrum", "kanban", "waterfall", "devops", "lean", "six sigma", "itil",
        "prince2", "pmp", "safe", "xp", "tdd", "bdd", "ddd", "microservices", "mvp",
        
        
        "aws certified", "azure certified", "gcp certified", "cissp", "cism", "cisa",
        "pmp", "scrum master", "product owner", "itil", "prince2", "six sigma", "ceh",
        "oscp", "ccna", "ccnp", "ccie", "mcse", "rhce", "oracle certified"
    ],
    
    "Soft Skills": [
        "leadership", "communication", "teamwork", "problem solving", "critical thinking",
        "creativity", "adaptability", "time management", "project management", 
        "analytical thinking", "decision making", "negotiation", "presentation",
        "mentoring", "coaching", "collaboration", "innovation", "strategic planning",
        "customer service", "sales", "marketing", "public speaking", "writing",
        "teamwork", "collaboration", "cross-functional collaboration", "remote collaboration",
       "virtual teamwork", "distributed team management", "cultural sensitivity", "inclusivity",
       "diversity and inclusion", "emotional intelligence", "empathy", "social awareness",
       "relationship building", "networking", "partnership development", "alliance management",
       "community building", "consensus building", "facilitation", "mediation", "diplomacy"
    ]
}

        # Flattened skill dictionary
        self.all_skills = {}
        for category, skills in self.skill_categories.items():
            for skill in skills:
                self.all_skills[skill.lower()] = category

    def extract_candidate_name(self, text: str) -> Optional[str]:
      
        return extract_name_from_resume(text)


    def extract_phone_number(self, text: str) -> Optional[str]:
        # Allow characters commonly found in phone numbers
        return extract_phone_number_from_text(text)

    def extract_experience(self, text: str) -> Optional[str]:
        
        return None

    def extract_contact_info(self, text: str) -> Dict[str, Optional[str]]:
        return extract_contact_info(text)

    def extract_skills_with_regex(self, text: str) -> List[Tuple[str, str, int]]:
        text_lower = text.lower()
        extracted = []
        for skill, category in self.all_skills.items():
            pattern = r'\b' + re.escape(skill) + r'\b'
            count = len(re.findall(pattern, text_lower))
            if count:
                extracted.append((skill, category, count))

        compound_patterns = {
            r'\b(react\.js|reactjs)\b': ('react', 'Web Technologies'),
            r'\b(node\.js|nodejs)\b': ('node.js', 'Web Technologies'),
        }
        for pattern, (skill, category) in compound_patterns.items():
            matches = re.findall(pattern, text_lower)
            if matches:
                extracted.append((skill, category, len(matches)))
        return extracted

    def score_and_categorize_skills(self, skills: List[Tuple[str, str, int]]) -> Dict[str, List[Dict]]:
        return score_and_categorize_skills(skills)

    def generate_candidate_id(self, name: Optional[str]) -> str:
        """
        Generate a unique candidate ID consisting of the cleaned name and a random number.
        """
        candidate = re.sub(r'\W+', '', name.lower()) if name else 'unknown'
        random_number = random.randint(10000, 99999)  
        return f"candidate_{candidate}_{random_number}"

    def process_resume(self, text: str) -> Dict:
        

        return process_resume(
            text,
            self.extract_experience,
            self.generate_candidate_id,
            self.extract_skills_with_regex
        )


# === UTILITY FUNCTIONS ===

def read_resume_from_file(file_path: str) -> Optional[str]:
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            return f.read()
    except FileNotFoundError:
        print(f" File not found: {file_path}")
    except Exception as e:
        print(f" Error reading file: {e}")
    return None

def display_results(result: Dict):

    candidate = result["candidate_info"]
    skills_by_category = result["skills_by_category"]

    # Extract technical and soft skills
    technical_skills = [s['skill'] for s in skills_by_category.get("Technical Skills", [])]
    soft_skills = [s['skill'] for s in skills_by_category.get("Soft Skills", [])]

    # Build the final dictionary
    formatted_output = {
        "candidate_id": result.get("candidate_id", "N/A"),
        "name": candidate.get("name", "Not found"),
        "email": candidate.get("email", "Not found"),
        "contact number":candidate.get("phone","Not found"),
        "Technical Skills": technical_skills,
        "Soft Skills": soft_skills,
        "experience_summary": candidate.get("experience", "Not found")
    }

    # Print as formatted JSON
    print("RESUME ANALYSIS RESULTS (Formatted Output):\n")
    print(json.dumps(formatted_output, indent=4))





def main():
    

    analyzer = EnhancedResumeAnalyzer()

    file_path = input("Enter the path to the resume text file: ").strip() #S3 access get point
    file_path = file_path.strip('"').strip("'")
    
    resume_text = read_resume_from_file(file_path)
    if not resume_text:
        print("Failed to read or empty file.")
        return

    result = analyzer.process_resume(resume_text)
    display_results(result)

    output_file = f"{result['candidate_id']}.json"  #S3 access put point

    with open(output_file, 'w', encoding='utf-8') as f:
        json.dump(result, f, indent=2)
    print(f"\n Results saved to {output_file}")


if __name__ == "__main__":
    main()
