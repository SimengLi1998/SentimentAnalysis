# SentimentAnalysis
Multitask Sentiment Analysis Based on GPT-3.5

Request Post:  [http://xxx:8800/service/review_analysis](http://xxx:8800/service/review_analysis)

Input Data Example： 

      {
         "commentId": 1,
         "content": "Ads won't load, the game is always lagging; I'm planning to uninstall it, please issue a refund."
      }

Input Data Example：

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

