# This file stores all the Adaptive cards used by the ChatBot.

hello = """{
    "contentType": "application/vnd.microsoft.card.adaptive",
    "content": {
        "type": "AdaptiveCard",
        "body": [
            {
                "type": "TextBlock",
                "size": "Medium",
                "weight": "Bolder",
                "text": "Welcome to the Weather ChatBot"
            },
            {
                "type": "ColumnSet",
                "columns": [
                    {
                        "type": "Column",
                        "items": [
                            {
                                "type": "Image",
                                "style": "Person",
                                "url": "https://avatar-prod-us-east-2.webexcontent.com/Avtr~V1~cca99e60-7e42-4fa8-ab73-90635eb378a6/V1~85dc04dd38e5511315d91ce8be030b01debfacf69bb8641687d54ec9523fc1b3~2897f018607249cfa9d12f8f1afd609a?quarantineState=evaluating",
                                "size": "Medium"
                            }
                        ],
                        "width": "auto"
                    },
                    {
                        "type": "Column",
                        "width": "stretch",
                        "items": [
                            {
                                "type": "TextBlock",
                                "text": "You can ask the bot for weather info for any city by sending it the name of the city. \\n\\nOnly single word locations are currently supported. Type 'help' or 'hello' to see this message again. \\n\\nTo start, type 'start' and press enter.",
                                "wrap": true
                            }
                        ]
                    }
                ]
            }
        ],
        "$schema": "http://adaptivecards.io/schemas/adaptive-card.json",
        "version": "1.2"
    }
}"""

start = """{
    "contentType": "application/vnd.microsoft.card.adaptive",
    "content": {
        "type": "AdaptiveCard",
        "$schema": "http://adaptivecards.io/schemas/adaptive-card.json",
        "version": "1.2",
        "body": [
            {
                "type": "TextBlock",
                "text": "Get current weather",
                "wrap": true,
                "size": "Large",
                "weight": "Bolder"
            },
            {
                "type": "TextBlock",
                "text": "Enter the name of a location:"
            },
            {
                "type": "Input.Text",
                "placeholder": "e.g. Lisbon, Zagreb, Baguley, etc",
                "id": "1"
            },
            {
                "type": "ActionSet",
                "actions": [
                    {
                        "type": "Action.Submit",
                        "title": "Send",
                        "style": "positive",
                        "id": "2"
                    }
                ]
            }
        ]
    }
}"""
