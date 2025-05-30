import psycopg
from pydantic import BaseModel


class ModelSettings(BaseModel):
    distance:int
    chunks:int
    model:str

async def get_users_model_settings(
    conn: psycopg.AsyncConnection, user_id: int):
    select_query = "SELECT (distance,chunks,model) FROM user_data.model_settings WHERE user_id = %s"
    async with conn.cursor() as cur:
        await cur.execute(select_query,
        (user_id,),
    )

        results = await cur.fetchone()
        if results:
            saved_settings = results[0]
            settings = ModelSettings(
                distance=int(saved_settings[0]),
                chunks=int(saved_settings[1]),
                model=saved_settings[2]
            )
            return settings
    return None

async def add_new_model_settings(
    conn: psycopg.AsyncConnection, user_id:int,settings:ModelSettings):
    insert_query = "INSERT INTO user_data.model_settings (user_id,distance,chunks,model) VALUES (%s,%s,%s,%s)"
    async with conn.cursor() as cur:
        await cur.execute(
            insert_query,
            (user_id,settings.distance,settings.chunks,settings.model)
        )

    await conn.commit()

async def update_users_model_settings(
    conn: psycopg.AsyncConnection, user_id: int, settings:ModelSettings):
    update_query = "UPDATE user_data.model_settings SET distance=%s, chunks=%s,model=%s WHERE user_id = %s"
    async with conn.cursor() as cur:
        await cur.execute(
            update_query,
            (settings.distance,settings.chunks,settings.model,user_id)
        )
        
    await conn.commit()