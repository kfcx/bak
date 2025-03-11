# coding:utf-8

from app.cmdline import main
import nest_asyncio

if __name__ == '__main__':
    nest_asyncio.apply()
    main()
