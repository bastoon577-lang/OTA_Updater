import tkinter as tk
from tkinter import ttk, filedialog
import socket
import sys
import os
import hashlib
import random
import threading

# Commands
FLASH = 0
SPIFFS = 100
AUTH = 200

def update_progress(progress, output=print, progress_callback=None):
    barLength = 60
    status = ""
    if isinstance(progress, int):
        progress = float(progress)
    if not isinstance(progress, float):
        progress = 0
        status = "Erreur : Doit être un flottant\r\n"
    if progress < 0:
        progress = 0
        status = "Stop...\r\n"
    if progress >= 1:
        progress = 1
        status = "Fait...\r\n"
    
    # Mise à jour de la Progressbar Tkinter en tâche de fond (via le thread principal)
    if progress_callback:
        progress_callback(progress * 100)

def update(remoteAddr, filename, localAddr = "0.0.0.0", remotePort = 8266, localPort = random.randint(10000,60000), password = "", command = FLASH, output = print, progress_callback = None, finish_callback = None):
    # Create a TCP/IP socket
    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    server_address = (localAddr, localPort)
    output(f"Démarrage sur {str(server_address[0])}:{str(server_address[1])}")
    try:
        sock.bind(server_address)
        sock.listen(1)
    except Exception as err:
        output(err)
        output("Erreur : L'écoute à échouée")
        if finish_callback: finish_callback(False)
        return 1

    if ( os.path.isfile(filename + '.signed') ):
        filename = filename + '.signed'
        file_check_msg = 'Fichier de mise à jour détecté. %s sera chargé à la place.' % (filename)
        output(file_check_msg + '\n')
    
    content_size = os.path.getsize(filename)
    f = open(filename,'rb')
    file_md5 = hashlib.md5(f.read()).hexdigest()
    f.close()
    output(f"Taille du fichier : {content_size} Ko")
    message = '%d %d %d %s\n' % (command, localPort, content_size, file_md5)

    output(f"Envois d'une invitation à : {remoteAddr}")
    sock2 = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    remote_address = (remoteAddr, int(remotePort))
    
    try:
        # Forçage de la résolution DNS avant de créer le tuple d'adresse
        resolved_ip = socket.gethostbyname(remoteAddr)
        remote_address = (resolved_ip, int(remotePort))
        output(f"Hostname résolu avec succès -> IP : {resolved_ip}")
    except socket.gaierror:
        output(f"Erreur : Impossible de trouver l'appareil '{remoteAddr}'.")
        output("Erreur : Vérifiez le nom, l'adresse IP ou la connexion réseau.")
        sock2.close()
        if finish_callback: finish_callback(False)
        return 1
    
    sock2.sendto(message.encode(), remote_address)
    sock2.settimeout(10)
    try:
        data = sock2.recv(128).decode()
    except Exception:
        output("Erreur : Pas de réponse de l'équipement")
        sock2.close()
        if finish_callback: finish_callback(False)
        return 1
    if (data != "OK"):
        if(data.startswith('AUTH')):
            nonce = data.split()[1]
            cnonce_text = '%s%u%s%s' % (filename, content_size, file_md5, remoteAddr)
            cnonce = hashlib.md5(cnonce_text.encode()).hexdigest()
            passmd5 = hashlib.md5(password.encode()).hexdigest()
            result_text = '%s:%s:%s' % (passmd5 ,nonce, cnonce)
            result = hashlib.md5(result_text.encode()).hexdigest()
            output("Authentification...")
            message = '%d %s %s\n' % (AUTH, cnonce, result)
            sock2.sendto(message.encode(), remote_address)
            sock2.settimeout(10)
            try:
                data = sock2.recv(32).decode()
            except Exception:
                output("Erreur : Pas de réponse lors de l'authentification")
                sock2.close()
                if finish_callback: finish_callback(False)
                return 1
            if (data != "OK"):
                output(f"Erreur : {data}")
                sock2.close()
                if finish_callback: finish_callback(False)
                return 1
            output("OK\n")
        else:
            output(f"Erreur : Mauvaise réponse : {data}")
            sock2.close()
            if finish_callback: finish_callback(False)
            return 1
    sock2.close()

    output("Attente de l'équipement...")
    try:
        sock.settimeout(10)
        connection, client_address = sock.accept()
        sock.settimeout(None)
        connection.settimeout(None)
    except Exception:
        output("Erreur : Pas de réponse de l'équipement")
        sock.close()
        if finish_callback: finish_callback(False)
        return 1

    received_ok = False

    try:
        f = open(filename, "rb")
        update_progress(0, output=output, progress_callback=progress_callback)
        offset = 0
        while True:
            chunk = f.read(1460)
            if not chunk: break
            offset += len(chunk)
            update_progress(offset/float(content_size), output=output, progress_callback=progress_callback)
            connection.settimeout(10)
            try:
                connection.sendall(chunk)
                if connection.recv(32).decode().find('O') >= 0:
                    received_ok = True
            except Exception:
                output("\nErreur")
                connection.close()
                f.close()
                sock.close()
                if finish_callback: finish_callback(False)
                return 1

        output("\nAttente du résultat...")
        try:
            connection.settimeout(60)
            received_ok = False
            received_error = False
            while not (received_ok or received_error):
                reply = connection.recv(64).decode()
                if reply.find('E') >= 0:
                    output(f"\nErreur : {reply}")
                    received_error = True
                elif reply.find('O') >= 0:
                    output("Result : OK")
                    received_ok = True
            connection.close()
            f.close()
            sock.close()
            if finish_callback: finish_callback(received_ok)
            return 0 if received_ok else 1
        except Exception:
            output("Erreur : Pas de résultat!")
            connection.close()
            f.close()
            sock.close()
            if finish_callback: finish_callback(False)
            return 1

    finally:
        try: connection.close()
        except: pass
        try: f.close()
        except: pass
        sock.close()

