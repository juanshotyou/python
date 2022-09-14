from jinja2 import Template

# This file stores all the Adaptive cards used by the ChatBot.

TMP_HELLO = """{
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

TMP_START = """{
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
                "id": "location"
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

TMP_WEATHER = """{
    "contentType": "application/vnd.microsoft.card.adaptive",
    "content": {
        "type": "AdaptiveCard",
        "$schema": "http://adaptivecards.io/schemas/adaptive-card.json",
        "version": "1.2",
        "body": [
            {
                "type": "Container",
                "items": [
                    {
                        "type": "TextBlock",
                        "text": "Weather in {{ location }} now:",
                        "wrap": true,
                        "fontType": "Default",
                        "size": "Large",
                        "weight": "Bolder"
                    }
                ]
            },
            {
                "type": "ColumnSet",
                "columns": [
                    {
                        "type": "Column",
                        "width": "stretch",
                        "items": [
                            {
                                "type": "TextBlock",
                                "text": "**Sky**: {{ w_main }}",
                                "wrap": true,
                                "horizontalAlignment": "Left",
                                "fontType": "Default"
                            },
                            {
                                "type": "TextBlock",
                                "text": "**Outdoor**: {{ w_desc }}",
                                "wrap": true
                            },
                            {
                                "type": "TextBlock",
                                "text": "**Temperature**: {{ tmp }} °C",
                                "wrap": true
                            },
                            {
                                "type": "TextBlock",
                                "text": "**Feels like**: {{ tmp_feel }} °C",
                                "wrap": true
                            },
                            {
                                "type": "TextBlock",
                                "text": "**Day range**: {{ tmp_min }} °C - {{ temp_max }} °C",
                                "wrap": true
                            },
                            {
                                "type": "TextBlock",
                                "text": "**Atmospheric pressure**: {{ pressure }} hPa",
                                "wrap": true
                            },
                            {
                                "type": "TextBlock",
                                "text": "**Humidity**: {{ humidity }} %",
                                "wrap": true
                            }
                        ]
                    }
                ]
            }
        ]
    }
}"""

J2_HELLO = Template(TMP_HELLO)
J2_START = Template(TMP_START)
J2_WEATHER = Template(TMP_WEATHER)
