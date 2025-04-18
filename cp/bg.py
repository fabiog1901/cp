import asyncio
from .db import pool
from .models import Msg


async def pull_from_mq():
    try:
        while True:
            with pool.connection() as conn:
                with conn.transaction() as tx:
                    with conn.cursor() as cur:
                        print("Polling from MQ...")
                        cur.execute("SELECT * FROM mq LIMIT 1 FOR UPDATE SKIP LOCKED;")
                        try:
                            msg = Msg(*cur.fetchone())
                            if msg:
                                print(f"Processing {msg.msg_id}")
                                await asyncio.sleep(3)

                                cur.execute(
                                    "DELETE FROM mq WHERE msg_id = %s;",
                                    (msg.msg_id,),
                                )
                        except:
                            pass

            await asyncio.sleep(5)  # add some polling delay to avoid running too often

    except asyncio.CancelledError:
        print("Task was stopped")
