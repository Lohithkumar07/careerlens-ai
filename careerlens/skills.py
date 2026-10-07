"""Skill taxonomy, role profiles and skill extraction."""
import re
from functools import lru_cache

# skill -> (category, aliases)
SKILLS = {
    # languages
    "python": ("Languages", ["python"]),
    "java": ("Languages", ["java"]),
    "javascript": ("Languages", ["javascript", "js", "es6"]),
    "typescript": ("Languages", ["typescript", "ts"]),
    "c++": ("Languages", ["c++"]),
    "c#": ("Languages", ["c#"]),
    "go": ("Languages", ["golang"]),
    "rust": ("Languages", ["rust"]),
    "kotlin": ("Languages", ["kotlin"]),
    "swift": ("Languages", ["swift"]),
    "sql": ("Languages", ["sql"]),
    "r": ("Languages", ["r programming", "rstudio"]),
    "scala": ("Languages", ["scala"]),
    "php": ("Languages", ["php"]),
    "bash": ("Languages", ["bash", "shell scripting"]),
    # web
    "react": ("Web", ["react", "react.js", "reactjs"]),
    "next.js": ("Web", ["next.js", "nextjs"]),
    "vue": ("Web", ["vue", "vue.js"]),
    "angular": ("Web", ["angular"]),
    "html": ("Web", ["html", "html5"]),
    "css": ("Web", ["css", "css3"]),
    "tailwind": ("Web", ["tailwind", "tailwind css"]),
    "redux": ("Web", ["redux"]),
    "node.js": ("Web", ["node.js", "nodejs"]),
    "express": ("Web", ["express", "express.js", "expressjs"]),
    "django": ("Web", ["django"]),
    "flask": ("Web", ["flask"]),
    "fastapi": ("Web", ["fastapi"]),
    "spring boot": ("Web", ["spring boot", "springboot"]),
    "rest api": ("Web", ["rest api", "rest apis", "restful", "restful apis"]),
    "graphql": ("Web", ["graphql"]),
    "microservices": ("Web", ["microservices", "microservice"]),
    # ml / ai
    "machine learning": ("ML & AI", ["machine learning", "ml"]),
    "deep learning": ("ML & AI", ["deep learning", "neural networks"]),
    "nlp": ("ML & AI", ["nlp", "natural language processing"]),
    "computer vision": ("ML & AI", ["computer vision", "image classification", "object detection"]),
    "scikit-learn": ("ML & AI", ["scikit-learn", "sklearn", "scikit learn"]),
    "tensorflow": ("ML & AI", ["tensorflow"]),
    "pytorch": ("ML & AI", ["pytorch"]),
    "keras": ("ML & AI", ["keras"]),
    "transformers": ("ML & AI", ["transformers", "hugging face", "huggingface", "bert"]),
    "llm": ("ML & AI", ["llm", "llms", "large language models"]),
    "prompt engineering": ("ML & AI", ["prompt engineering"]),
    "langchain": ("ML & AI", ["langchain"]),
    "rag": ("ML & AI", ["rag", "retrieval augmented generation"]),
    "opencv": ("ML & AI", ["opencv"]),
    "xgboost": ("ML & AI", ["xgboost", "lightgbm"]),
    "mlops": ("ML & AI", ["mlops", "mlflow", "model deployment"]),
    "feature engineering": ("ML & AI", ["feature engineering"]),
    "time series": ("ML & AI", ["time series", "forecasting"]),
    "statistics": ("ML & AI", ["statistics", "hypothesis testing", "statistical modeling"]),
    # data
    "pandas": ("Data", ["pandas"]),
    "numpy": ("Data", ["numpy"]),
    "matplotlib": ("Data", ["matplotlib", "seaborn"]),
    "data visualization": ("Data", ["data visualization", "data visualisation", "dashboards"]),
    "tableau": ("Data", ["tableau"]),
    "power bi": ("Data", ["power bi", "powerbi"]),
    "excel": ("Data", ["excel", "advanced excel"]),
    "spark": ("Data", ["spark", "pyspark", "apache spark"]),
    "hadoop": ("Data", ["hadoop"]),
    "kafka": ("Data", ["kafka"]),
    "airflow": ("Data", ["airflow"]),
    "etl": ("Data", ["etl", "data pipelines", "elt"]),
    "a/b testing": ("Data", ["a/b testing", "ab testing", "experimentation"]),
    # devops / cloud
    "docker": ("DevOps & Cloud", ["docker", "containerization"]),
    "kubernetes": ("DevOps & Cloud", ["kubernetes", "k8s"]),
    "aws": ("DevOps & Cloud", ["aws", "amazon web services", "ec2", "s3"]),
    "azure": ("DevOps & Cloud", ["azure"]),
    "gcp": ("DevOps & Cloud", ["gcp", "google cloud"]),
    "terraform": ("DevOps & Cloud", ["terraform"]),
    "ci/cd": ("DevOps & Cloud", ["ci/cd", "cicd", "github actions", "jenkins", "gitlab ci"]),
    "linux": ("DevOps & Cloud", ["linux"]),
    "ansible": ("DevOps & Cloud", ["ansible"]),
    "prometheus": ("DevOps & Cloud", ["prometheus"]),
    "grafana": ("DevOps & Cloud", ["grafana"]),
    "nginx": ("DevOps & Cloud", ["nginx"]),
    "git": ("DevOps & Cloud", ["git", "github", "gitlab"]),
    # databases
    "postgresql": ("Databases", ["postgresql", "postgres"]),
    "mysql": ("Databases", ["mysql"]),
    "mongodb": ("Databases", ["mongodb", "mongo"]),
    "redis": ("Databases", ["redis"]),
    "firebase": ("Databases", ["firebase"]),
    "elasticsearch": ("Databases", ["elasticsearch", "opensearch"]),
    # security
    "penetration testing": ("Security", ["penetration testing", "pentesting", "ethical hacking"]),
    "siem": ("Security", ["siem", "splunk"]),
    "network security": ("Security", ["network security", "firewalls"]),
    "owasp": ("Security", ["owasp"]),
    "cryptography": ("Security", ["cryptography", "encryption"]),
    "incident response": ("Security", ["incident response", "threat hunting"]),
    # mobile
    "android": ("Mobile", ["android"]),
    "ios": ("Mobile", ["ios"]),
    "flutter": ("Mobile", ["flutter", "dart"]),
    "react native": ("Mobile", ["react native"]),
    # practices
    "unit testing": ("Practices", ["unit testing", "pytest", "jest", "junit"]),
}