def launch_gui():
    root = tk.Tk()
    root.title("OTA_Updater")
    root.geometry("1200x450")

    top = ttk.Frame(root)
    top.pack(fill="x", padx=10, pady=10)
    
    ttk.Label(top, text="Fichier :").pack(side="left")
    file_var = tk.StringVar(value="Aucun fichier sélectionné")
    file_entry = ttk.Entry(top, textvariable=file_var, width=50)
    file_entry.pack(side="left", padx=5)
    
    def browse_file():
        filename = filedialog.askopenfilename(
            title="Sélectionner le fichier de mise à jour",
            filetypes=[("Tous les fichiers", "*.*")]
        )
        if filename:
            file_var.set(filename)
            
    ttk.Button(top, text="...", width=3, command=browse_file).pack(side="left", padx=(0, 10))
    
    ttk.Label(top, text="IP/Hostname :").pack(side="left")
    ip_var = tk.StringVar(value="SmartCharger.local")
    ip_entry = ttk.Entry(top, textvariable=ip_var, width=20)
    ip_entry.pack(side="left", padx=5)

    progress_frame = ttk.Frame(root)
    progress_frame.pack(fill="x", padx=10, pady=(0, 10))
    
    progress_bar = ttk.Progressbar(progress_frame, orient="horizontal", mode="determinate")
    progress_bar.pack(fill="x", expand=True)

    out = tk.Text(root, bg="black", fg="white", insertbackground="white", state="disabled")
    out.pack(fill="both", expand=True, padx=10, pady=(0, 10))

    def log(msg):
        out.config(state="normal")
        out.insert("end", str(msg)+"\n")
        out.see("end")
        out.config(state="disabled")

    def clear():
        out.config(state="normal")
        out.delete("1.0","end")
        out.config(state="disabled")
        progress_bar["value"] = 0

    def set_progress_value(val):
        progress_bar["value"] = val
        root.update_idletasks() # Force Tkinter à redessiner immédiatement le composant

    def on_update_finished(success):
        btn_update.config(state="normal")
        if success:
            log("--- MISE À JOUR TERMINÉE AVEC SUCCÈS ---")
        else:
            log("--- ÉCHEC DE LA MISE À JOUR ---")

    def run_update_thread():
        btn_update.config(state="disabled")
        progress_bar["value"] = 0
        
        log(f"Cible : {ip_var.get().strip()}")
        log(f"Fichier : {file_var.get()}")
        
        # Lancement dans un Thread parallèle
        t = threading.Thread(
            target=update,
            kwargs={
                "remoteAddr": str(ip_var.get().strip()),
                "filename": file_var.get(),
                "output": log,
                "progress_callback": set_progress_value,
                "finish_callback": on_update_finished
            },
            daemon=True # Permet de tuer le thread si on ferme l'application
        )
        t.start()
     
    def do_update():
        path = file_var.get()
        if path == "Aucun fichier sélectionné" or not path:
            log("Erreur : Veuillez sélectionner un fichier valide avant de mettre à jour.")
        else:
            run_update_thread()

    btn_update = ttk.Button(top, text="Mettre à jour", command=do_update)
    btn_update.pack(side="left", padx=10)
    
    ttk.Button(top, text="Effacer log", command=clear).pack(side="left", padx=5)
    ttk.Button(top, text="Quitter", command=root.destroy).pack(side="right")
    
    root.mainloop()

if __name__ == '__main__':
    launch_gui()