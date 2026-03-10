try:
    import os
    import sys
    import subprocess
    from telethon import TelegramClient, events, sync
    from pathlib import Path

    CWD = Path('/Users/joel/.connect_r2d2')
    TIMEOUT_SEC = 600
    API_ID = sys.argv[1]
    API_HASH = sys.argv[2]
    PHONE = sys.argv[3]
    BOT_USERNAME = sys.argv[4]

#    print(f'API_ID: {API_ID}', flush=True)
#    print(f'API_HASH: {API_HASH}', flush=True)
#    print(f'PHONE: {PHONE}', flush=True)
#    print(f'BOT_USERNAME: {BOT_USERNAME}', flush=True)
#
#    # Delete old logs.
#    os.system(f"rm -f {CWD/'logs'/'r2bot.out.log'}")
#    os.system(f"rm -f {CWD/'logs'/'r2bot.err.log'}")

    # Create client.
    client = TelegramClient(CWD/'userbot_session', API_ID, API_HASH)

    # Command handler.
    def handle_cmd(cmd):
        global TIMEOUT_SEC

        # Check length of command.
        len_cmd = len(cmd)
        if len_cmd < 2:
            err_msg = f'❌ Command too short (len={len_cmd}).'
            print(err_msg, flush=True)
            return [err_msg]

        # Determine return type.
        if not cmd[0] in ['0', '1', '2', '3', '4', '5']:
            err_msg = f'''❌ First character must be a number indicating the return type:
    0: returnvalue
    1: stdout
    2: stderr
    3: set timeout [s]
    4: write to a.txt
    5: append to a.txt'''
            print('❌ Invalid command.', flush=True)
            return [err_msg]

        return_type = int(cmd[0])
        cmd = cmd[1:]

        # Set timeout.
        if return_type == 3:
            try:
                TIMEOUT_SEC = int(cmd)
                return_msg = f'TIMEOUT_SEC: {TIMEOUT_SEC}'
                print('✅ Success.', flush=True)
                return [return_msg]
            except:
                err_msg = f'❌ Error modifying timeout. TIMEOUT_SEC: {TIMEOUT_SEC}.'
                print(err_msg, flush=True)
                return [err_msg]

        elif return_type == 4:
            try:
                with open(CWD/'a.txt', 'w') as f:
                    f.write(cmd + '\n')
                print('✅ Success.', flush=True)
                return ['✅ Success.']
            except:
                err_msg = f'❌ Error writing to a.txt.'
                print(err_msg, flush=True)
                return [err_msg]

        elif return_type == 5:
            try:
                with open(CWD/'a.txt', 'a') as f:
                    f.write(cmd + '\n')
                print('✅ Success.', flush=True)
                return ['✅ Success.']
            except:
                err_msg = f'❌ Error appending to a.txt.'
                print(err_msg, flush=True)
                return [err_msg]

        else:
            # Execute command.
            try:
                ## Authorize request.
                #user_id = str(update.effective_user.id)
                #if user_id != CHAT_ID:
                #    return f'Not authorized (id: "{user_id}", allowed: "{CHAT_ID}").'

                result = subprocess.run(
                    cmd.split(),
                    capture_output=True,
                    text=True,
                    encoding='utf-8',
                    errors='replace',       # avoid UnicodeDecodeError crashes
                    cwd=CWD,                # necessary when launced via launchctl
                    timeout=TIMEOUT_SEC,
                    check=False             # don't raise exception on non-zero exit
                )

                # Get return text.
                if return_type == 0:
                    return_text = str(result.returncode)
                elif return_type == 1:
                    return_text = result.stdout
                else:
                    return_text = result.stderr
                print('✅ Command executed.', flush=True)

            except subprocess.TimeoutExpired:
                err_msg = f'❌ Time-out after {TIMEOUT_SEC}s'
                print(err_msg, flush=True)
                return [err_msg]
            except Exception as e:
                err_msg = f'❌ Exception: {str(e)}'
                print(err_msg, flush=True)
                return [err_msg]

        # Send return text. Split long text into separate messages.
        if return_text == '':
            return ['[no return text]']

        return_msgs = []
        while True:
            if len(return_text) < 4096:
                if len(return_text) > 0:
                    return_msgs.append(return_text)
                break

            send_text = return_text[0:4096]
            return_text = return_text[4096:]
            return_msgs.append(send_text)

        return return_msgs


    async def main():
        # Listen for responses from bot.
        @client.on(events.NewMessage(from_users=BOT_USERNAME))
        async def handler(event):
            cmd = event.message.text.strip()
            print(f'Command received: {cmd}', flush=True)
            return_msgs = handle_cmd(cmd)
            #print(return_msgs, flush=True)
            for msg in return_msgs:
                #await event.reply(msg)
                await client.send_message(bot_entity, msg)

        await client.run_until_disconnected()

    # Run the client.
    with client:
        # Start client (will prompt for login code if needed).
        client.start(phone=PHONE)
        
        # Get entity for bot (start chat if not already open).
        bot_entity = client.get_entity(BOT_USERNAME)
        
        # Send ready message to bot.
        client.send_message(bot_entity, 'ready')
        print(f'✅ R2-D2 connected. Waiting for commands. Press ⌘+Q to quit.', flush=True)
        
        # Main loop.
        client.loop.run_until_complete(main())

except Exception as e:
    print(f'❌ Uncaught exception: {str(e)}', flush=True)
    sys.exit(0) # exit cleanly to hopefully prevent restart
