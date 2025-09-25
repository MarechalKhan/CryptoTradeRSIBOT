import os
from dotenv import load_dotenv, find_dotenv

print("CWD (pasta atual):", os.getcwd())
print("Arquivos na pasta atual:", os.listdir(os.getcwd()))
env_path = find_dotenv(usecwd=True)
print(".env encontrado por find_dotenv():", repr(env_path))

if env_path:
    try:
        with open(env_path, "r", encoding="utf-8") as f:
            content = f.read()
        print("\n--- Conteúdo bruto do .env (mostrado abaixo) ---")
        print(content)
        print("--- fim do conteúdo ---\n")
    except Exception as e:
        print("Erro ao abrir .env:", e)
else:
    print("Nenhum .env encontrado pela função find_dotenv()")