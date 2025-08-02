# Resume Parser & Skill Extractor System 

This project is an end-to-end Resume Parser and Skill Extractor system built using AWS services (S3, Lambda, Bedrock), Flask, and modern NLP tools. It extracts structured candidate data from resumes (PDFs), stores the results in S3, and provides an interactive admin dashboard for analysis and reporting.

🚀 Features

📄 Upload resumes (PDF) via Flask web interface

📦 Store and retrieve resumes using Amazon S3

📊 Store metadata (filename and timestamp) in DynamoDB when resumes are uploaded to the first S3 bucket(optional)

🤖 Trigger AWS Lambda on resume upload to:

Extract text using pdfminer.six

Use Amazon Bedrock Nova Pro model to extract:

Candidate name

Experience summary

Graduation/Postgraduation qualification

Save structured output JSON to another S3 bucket

🔍 Skill and language extraction using a custom keyword-based library and basics using regex:

Categorizes technical and non-technical skills

Identifies known programming languages from text

Identifies phoneno, email using regex

🌐 Admin Dashboard:

View candidate list from JSON file in S3

Filter, search, and sort by skills, name, or summary keywords

Word cloud generation for trending skills

Bar chart showing most common programming languages

Pie chart showing postgraduate vs graduate ratio

Use Gemini 1.5 Flash for dashboard summaries

Export filtered results to CSV

🛡️ Anonymized data export for experimentation:

Uses Faker library to mask names, emails, phone numbers, and UUIDs

Admin can download anonymized dataset

🧰 Tech Stack

Backend: Flask (Python, app.py)

Cloud: AWS S3, Lambda, Bedrock (Nova Pro), DynamoDB (for upload metadata)

NLP & SDKs: pdfminer.six, boto3, re, uuid, datetime, faker

Frontend: HTML + JS Dashboard (with Chart.js / WordCloud.js)

Visualization: Word cloud, bar chart, pie chart for reports

🔑 AWS Resources Required

S3 Buckets

Lambda Function

Bedrock Model:

Nova Pro model used for extracting name, experience, education

Gemini API:

Gemini 1.5 Flash used to generate dashboard summary insights

⚙️ Setup Instructions

Install Python Requirements:

pip install -r requirements.txt

Configure AWS CLI:

aws configure

Run Flask App Locally:

python app.py

Deploy Lambda Function:

Zip dependencies and Lambda script

Upload via AWS Console or CLI

📊 Dashboard Visualizations

📈 Bar Chart – Most commonly used programming languages

🌐 Word Cloud – Frequent keywords and skills

🥧 Pie Chart – Postgraduate vs Graduate ratio

💡 Gemini Summary – Insightful summary using Gemini 1.5 Flash

🧠 Future Improvements

Add tagging, feedback & rating system

Integrate resume ranking & ML scoring


