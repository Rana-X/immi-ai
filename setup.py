from setuptools import setup, find_packages

setup(
    name="rag_visa",
    version="0.1",
    packages=find_packages(),
    install_requires=[
        "openai>=1.12.0",
        "pinecone-client==3.0.0",
        "python-dotenv==1.0.0",
        "PyPDF2==3.0.1",
        "scikit-learn>=1.0.2",
        "numpy>=1.21.0",
        "fastapi==0.109.0",
        "uvicorn==0.27.0",
        "pydantic==2.5.3",
    ],
) 