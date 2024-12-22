from setuptools import setup, find_packages

setup(
    name="property_parser",
    version="0.1.0",
    packages=find_packages(),
    install_requires=[
        "python-telegram-bot==20.7",
        "telethon==1.33.1",
        "python-dotenv==1.0.0",
        "SQLAlchemy==2.0.23",
        "aiosqlite==0.19.0",
    ],
    python_requires=">=3.12",
)
