✅ 1. Use a Pretrained API to Infer Names from Text
(Example: Bedrock amazon nova pro model)

🔷 Pros:
✅ No deployment hassle (no large models in Lambda)

✅ Faster development, no packaging nightmare

✅ Always access to updated models

✅ Can scale independently of your Lambda

🔴 Cons:
❌ Requires external network calls (slightly slower per call)

❌ Dependent on third-party APIs or uptime

❌ May have cost/usage limits (if using hosted inference APIs)

✅ 2. Fine-tune and Deploy Model inside AWS Lambda
(Example: custom spaCy or HuggingFace model zipped and used inside Lambda)

🔷 Pros:
✅ Fully offline and self-contained

✅ Custom-trained for your resume format → higher accuracy

✅ No external latency or dependency

🔴 Cons:
❌ Lambda storage limit = 250 MB unzipped (HuggingFace BERT = 400+ MB) → spaCy may work with compression

❌ Cold starts + slow inference if not optimized

❌ Difficult to package all dependencies (e.g. torch, transformers) with native binaries