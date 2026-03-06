"""应用主入口。"""

from __future__ import annotations

import asyncio
import logging

from crawlers.binance_ws import BinancePriceCrawler
from crawlers.news_rss import NewsRSSCrawler
from crawlers.price_history import PriceHistoryRecorder
from redis_client import RedisClient
from scheduler import TaskScheduler


def setup_logging() -> None:
    """初始化日志配置。"""
    logging.basicConfig(
        level=logging.INFO,
        format="%(asctime)s | %(levelname)s | %(name)s | %(message)s",
    )


async def run() -> None:
    """启动所有数据任务。"""
    setup_logging()
    logger = logging.getLogger(__name__)

    redis_client = RedisClient()
    history_recorder = PriceHistoryRecorder(redis_client)
    news_crawler = NewsRSSCrawler(redis_client)
    price_crawler = BinancePriceCrawler(redis_client)
    scheduler = TaskScheduler(history_recorder, news_crawler)

    try:
        # 启动前先检查 Redis。
        await redis_client.ping()
        logger.info("Redis 连接成功")

        # 启动调度器并先执行一次新闻抓取。
        scheduler.start()
        await news_crawler.run_once()

        # 实时价格任务会持续运行。
        await price_crawler.run()
    except asyncio.CancelledError:
        logger.info("收到取消信号，准备退出")
    finally:
        scheduler.stop()
        await redis_client.close()


if __name__ == "__main__":
    try:
        asyncio.run(run())
    except KeyboardInterrupt:
        logging.getLogger(__name__).info("程序已手动中断")
