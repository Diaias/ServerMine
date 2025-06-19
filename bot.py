import discord
import psutil
import subprocess
import asyncio
import socket
from discord.ext import commands

TOKEN = "TOKEN DO BOT"  

intents = discord.Intents.default()
intents.message_content = True

bot = commands.Bot(command_prefix="!", intents=intents)

def busca_ip():
    hostname = socket.gethostname()
    ips = socket.gethostbyname_ex(hostname)[2]
    valid_ips = [ip for ip in ips if not ip.startswith("127.")]
    return valid_ips[0] if valid_ips else "IP não encontrado"

def rodando(nome_jar="purpur-1.21.1-2329.jar"):
    for proc in psutil.process_iter(['name', 'cmdline']):
        try:
            if "java" in proc.info['name'].lower() and nome_jar in " ".join(proc.info['cmdline']):
                return True
        except (psutil.NoSuchProcess, psutil.AccessDenied):
            continue
    return False

def get_online_players_from_log(log_path="logs/latest.log"):
    jogadores = set()
    try:
        with open(log_path, "r", encoding="utf-8") as f:
            for linha in f:
                if "joined the game" in linha:
                    nome = linha.split("]: ")[1].split(" joined the game")[0].strip()
                    jogadores.add(nome)
                elif "left the game" in linha:
                    nome = linha.split("]: ")[1].split(" left the game")[0].strip()
                    jogadores.discard(nome)
        return jogadores
    except Exception as e:
        print("Erro ao ler log:", e)
        return set()

@bot.event
async def on_ready():
    ip = busca_ip()

    subprocess.Popen(["java", "-Xmx12G", "-jar", "purpur-1.21.1-2329.jar", "nogui"])

    canal = bot.get_channel(1385103580364669148)
    mensagem = await canal.fetch_message(1385108283118977115)

    ultimo_status = None

    while True:

        status_atual = "ONLINE" if rodando() else "OFFLINE"

        if status_atual != ultimo_status:
            ultimo_status = status_atual

        if status_atual == "ONLINE":
            jogadores = get_online_players_from_log()
            texto_jogadores = ", ".join(jogadores) if jogadores else "0"
            await mensagem.edit(
                content=(
                    f">>> **Status** \n\n"
                    f"Servidor está: **ONLINE**    :green_circle:\n\n"
                    f"Online {len(jogadores)}/20\n\n"
                    f"IP do Server: `{ip}:25565`"
                )
            )
        else:
            await mensagem.edit(
                content=f">>> **Status** \n\nServidor está: **OFFLINE**   :red_circle:\n\n"
            )

        await asyncio.sleep(10)

bot.run(TOKEN)