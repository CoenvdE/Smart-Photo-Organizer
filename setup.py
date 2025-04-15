from setuptools import setup, find_packages

setup(
    name="smart-photo-organizer",
    version="0.1.0",
    description="AI-powered tool for organizing photos by content",
    author="AI Photo Organizer Team",
    author_email="example@example.com",
    packages=find_packages(),
    install_requires=[
        "google-auth-oauthlib>=1.0.0",
        "google-api-python-client>=2.89.0",
        "google-auth-httplib2>=0.1.0",
        "pandas>=2.0.3",
        "openpyxl>=3.1.2",
        "Pillow>=10.0.0",
        "python-dotenv>=1.0.0",
        "openai>=1.2.0",
        "tqdm>=4.65.0",
        "pydantic>=2.0.3"
    ],
    entry_points={
        'console_scripts': [
            'photo-organizer=src.main:main',
        ],
    },
    python_requires=">=3.8",
    classifiers=[
        "Development Status :: 3 - Alpha",
        "Intended Audience :: End Users/Desktop",
        "License :: OSI Approved :: MIT License",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
    ],
) 