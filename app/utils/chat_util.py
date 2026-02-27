# 角色名称，提取为常量，避免混乱
ROLE_NAMES = ("User", "Assistant", "System");

# 构建与模型交互所需的输入对象
def create_chat_history(context, new_user_message: str, system_prompt: str = ""):
    messages = []
    messages.append({"role": "system", "content": system_prompt});
    if context:
        for line in context.split('\n'):
            if line.startswith(f"{ROLE_NAMES[0]}: "):
                messages.append({"role": "user", "content": line[ROLE_NAMES[0].__len__():]})
            elif line.startswith(f"{ROLE_NAMES[1]}: "):
                messages.append({"role": "assistant", "content": line[ROLE_NAMES[1].__len__():]})
    messages.append({"role": "user", "content": new_user_message});
    return messages;

def get_system_prompt(connection, model_id: str):
    cursor = connection.cursor()
    try:
        query = """
        SELECT avatar_system_prompt 
        FROM avatars 
        WHERE avatar_id = %s;
        """
        cursor.execute(query, (model_id,))
        result = cursor.fetchone()
        print("system prompt: ", result);
        if result:
            return result[0]
        else:
            return ""
    except Exception as e:
        print(f"An error occurred: {e}")
        return ""
    finally:
        cursor.close()

# 构建缓存到Redis中的对象:
def create_redis_cache(context: str, user_message: str, response_message: str):
    #存入Redis的对象
    new_context = context + f"\n{ROLE_NAMES[0]}: {user_message}\n{ROLE_NAMES[1]}: {response_message}";
    return new_context;