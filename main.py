"""Math Fighter - a math fighting game for kids.

Run with:  python main.py
In a web browser (pygbag) this file starts the browser version instead;
build it with:  python3 tools/build_web.py     (writes build/web/)
"""
import sys

import pygame  # noqa: F401  (imported here so pygbag loads pygame for the web build)

if sys.platform == "emscripten":
    import asyncio

    from mathfighter.game import Game

    async def web_main():
        await Game().run_web()

    asyncio.run(web_main())
else:
    from mathfighter.game import main

    if __name__ == "__main__":
        main()