# role -> core skills (used for gap analysis and synthetic data generation)
ROLE_PROFILES = {
    "Data Scientist": ["python", "machine learning", "statistics", "pandas", "numpy", "scikit-learn",
                       "sql", "data visualization", "matplotlib", "feature engineering",
                       "a/b testing", "time series", "xgboost"],
    "ML Engineer": ["python", "machine learning", "deep learning", "pytorch", "tensorflow", "mlops",
                    "docker", "kubernetes", "aws", "scikit-learn", "ci/cd", "fastapi",
                    "feature engineering"],
    "NLP / LLM Engineer": ["python", "nlp", "transformers", "llm", "prompt engineering", "pytorch",
                           "langchain", "rag", "fastapi", "deep learning", "elasticsearch"],
    "Computer Vision Engineer": ["python", "computer vision", "opencv", "deep learning", "pytorch",
                                 "tensorflow", "keras", "c++", "numpy", "docker"],
    "Data Analyst": ["sql", "excel", "tableau", "power bi", "python", "pandas",
                     "data visualization", "statistics", "a/b testing", "etl"],
    "Data Engineer": ["python", "sql", "spark", "airflow", "etl", "aws", "kafka", "docker",
                      "postgresql", "hadoop", "terraform"],
    "Frontend Developer": ["javascript", "typescript", "react", "html", "css", "tailwind", "next.js",
                           "redux", "git", "unit testing", "graphql"],
    "Backend Developer": ["rest api", "postgresql", "mysql", "redis", "docker", "microservices",
                          "django", "flask", "spring boot", "mongodb", "git", "java", "python"],
    "Full Stack Developer": ["javascript", "react", "node.js", "express", "mongodb", "postgresql",
                             "rest api", "html", "css", "git", "docker", "typescript", "next.js"],
    "DevOps Engineer": ["docker", "kubernetes", "aws", "terraform", "ci/cd", "linux", "ansible",
                        "prometheus", "grafana", "bash", "git", "nginx", "azure"],
    "Cybersecurity Analyst": ["penetration testing", "siem", "network security", "owasp",
                              "cryptography", "incident response", "linux", "python", "bash"],
    "Mobile Developer": ["android", "ios", "flutter", "react native", "kotlin", "swift",
                         "firebase", "rest api", "git"],
}

