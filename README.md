# Sentiment Analysis Based on GPT-3.5
[![License](https://img.shields.io/github/license/SimengLi1998/SentimentAnalysis)](https://github.com/SimengLi1998/SentimentAnalysis/blob/master/LICENSE)
![Python](https://img.shields.io/badge/python-3.8+-blue.svg)

Multitask Sentiment Analysis Based on GPT-3.5

![image](https://github.com/SimengLi1998/SentimentAnalysis/assets/87021559/56e39a24-199c-4299-bf09-547ac8368892)
![image](https://github.com/SimengLi1998/SentimentAnalysis/assets/87021559/e8ece483-5534-4267-afe2-3bc197bd613e)

## Overview
The Sentiment Analysis System is designed to analyze user comments on products, extracting sentiment orientation, intensity, intention, keywords, and other useful information. This project is suitable for various types of user feedback analysis, such as advice, complaints, bug reports, and more. The system supports multi-language text input and provides detailed sentiment analysis results, helping businesses better understand user needs and improve their products.

## Features
- Sentiment Analysis: Identifies the sentiment orientation (positive, neutral, negative) and intensity of comments.
- Intention Recognition: Analyzes the intention categories of user comments (e.g., advertisement issues, refund requests).
- Keyword Extraction: Extracts key phrases and words from user comments.
- Multi-language Support: Supports analysis and processing of comments in multiple languages.

Request Post:  [http://xxx:8800/service/review_analysis](http://xxx:8800/service/review_analysis)

## Input Data Example

      {
         "commentId": 1,
         "content": "Ads won't load, the game is always lagging; I'm planning to uninstall it, please issue a refund."
      }

## Input Data Example

      {
              "commentId":1, 
              "result":{
                      "sentiment": "negative", 
                      "intensity": "-0.8",
                      "intention": [1,4], 
                      "keywords": {
                          "1": ["game lagging", "Ads won't load"],
                          "4": ["issue a refun"]
                      }  
              } ,
              "status": 1  
      }

### Usage

1. Clone the project to your local machine:
    ```bash
    git clone https://github.com/SimengLi1998/SentimentAnalysis.git
    ```

2. Install dependencies:
    ```bash
    cd SentimentAnalysis
    pip install -r requirements.txt
    ```

3. Run the system:
    ```bash
    python main.py pro
    ```

### License
This project is licensed under the [MIT License](LICENSE).
