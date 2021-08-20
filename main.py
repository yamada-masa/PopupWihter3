import asyncio
import json
import random
from uuid import uuid4

import websockets

EVENTS = [
    "AdditionalContentLoaded",
    "AgentCommand",
    "AgentCreated",
    "ApiInit",
    "AppPaused",
    "AppResumed",
    "AppSuspended",
    "AwardAchievement",
    "BlockBroken",
    "BlockPlaced",
    "BoardTextUpdated",
    "BossKilled",
    "CameraUsed",
    "CauldronUsed",
    "ChunkChanged",
    "ChunkLoaded",
    "ChunkUnloaded",
    "ConfigurationChanged",
    "ConnectionFailed",
    "CraftingSessionCompleted",
    "EndOfDay",
    "EntitySpawned",
    "FileTransmissionCancelled",
    "FileTransmissionCompleted",
    "FileTransmissionStarted",
    "FirstTimeClientOpen",
    "FocusGained",
    "FocusLost",
    "GameSessionComplete",
    "GameSessionStart",
    "HardwareInfo",
    "HasNewContent",
    "ItemAcquired",
    "ItemCrafted",
    "ItemDestroyed",
    "ItemDropped",
    "ItemEnchanted",
    "ItemSmelted",
    "ItemUsed",
    "JoinCanceled",
    "JukeboxUsed",
    "LicenseCensus",
    "MascotCreated",
    "MenuShown",
    "MobInteracted",
    "MobKilled",
    "MultiplayerConnectionStateChanged",
    "MultiplayerRoundEnd",
    "MultiplayerRoundStart",
    "NpcPropertiesUpdated",
    "OptionsUpdated",
    "performanceMetrics",
    "PackImportStage",
    "PlayerBounced",
    "PlayerDied",
    "PlayerJoin",
    "PlayerLeave",
    "PlayerMessage",
    "PlayerTeleported",
    "PlayerTransform",
    "PlayerTravelled",
    "PortalBuilt",
    "PortalUsed",
    "PortfolioExported",
    "PotionBrewed",
    "PurchaseAttempt",
    "PurchaseResolved",
    "RegionalPopup",
    "RespondedToAcceptContent",
    "ScreenChanged",
    "ScreenHeartbeat",
    "SignInToEdu",
    "SignInToXboxLive",
    "SignOutOfXboxLive",
    "SpecialMobBuilt",
    "StartClient",
    "StartWorld",
    "TextToSpeechToggled",
    "UgcDownloadCompleted",
    "UgcDownloadStarted",
    "UploadSkin",
    "VehicleExited",
    "WorldExported",
    "WorldFilesListed",
    "WorldGenerated",
    "WorldLoaded",
    "WorldUnloaded",
]


async def mineproxy(websocket, path):
    print("Connected")

    msg = {
        "header": {
            "version": 1,
            "requestId": "",
            "messageType": "commandRequest",
            "messagePurpose": "subscribe",
        },
        "body": {"eventName": "PlayerMessage"},
    }
    await websocket.send(json.dumps(msg))

    """
    for e in EVENTS:
        msg["header"]["requestId"] = str(uuid4())
        msg["body"]["eventName"] = e
        await websocket.send(
            json.dumps(msg)
        )
    """

    async def send(cmd):
        await websocket.send(
            json.dumps(
                {
                    "header": {
                        "version": 1,
                        "requestId": str(uuid4()),
                        "messagePurpose": "commandRequest",
                        "messageType": "commandRequest",
                    },
                    "body": {
                        "version": 1,
                        "commandLine": cmd,
                        "origin": {"type": "player"},
                    },
                }
            )
        )

    async def stage_reset():
        x = random.randint(1, 10)
        z = random.randint(1, 10)

        await send("/fill -5 5 13 4 7 22 air")
        await send("/fill -5 6 13 4 6 22 soul_sand")
        await send(f"/setblock {-5 + x} 5 {13 + z} soul_sand")

    async def user_init(name: str):
        cmds = [
            "/give {} netherite_sword 1",
            "/give {} bow 1",
            "/give {} enchanted_golden_apple 64",
            '/give {} skull 128 1 {"minecraft:can_place_on":{"blocks":["soul_sand"]}}',
            "/give {} netherite_helmet 1",
            "/give {} netherite_chestplate 1",
            "/give {} netherite_leggings 1",
            "/give {} netherite_boots 1",
            "/give {} arrow 64",
        ]

        for cmd in cmds:
            await send(cmd.format(name))

    try:
        async for msg in websocket:
            print(msg)
            msg = json.loads(msg)
            if msg["body"].get("eventName", "") == "PlayerMessage":
                text = msg["body"]["properties"]["Message"]
                if text == "stage-reset":
                    await stage_reset()
                elif text == "user-init":
                    player_name = msg["body"]["properties"].get("Sender")
                    await user_init(player_name)

    except websockets.ConnectionClosedError:
        print("Disconnected")


start_server = websockets.serve(mineproxy, port=19131)
print("/connect localhost:19132")
asyncio.get_event_loop().run_until_complete(start_server)
asyncio.get_event_loop().run_forever()
