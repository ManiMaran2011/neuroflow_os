import asyncio
from intent_analyzer import IntentAnalyzer

async def main():
    analyzer = IntentAnalyzer()

    print(await analyzer.analyze("what is maths"))
    print(await analyzer.analyze("add task buy groceries"))
    print(await analyzer.analyze("add task and remind me"))
    print(await analyzer.analyze("do it again"))

asyncio.run(main())
