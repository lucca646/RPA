import subprocess

# Exécute la commande ngrok status pour obtenir les tunnels actifs
try:
    output = subprocess.check_output(["ngrok", "status"], universal_newlines=True)
    print(output)
except subprocess.CalledProcessError as e:
    print(f"Erreur : {e}")

# Vous pouvez également analyser la sortie pour extraire les URL des tunnels actifs