# role-flavoured experience phrases (give the model realistic context terms)
ROLE_PHRASES = {
    "Data Scientist": ["analyzed customer churn and built predictive models",
                       "ran hypothesis tests and communicated insights to stakeholders",
                       "engineered features and tuned model hyperparameters"],
    "ML Engineer": ["deployed models to production and monitored model drift",
                    "built training pipelines and scalable inference services",
                    "optimized model latency and automated retraining"],
    "NLP / LLM Engineer": ["fine-tuned language models for text classification and summarization",
                           "built chatbots and semantic search over documents",
                           "designed prompts and evaluated generation quality"],
    "Computer Vision Engineer": ["trained detection and segmentation models on image datasets",
                                 "built real-time video analytics pipelines",
                                 "annotated images and improved mean average precision"],
    "Data Analyst": ["built dashboards and weekly business reports",
                     "cleaned data and wrote queries to answer business questions",
                     "tracked KPIs and presented trends to management"],
    "Data Engineer": ["built batch and streaming data pipelines",
                      "designed data warehouse schemas and scheduled workflows",
                      "improved pipeline reliability and data quality checks"],
    "Frontend Developer": ["built responsive user interfaces and reusable components",
                           "improved page performance and accessibility",
                           "implemented state management and client side routing"],
    "Backend Developer": ["designed scalable services and database schemas",
                          "implemented authentication and optimized slow queries",
                          "built secure endpoints and background workers"],
    "Full Stack Developer": ["built end to end web applications from database to user interface",
                             "shipped features across client and server",
                             "integrated payments and deployed web apps"],
    "DevOps Engineer": ["automated infrastructure provisioning and deployments",
                        "managed clusters and improved system reliability",
                        "set up monitoring alerting and release pipelines"],
    "Cybersecurity Analyst": ["investigated security alerts and vulnerabilities",
                              "performed risk assessments and hardened systems",
                              "wrote incident reports and tuned detection rules"],
    "Mobile Developer": ["built and published mobile apps to app stores",
                         "implemented push notifications and offline support",
                         "optimized app startup time and battery usage"],
}


@lru_cache(maxsize=1)
def _patterns():
    compiled = {}
    for skill, (_cat, aliases) in SKILLS.items():
        alt = "|".join(re.escape(a) for a in sorted(set(aliases + [skill]), key=len, reverse=True))
        compiled[skill] = re.compile(rf"(?<![a-z0-9+#.])(?:{alt})(?![a-z0-9+#])", re.IGNORECASE)
    return compiled


def extract_skills(text: str) -> list:
    """Return the canonical skills mentioned in `text` (sorted)."""
    found = [s for s, pat in _patterns().items() if pat.search(text)]
    return sorted(found)


def category_of(skill: str) -> str:
    return SKILLS[skill][0] if skill in SKILLS else "Other"
