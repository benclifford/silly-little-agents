### ==== pretend this bit is in the academy standard library ==== ###

import asyncio
from academy.agent import Agent, action
from academy.manager import Manager
from academy.exchange import LocalExchangeFactory, RedisExchangeFactory
from concurrent.futures import ThreadPoolExecutor, ProcessPoolExecutor

import logging
logger = logging.getLogger(__name__)

class LogHandler(logging.Handler):
    def __init__(self, where, who):
        self.where = where
        self.who = who
        super().__init__()

    def emit(self, record):
        if record.__dict__.get("academy.agent_id", None) != self.who \
           and record.__dict__.get("academy.src", None) != self.who \
           and record.__dict__.get("academy.dest", None) != self.who \
           and record.__dict__.get("academy.mailbox_id", None) != self.who:
            return

        d={}
        d['formatted'] = self.format(record)
        for k, v in record.__dict__.items():
            try:
                d[k] = str(v)
            except Exception as e:
                d[k] = f'Unrepresentable: {e!r}'
        self.where.append(d)

class LogAgent(Agent):

  async def agent_on_startup(self):
    logger.info("log agent startup... about to call superclass startup", extra={"academy.agent_id": self.agent_id})
    self.interesting_logs = []
    root = logging.getLogger()
    root.addHandler(LogHandler(self.interesting_logs, self.agent_id))

    await super().agent_on_startup()

  @action
  async def get_interesting_logs(self):
    return self.interesting_logs
