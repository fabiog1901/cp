import asyncio
import random

from . import runner
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
                                if msg.msg_type == "CREATE_CLUSTER":
                                    print("Processing a CREATE_CLUSTER")
                                    runner.create_cluster(
                                        msg.msg_id, msg.msg_data, msg.created_by
                                    )
                                elif msg.msg_type == "DELETE_CLUSTER":
                                    print("Processing a DELETE_CLUSTER")
                                    runner.delete_cluster(msg.msg_id, msg.msg_data)
                                elif msg.msg_type == "DEBUG":
                                    print("Processing a DEBUG")
                                    pass
                                elif msg.msg_type == "FAIL_ZOMBIE_JOBS":
                                    print("Processing a FAIL_ZOMBIE_JOBS")
                                    runner.fail_zombie_jobs()
                                else:
                                    print(f"Unknown task type requested: {msg.msg_type}")

                                cur.execute(
                                    "DELETE FROM mq WHERE msg_id = %s;",
                                    (msg.msg_id,),
                                )
                        except:
                            pass

            # add some polling delay to avoid running too often
            await asyncio.sleep(5 * random.uniform(0.7, 1.3))

    except asyncio.CancelledError:
        print("Task was stopped")
