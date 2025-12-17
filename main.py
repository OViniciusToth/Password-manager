import tkinter as tk
from tkinter import messagebox, filedialog, scrolledtext, simpledialog
import json
import os
import base64
from cryptography.fernet import Fernet
from collections import defaultdict
import logging
from datetime import datetime
import random
import string
import sys

# === Configuração do Log Avançada ===
class ConsoleHandler(logging.Handler):
    """Handler personalizado para enviar logs para o console do TKinter"""
    def __init__(self, text_widget):
        super().__init__()
        self.text_widget = text_widget

    def emit(self, record):
        msg = self.format(record)
        self.text_widget.configure(state='normal')
        self.text_widget.insert(tk.END, msg + '\n')
        self.text_widget.configure(state='disabled')
        self.text_widget.see(tk.END)

def configurar_logging_com_console():
    """Configura o sistema de logging com console integrado"""
    if not os.path.exists('logs'):
        os.makedirs('logs')
    
    for handler in logging.root.handlers[:]:
        logging.root.removeHandler(handler)
    
    formatter = logging.Formatter('%(asctime)s - %(levelname)s - %(message)s')
    
    file_handler = logging.FileHandler(f'logs/password_manager_{datetime.now().strftime("%Y%m%d_%H%M%S")}.log')
    file_handler.setFormatter(formatter)
    
    console_handler = logging.StreamHandler(sys.stdout)
    console_handler.setFormatter(formatter)
    
    logging.basicConfig(
        level=logging.INFO,
        handlers=[file_handler, console_handler]
    )
    
    logging.info("=== SISTEMA DE GERENCIAMENTO DE SENHAS INICIADO ===")

configurar_logging_com_console()

# === Criptografia ===
ARQUIVO_CHAVE = "chave.key"
ARQUIVO_DADOS = "contas.json"
ARQUIVO_CONFIG = "config.json"
SENHA_MESTRE = "admin"

if not os.path.exists(ARQUIVO_CHAVE):
    logging.info("Gerando nova chave de criptografia...")
    chave = Fernet.generate_key()
    with open(ARQUIVO_CHAVE, "wb") as f:
        f.write(chave)
    logging.info("Chave de criptografia gerada e salva com sucesso")
else:
    with open(ARQUIVO_CHAVE, "rb") as f:
        chave = f.read()
    logging.info("Chave de criptografia carregada com sucesso")

fernet = Fernet(chave)

# === Mapeamento de domínios equivalentes ===
DOMINIOS_EQUIVALENTES = {
    'gmail.com': 'gmail.com',
    'googlemail.com': 'gmail.com',
    'google.com': 'gmail.com',
    'google.com.br': 'gmail.com',
    'hotmail.com': 'outlook.com',
    'live.com': 'outlook.com',
    'live.com.br': 'outlook.com',
    'msn.com': 'outlook.com'
}

# === Variáveis globais para console ===
janela_console_global = None
console_handler_global = None

# === Funções para salvar/recuperar configurações ===
def carregar_config():
    """Carrega as configurações da janela"""
    if os.path.exists(ARQUIVO_CONFIG):
        try:
            with open(ARQUIVO_CONFIG, "r", encoding='utf-8') as f:
                config = json.load(f)
                logging.info("Configurações carregadas com sucesso")
                return config
        except Exception as e:
            logging.error(f"Erro ao carregar configurações: {str(e)}")
    else:
        logging.info("Arquivo de configurações não encontrado, criando novo")
    return {}

def salvar_config(config):
    """Salva as configurações da janela"""
    try:
        with open(ARQUIVO_CONFIG, "w", encoding='utf-8') as f:
            json.dump(config, f, indent=4, ensure_ascii=False)
        logging.info("Configurações salvas com sucesso")
    except Exception as e:
        logging.error(f"Erro ao salvar configurações: {str(e)}")

def salvar_posicao_console(janela):
    """Salva a posição e tamanho apenas do console"""
    try:
        config = carregar_config()
        config['console'] = {
            'x': janela.winfo_x(),
            'y': janela.winfo_y(),
            'width': janela.winfo_width(),
            'height': janela.winfo_height()
        }
        salvar_config(config)
    except Exception as e:
        logging.error(f"Erro ao salvar posição do console: {str(e)}")

def restaurar_posicao_console(janela, largura_padrao=700, altura_padrao=400):
    """Restaura a posição e tamanho apenas do console"""
    try:
        config = carregar_config()
        if 'console' in config:
            pos = config['console']
            x = pos.get('x', 100)
            y = pos.get('y', 100)
            width = pos.get('width', largura_padrao)
            height = pos.get('height', altura_padrao)
            
            # Verifica se a posição está dentro dos limites da tela
            if x < 0: x = 100
            if y < 0: y = 100
            
            janela.geometry(f"{width}x{height}+{x}+{y}")
        else:
            # Posição padrão centralizada
            janela.geometry(f"{largura_padrao}x{altura_padrao}+100+100")
    except Exception as e:
        logging.error(f"Erro ao restaurar posição do console: {str(e)}")
        janela.geometry(f"{largura_padrao}x{altura_padrao}+100+100")

# === Funções para salvar/recuperar configurações do gerador de senhas ===
def carregar_config_gerador():
    """Carrega as configurações do gerador de senhas"""
    config = carregar_config()
    gerador_config = config.get('gerador_senhas', {})
    
    # Valores padrão
    config_padrao = {
        'comprimento': 16,
        'maiusculas': True,
        'numeros': True,
        'especiais': True,
        'caracteres_especiais': "!@#$%&*()_+-=[]{}|;:,.<>?"
    }
    
    # Mescla com valores salvos
    config_final = {
        'comprimento': gerador_config.get('comprimento', config_padrao['comprimento']),
        'maiusculas': gerador_config.get('maiusculas', config_padrao['maiusculas']),
        'numeros': gerador_config.get('numeros', config_padrao['numeros']),
        'especiais': gerador_config.get('especiais', config_padrao['especiais']),
        'caracteres_especiais': gerador_config.get('caracteres_especiais', config_padrao['caracteres_especiais'])
    }
    
    logging.info(f"Configurações do gerador carregadas: {config_final}")
    return config_final

def salvar_config_gerador(comprimento, maiusculas, numeros, especiais, caracteres_especiais):
    """Salva as configurações do gerador de senhas"""
    try:
        config = carregar_config()
        config['gerador_senhas'] = {
            'comprimento': comprimento,
            'maiusculas': maiusculas,
            'numeros': numeros,
            'especiais': especiais,
            'caracteres_especiais': caracteres_especiais
        }
        salvar_config(config)
        logging.info(f"Configurações do gerador SALVAS: comprimento={comprimento}, especiais={especiais}, caracteres='{caracteres_especiais}'")
    except Exception as e:
        logging.error(f"Erro ao salvar configurações do gerador: {str(e)}")

# === Função para normalizar domínio ===
def normalizar_dominio(site):
    """Normaliza domínios equivalentes para o mesmo domínio principal"""
    site_lower = site.lower().strip()
    
    # Verifica se é um domínio que tem equivalente
    for dominio, equivalente in DOMINIOS_EQUIVALENTES.items():
        if dominio in site_lower:
            return equivalente
    
    # Se não tem equivalente, retorna o próprio site
    return site_lower

# === Função para normalizar conta ===
def normalizar_conta(site, usuario):
    """Normaliza site e usuário para verificação de duplicatas considerando domínios equivalentes"""
    site_normalizado = normalizar_dominio(site)
    usuario_normalizado = usuario.lower().strip()
    return f"{site_normalizado}||{usuario_normalizado}"

# === JSON Local ===
def carregar_dados():
    logging.info("Tentando carregar dados do arquivo JSON...")
    if os.path.exists(ARQUIVO_DADOS):
        try:
            with open(ARQUIVO_DADOS, "r") as f:
                dados = json.load(f)
                logging.info(f"Carregados {len(dados)} contas do arquivo JSON")
                return dados
        except Exception as e:
            logging.error(f"Erro ao carregar dados: {str(e)}")
            return []
    logging.info("Nenhum arquivo de dados encontrado, retornando lista vazia")
    return []

def salvar_dados(dados):
    try:
        logging.info(f"Salvando {len(dados)} contas no arquivo JSON...")
        with open(ARQUIVO_DADOS, "w") as f:
            json.dump(dados, f, indent=4)
        logging.info("Dados salvos com sucesso")
        return True
    except Exception as e:
        logging.error(f"Erro ao salvar dados: {str(e)}")
        messagebox.showerror("Erro", f"Erro ao salvar dados: {str(e)}")
        return False

# === Criptografia ===
def criptografar(texto):
    logging.debug("Criptografando texto...")
    return fernet.encrypt(texto.encode()).decode()

def descriptografar(cripto):
    logging.debug("Descriptografando texto...")
    return fernet.decrypt(cripto.encode()).decode()

# === Gerador de Senhas ===
def gerar_senha(comprimento=12, usar_maiusculas=True, usar_numeros=True, caracteres_especiais=""):
    """Gera uma senha aleatória com os critérios especificados"""
    logging.info("Gerando nova senha...")
    
    caracteres = string.ascii_lowercase
    if usar_maiusculas:
        caracteres += string.ascii_uppercase
    if usar_numeros:
        caracteres += string.digits
    if caracteres_especiais:
        caracteres += caracteres_especiais
    
    if not caracteres:
        logging.warning("Nenhum critério selecionado para gerar senha")
        return ""
    
    senha = ''.join(random.choice(caracteres) for _ in range(comprimento))
    logging.info(f"Senha gerada com {comprimento} caracteres")
    return senha

def mostrar_gerador_senha():
    """Mostra a janela do gerador de senhas"""
    logging.info("Abrindo gerador de senhas...")
    
    janela_gerador = tk.Toplevel(janela)
    janela_gerador.title("Gerador de Senhas")
    janela_gerador.geometry("450x550")
    janela_gerador.configure(bg="#1e1e2f")
    janela_gerador.resizable(False, False)
    
    # Carrega configurações salvas ANTES de criar as variáveis
    config_salva = carregar_config_gerador()
    logging.info(f"Configurações carregadas para o gerador: {config_salva}")
    
    # Variáveis de controle - INICIALIZADAS COM VALORES SALVOS
    comprimento_var = tk.IntVar(value=config_salva['comprimento'])
    maiusculas_var = tk.BooleanVar(value=config_salva['maiusculas'])
    numeros_var = tk.BooleanVar(value=config_salva['numeros'])
    especiais_var = tk.BooleanVar(value=config_salva['especiais'])
    especiais_var_str = tk.StringVar(value=config_salva['caracteres_especiais'])
    senha_gerada_var = tk.StringVar()
    
    def atualizar_estado_especiais():
        """Atualiza o estado dos campos de caracteres especiais"""
        if especiais_var.get():
            entry_especiais.configure(state='normal')
            btn_salvar_especiais.configure(state='normal')
        else:
            entry_especiais.configure(state='disabled')
            btn_salvar_especiais.configure(state='disabled')
        logging.info(f"Estado dos especiais atualizado: {especiais_var.get()}")
    
    def salvar_configuracoes_atuais():
        """Salva as configurações atuais"""
        caracteres_especiais = especiais_var_str.get() if especiais_var.get() else ""
        
        salvar_config_gerador(
            comprimento=comprimento_var.get(),
            maiusculas=maiusculas_var.get(),
            numeros=numeros_var.get(),
            especiais=especiais_var.get(),
            caracteres_especiais=caracteres_especiais
        )
        messagebox.showinfo("Configurações Salvas", "Suas configurações foram salvas!")
        logging.info(f"Configurações salvas manualmente - Caracteres: '{caracteres_especiais}'")
    
    def gerar_senha_com_config_atual():
        """Gera senha com as configurações atuais"""
        comprimento = comprimento_var.get()
        if comprimento < 4:
            messagebox.showwarning("Comprimento inválido", "O comprimento mínimo é 4 caracteres")
            return
        
        # Obtém os caracteres especiais
        caracteres_especiais = especiais_var_str.get() if especiais_var.get() else ""
        
        logging.info(f"Gerando senha - Comprimento: {comprimento}, Especiais: {especiais_var.get()}, Chars: '{caracteres_especiais}'")
        
        # SALVA AS CONFIGURAÇÕES ANTES DE GERAR
        salvar_config_gerador(
            comprimento=comprimento,
            maiusculas=maiusculas_var.get(),
            numeros=numeros_var.get(),
            especiais=especiais_var.get(),
            caracteres_especiais=caracteres_especiais
        )
        
        # Gera a senha
        senha = gerar_senha(
            comprimento=comprimento,
            usar_maiusculas=maiusculas_var.get(),
            usar_numeros=numeros_var.get(),
            caracteres_especiais=caracteres_especiais
        )
        
        if senha:
            senha_gerada_var.set(senha)
            entry_senha_gerada.configure(state='normal')
            entry_senha_gerada.delete(0, tk.END)
            entry_senha_gerada.insert(0, senha)
            entry_senha_gerada.configure(state='readonly')
            logging.info("Senha gerada e exibida com sucesso")
        else:
            messagebox.showerror("Erro", "Não foi possível gerar a senha. Verifique as configurações.")
    
    def copiar_senha_gerada():
        senha = senha_gerada_var.get()
        if senha:
            janela_gerador.clipboard_clear()
            janela_gerador.clipboard_append(senha)
            messagebox.showinfo("Copiado", "Senha copiada para a área de transferência!")
            logging.debug("Senha copiada para área de transferência")
        else:
            messagebox.showwarning("Aviso", "Gere uma senha primeiro!")
    
    def usar_senha_e_fechar():
        senha = senha_gerada_var.get()
        if senha:
            entry_senha.delete(0, tk.END)
            entry_senha.insert(0, senha)
            janela_gerador.destroy()
            logging.debug("Senha aplicada no campo principal")
            messagebox.showinfo("Sucesso", "Senha inserida no campo de senha!")
        else:
            messagebox.showwarning("Aviso", "Gere uma senha primeiro!")
    
    def enviar_para_campo_sem_fechar():
        """Envia a senha gerada para o campo de senha principal sem fechar o gerador"""
        senha = senha_gerada_var.get()
        if senha:
            entry_senha.delete(0, tk.END)
            entry_senha.insert(0, senha)
            logging.debug("Senha enviada para campo principal")
            messagebox.showinfo("Sucesso", "Senha enviada para o campo de senha!")
        else:
            messagebox.showwarning("Aviso", "Gere uma senha primeiro!")
    
    def enviar_direto_para_campo():
        """Envia a senha diretamente para o campo principal e mantém o gerador aberto"""
        senha = senha_gerada_var.get()
        if senha:
            entry_senha.delete(0, tk.END)
            entry_senha.insert(0, senha)
            logging.info("Senha enviada diretamente para o campo principal")
        else:
            messagebox.showwarning("Aviso", "Gere uma senha primeiro!")
    
    def restaurar_config_padrao():
        """Restaura as configurações padrão"""
        comprimento_var.set(16)
        maiusculas_var.set(True)
        numeros_var.set(True)
        especiais_var.set(True)
        especiais_var_str.set("!@#$%&*()_+-=[]{}|;:,.<>?")
        
        # Atualiza o estado dos campos
        atualizar_estado_especiais()
        
        # Salva as configurações padrão
        salvar_config_gerador(
            comprimento=16,
            maiusculas=True,
            numeros=True,
            especiais=True,
            caracteres_especiais="!@#$%&*()_+-=[]{}|;:,.<>?"
        )
        
        messagebox.showinfo("Padrão Restaurado", "Configurações restauradas para os valores padrão!")
        logging.info("Configurações do gerador restauradas para padrão")
        
        # Gera uma nova senha com as configurações padrão
        gerar_senha_com_config_atual()
    
    # Widgets da interface
    tk.Label(janela_gerador, text="🔐 Gerador de Senhas", font=("Arial", 16, "bold"), 
             bg="#1e1e2f", fg="white").pack(pady=15)
    
    # Frame principal para organização
    main_frame = tk.Frame(janela_gerador, bg="#1e1e2f")
    main_frame.pack(fill=tk.BOTH, expand=True, padx=20, pady=10)
    
    # Comprimento
    frame_comprimento = tk.Frame(main_frame, bg="#1e1e2f")
    frame_comprimento.pack(fill=tk.X, pady=8)
    tk.Label(frame_comprimento, text="Comprimento:", bg="#1e1e2f", fg="white", 
             font=("Arial", 10)).pack(side=tk.LEFT)
    tk.Label(frame_comprimento, textvariable=comprimento_var, bg="#1e1e2f", fg="#00ff00",
             font=("Arial", 10, "bold"), width=3).pack(side=tk.RIGHT)
    tk.Scale(frame_comprimento, from_=4, to=32, orient=tk.HORIZONTAL, variable=comprimento_var,
             bg="#1e1e2f", fg="white", highlightbackground="#1e1e2f", length=300,
             command=lambda x: gerar_senha_com_config_atual()).pack(fill=tk.X)
    
    # Separador
    tk.Frame(main_frame, bg="#444", height=1).pack(fill=tk.X, pady=10)
    
    # Checkboxes
    check_frame = tk.Frame(main_frame, bg="#1e1e2f")
    check_frame.pack(fill=tk.X, pady=5)
    
    tk.Checkbutton(check_frame, text="Letras Maiúsculas (A-Z)", variable=maiusculas_var,
                   bg="#1e1e2f", fg="white", selectcolor="#2b2b3d", font=("Arial", 10),
                   command=gerar_senha_com_config_atual).pack(anchor="w")
    tk.Checkbutton(check_frame, text="Números (0-9)", variable=numeros_var,
                   bg="#1e1e2f", fg="white", selectcolor="#2b2b3d", font=("Arial", 10),
                   command=gerar_senha_com_config_atual).pack(anchor="w")
    
    # Caracteres especiais
    especiais_frame = tk.Frame(main_frame, bg="#1e1e2f")
    especiais_frame.pack(fill=tk.X, pady=5)
    
    check_especiais = tk.Checkbutton(especiais_frame, text="Caracteres Especiais:", variable=especiais_var,
                   bg="#1e1e2f", fg="white", selectcolor="#2b2b3d", font=("Arial", 10), 
                   command=lambda: [atualizar_estado_especiais(), gerar_senha_com_config_atual()])
    check_especiais.pack(anchor="w")
    
    entry_especiais = tk.Entry(especiais_frame, textvariable=especiais_var_str, 
                              font=("Courier", 10), width=40)
    entry_especiais.pack(fill=tk.X, pady=5)
    entry_especiais.bind('<KeyRelease>', lambda e: gerar_senha_com_config_atual())
    
    # Frame para botões de caracteres especiais
    frame_btn_especiais = tk.Frame(especiais_frame, bg="#1e1e2f")
    frame_btn_especiais.pack(fill=tk.X, pady=5)
    
    btn_salvar_especiais = tk.Button(frame_btn_especiais, text="💾 Salvar Configurações", 
                                    command=salvar_configuracoes_atuais, bg="#17a2b8", fg="white",
                                    font=("Arial", 8))
    btn_salvar_especiais.pack(side=tk.LEFT, padx=(0, 5))
    
    tk.Button(frame_btn_especiais, text="🔄 Padrão", command=restaurar_config_padrao,
              bg="#6c757d", fg="white", font=("Arial", 8)).pack(side=tk.LEFT)
    
    # Dica de caracteres especiais
    tk.Label(especiais_frame, text="Exemplo: !@#$%&*()_+-=[]{}|;:,.<>?", 
             bg="#1e1e2f", fg="#888", font=("Arial", 8)).pack(anchor="w")
    
    # Botão gerar
    tk.Button(main_frame, text="🔄 Gerar Senha", command=gerar_senha_com_config_atual,
              bg="#17a2b8", fg="white", font=("Arial", 12, "bold"), 
              height=2).pack(fill=tk.X, pady=15)
    
    # Separador
    tk.Frame(main_frame, bg="#444", height=1).pack(fill=tk.X, pady=10)
    
    # Senha gerada
    tk.Label(main_frame, text="Senha Gerada:", bg="#1e1e2f", fg="white", 
             font=("Arial", 11, "bold")).pack(anchor="w")
    
    frame_senha = tk.Frame(main_frame, bg="#1e1e2f")
    frame_senha.pack(fill=tk.X, pady=8)
    
    # Campo de entrada para exibir a senha gerada
    entry_senha_gerada = tk.Entry(frame_senha, 
                                 font=("Courier", 12), 
                                 bg="#2b2b3d", fg="#00ff00")
    entry_senha_gerada.pack(side=tk.LEFT, fill=tk.X, expand=True)
    entry_senha_gerada.configure(state='readonly')
    
    btn_frame = tk.Frame(frame_senha, bg="#1e1e2f")
    btn_frame.pack(side=tk.RIGHT, padx=(5, 0))
    
    tk.Button(btn_frame, text="📋", command=copiar_senha_gerada, 
              bg="#444", fg="white", width=3, font=("Arial", 10)).pack(side=tk.LEFT, padx=2)
    
    # Botões de ação
    frame_botoes = tk.Frame(main_frame, bg="#1e1e2f")
    frame_botoes.pack(fill=tk.X, pady=10)
    
    # PRIMEIRA LINHA DE BOTÕES
    frame_botoes_linha1 = tk.Frame(frame_botoes, bg="#1e1e2f")
    frame_botoes_linha1.pack(fill=tk.X, pady=2)
    
    # Botão: Enviar Direto para Campo (sem fechar)
    tk.Button(frame_botoes_linha1, text="🚀 Enviar Direto", command=enviar_direto_para_campo,
              bg="#ff9800", fg="white", font=("Arial", 10, "bold")).pack(side=tk.LEFT, fill=tk.X, expand=True, padx=2)
    
    # Botão para enviar sem fechar
    tk.Button(frame_botoes_linha1, text="📤 Enviar", command=enviar_para_campo_sem_fechar,
              bg="#28a745", fg="white", font=("Arial", 10)).pack(side=tk.LEFT, fill=tk.X, expand=True, padx=2)
    
    # SEGUNDA LINHA DE BOTÕES
    frame_botoes_linha2 = tk.Frame(frame_botoes, bg="#1e1e2f")
    frame_botoes_linha2.pack(fill=tk.X, pady=2)
    
    # Botão para usar e fechar
    tk.Button(frame_botoes_linha2, text="✅ Usar e Fechar", command=usar_senha_e_fechar,
              bg="#28a745", fg="white", font=("Arial", 10)).pack(side=tk.LEFT, fill=tk.X, expand=True, padx=2)
    
    # Botão fechar
    tk.Button(frame_botoes_linha2, text="❌ Fechar", command=janela_gerador.destroy,
              bg="#6c757d", fg="white", font=("Arial", 10)).pack(side=tk.LEFT, fill=tk.X, expand=True, padx=2)
    
    # INICIALIZAÇÃO FINAL - Executa após a janela estar totalmente criada
    def inicializacao_final():
        """Inicialização final após a janela estar pronta"""
        logging.info("=== INICIALIZAÇÃO FINAL DO GERADOR ===")
        logging.info(f"Configurações iniciais: comprimento={comprimento_var.get()}, especiais={especiais_var.get()}, chars='{especiais_var_str.get()}'")
        
        # Atualiza o estado inicial dos campos
        atualizar_estado_especiais()
        
        # Gera a primeira senha automaticamente
        gerar_senha_com_config_atual()
        
        logging.info("Gerador totalmente inicializado e configurado")
    
    # Executa a inicialização após um breve delay
    janela_gerador.after(200, inicializacao_final)

# === Função para exportar contas em TXT ===
def exportar_contas_txt():
    """Exporta todas as contas para arquivos TXT individuais"""
    dados = carregar_dados()
    
    if not dados:
        messagebox.showinfo("Exportar", "Nenhuma conta para exportar.")
        return
    
    # Pede para selecionar a pasta de destino
    pasta_destino = filedialog.askdirectory(title="Selecione a pasta para salvar os arquivos TXT")
    
    if not pasta_destino:
        return
    
    try:
        contas_exportadas = 0
        
        for conta in dados:
            # Cria um nome de arquivo seguro a partir do site e usuário
            site_seguro = "".join(c for c in conta['site'] if c.isalnum() or c in (' ', '-', '_')).rstrip()
            usuario_seguro = "".join(c for c in conta['usuario'] if c.isalnum() or c in (' ', '-', '_')).rstrip()
            
            # Se o nome ficar vazio, usa um nome padrão
            if not site_seguro:
                site_seguro = "site_desconhecido"
            if not usuario_seguro:
                usuario_seguro = "usuario_desconhecido"
            
            nome_arquivo = f"{site_seguro}_{usuario_seguro}.txt"
            caminho_arquivo = os.path.join(pasta_destino, nome_arquivo)
            
            # Se o arquivo já existir, adiciona um número
            contador = 1
            while os.path.exists(caminho_arquivo):
                nome_arquivo = f"{site_seguro}_{usuario_seguro}_{contador}.txt"
                caminho_arquivo = os.path.join(pasta_destino, nome_arquivo)
                contador += 1
            
            # Descriptografa a senha
            senha_descriptografada = descriptografar(conta['senha'])
            
            # Cria o conteúdo do arquivo
            conteudo = f"""CONTA EXPORTADA - GERENCIADOR DE SENHAS
Data da Exportação: {datetime.now().strftime("%Y-%m-%d %H:%M:%S")}

=== INFORMAÇÕES DA CONTA ===
Site: {conta['site']}
Usuário: {conta['usuario']}
Senha: {senha_descriptografada}
Apelido: {conta.get('apelido', 'Nenhum')}
Data de Criação: {conta.get('data_criacao', 'Desconhecida')}

=== INSTRUÇÕES ===
• Este arquivo contém informações sensíveis
• Mantenha em local seguro
• Não compartilhe com ninguém
• Exclua quando não for mais necessário

=== SISTEMA ===
Exportado por: Gerenciador de Senhas
Versão: 2.0
Data: {datetime.now().strftime("%d/%m/%Y")}
"""
            
            # Salva o arquivo
            with open(caminho_arquivo, 'w', encoding='utf-8') as f:
                f.write(conteudo)
            
            contas_exportadas += 1
        
        messagebox.showinfo("Exportação Concluída", 
                           f"Exportação realizada com sucesso!\n"
                           f"Contas exportadas: {contas_exportadas}\n"
                           f"Pasta: {pasta_destino}")
        logging.info(f"Exportação TXT: {contas_exportadas} contas exportadas para {pasta_destino}")
        
    except Exception as e:
        messagebox.showerror("Erro na Exportação", f"Erro ao exportar contas: {str(e)}")
        logging.error(f"Erro na exportação TXT: {str(e)}")

# === Funções para gerenciamento de contas ===
def adicionar_conta():
    """Adiciona uma nova conta ao sistema"""
    site = entry_site.get().strip()
    usuario = entry_usuario.get().strip()
    senha = entry_senha.get().strip()
    apelido = entry_apelido.get().strip()
    
    if not site or not usuario or not senha:
        messagebox.showerror("Erro", "Preencha todos os campos obrigatórios (Site, Usuário e Senha)!")
        return
    
    # Verifica se já existe uma conta com o mesmo site e usuário
    dados = carregar_dados()
    conta_normalizada = normalizar_conta(site, usuario)
    
    for conta in dados:
        conta_existente_normalizada = normalizar_conta(conta['site'], conta['usuario'])
        if conta_existente_normalizada == conta_normalizada:
            messagebox.showerror("Erro", "Já existe uma conta com este site e usuário!")
            return
    
    # Adiciona a nova conta
    nova_conta = {
        'site': site,
        'usuario': usuario,
        'senha': criptografar(senha),
        'apelido': apelido,
        'data_criacao': datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    }
    
    dados.append(nova_conta)
    
    if salvar_dados(dados):
        # Limpa os campos
        entry_site.delete(0, tk.END)
        entry_usuario.delete(0, tk.END)
        entry_senha.delete(0, tk.END)
        entry_apelido.delete(0, tk.END)
        
        messagebox.showinfo("Sucesso", "Conta adicionada com sucesso!")
        logging.info(f"Nova conta adicionada: {site} - {usuario}")
    else:
        messagebox.showerror("Erro", "Não foi possível salvar a conta!")

def ver_contas():
    """Mostra uma janela com todas as contas salvas ORDENADAS POR SITE"""
    dados = carregar_dados()
    
    if not dados:
        messagebox.showinfo("Contas", "Nenhuma conta salva.")
        return
    
    # ORDENA as contas por site (ordem alfabética)
    dados_ordenados = sorted(dados, key=lambda x: x['site'].lower())
    
    janela_contas = tk.Toplevel(janela)
    janela_contas.title("Contas Salvas - Ordenadas por Site")
    janela_contas.geometry("700x500")
    janela_contas.configure(bg="#1e1e2f")
    
    # Frame para a lista de contas
    frame_lista = tk.Frame(janela_contas, bg="#1e1e2f")
    frame_lista.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
    
    # Listbox com scrollbar
    scrollbar = tk.Scrollbar(frame_lista)
    scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
    
    lista_contas = tk.Listbox(frame_lista, yscrollcommand=scrollbar.set, 
                             bg="#2b2b3d", fg="white", font=("Arial", 10), 
                             selectmode=tk.SINGLE, width=80, height=20)
    lista_contas.pack(fill=tk.BOTH, expand=True)
    
    scrollbar.config(command=lista_contas.yview)
    
    # Preenche a lista com dados ORDENADOS
    for i, conta in enumerate(dados_ordenados):
        site = conta['site']
        usuario = conta['usuario']
        apelido = conta.get('apelido', '')
        
        if apelido:
            display_text = f"{site} - {usuario} ({apelido})"
        else:
            display_text = f"{site} - {usuario}"
        
        lista_contas.insert(tk.END, display_text)
    
    # Frame para botões
    frame_botoes = tk.Frame(janela_contas, bg="#1e1e2f")
    frame_botoes.pack(fill=tk.X, padx=10, pady=10)
    
    def ver_detalhes():
        selecionado = lista_contas.curselection()
        if not selecionado:
            messagebox.showwarning("Aviso", "Selecione uma conta!")
            return
        
        indice = selecionado[0]
        conta = dados_ordenados[indice]
        
        # Mostra os detalhes em uma nova janela
        janela_detalhes = tk.Toplevel(janela_contas)
        janela_detalhes.title("Detalhes da Conta")
        janela_detalhes.geometry("500x400")
        janela_detalhes.configure(bg="#1e1e2f")
        
        # Frame para detalhes
        frame_detalhes = tk.Frame(janela_detalhes, bg="#1e1e2f")
        frame_detalhes.pack(fill=tk.BOTH, expand=True, padx=20, pady=20)
        
        # Campos de detalhes
        campos = [
            ("Site:", conta['site']),
            ("Usuário:", conta['usuario']),
            ("Senha:", "••••••••"),
            ("Apelido:", conta.get('apelido', 'Nenhum')),
            ("Data de Criação:", conta.get('data_criacao', 'Desconhecida'))
        ]
        
        for i, (label, valor) in enumerate(campos):
            tk.Label(frame_detalhes, text=label, bg="#1e1e2f", fg="white", 
                    font=("Arial", 10, "bold")).grid(row=i, column=0, sticky="w", pady=8)
            
            if label == "Senha:":
                frame_senha = tk.Frame(frame_detalhes, bg="#1e1e2f")
                frame_senha.grid(row=i, column=1, sticky="ew", pady=8)
                
                senha_real = descriptografar(conta['senha'])
                entry_senha_detalhes = tk.Entry(frame_senha, show="*", font=("Arial", 10),
                                               bg="#2b2b3d", fg="white")
                entry_senha_detalhes.insert(0, senha_real)
                entry_senha_detalhes.configure(state='readonly')
                entry_senha_detalhes.pack(side=tk.LEFT, fill=tk.X, expand=True)
                
                def mostrar_senha():
                    if entry_senha_detalhes.cget('show') == '*':
                        entry_senha_detalhes.configure(show='')
                        btn_mostrar.config(text="🙈 Ocultar")
                    else:
                        entry_senha_detalhes.configure(show='*')
                        btn_mostrar.config(text="👁️ Mostrar")
                
                btn_mostrar = tk.Button(frame_senha, text="👁️ Mostrar", command=mostrar_senha,
                                      bg="#17a2b8", fg="white", font=("Arial", 8))
                btn_mostrar.pack(side=tk.RIGHT, padx=(5, 0))
                
                def copiar_senha():
                    janela_detalhes.clipboard_clear()
                    janela_detalhes.clipboard_append(senha_real)
                    messagebox.showinfo("Copiado", "Senha copiada para a área de transferência!")
                    logging.info(f"Senha copiada para conta: {conta['site']}")
                
                tk.Button(frame_senha, text="📋", command=copiar_senha,
                         bg="#28a745", fg="white", font=("Arial", 8)).pack(side=tk.RIGHT, padx=2)
            else:
                tk.Label(frame_detalhes, text=valor, bg="#1e1e2f", fg="#cccccc",
                        font=("Arial", 10)).grid(row=i, column=1, sticky="w", pady=8)
        
        # Botão fechar
        tk.Button(frame_detalhes, text="Fechar", command=janela_detalhes.destroy,
                 bg="#6c757d", fg="white", font=("Arial", 10)).grid(row=len(campos), column=0, columnspan=2, pady=15)
    
    def copiar_senha():
        selecionado = lista_contas.curselection()
        if not selecionado:
            messagebox.showwarning("Aviso", "Selecione uma conta!")
            return
        
        indice = selecionado[0]
        conta = dados_ordenados[indice]
        
        senha = descriptografar(conta['senha'])
        janela_contas.clipboard_clear()
        janela_contas.clipboard_append(senha)
        messagebox.showinfo("Copiado", "Senha copiada para a área de transferência!")
        logging.info(f"Senha copiada para conta: {conta['site']} - {conta['usuario']}")
    
    def excluir_conta():
        selecionado = lista_contas.curselection()
        if not selecionado:
            messagebox.showwarning("Aviso", "Selecione uma conta!")
            return
        
        indice = selecionado[0]
        conta = dados_ordenados[indice]
        
        resposta = messagebox.askyesno("Confirmar", f"Tem certeza que deseja excluir a conta:\n{conta['site']} - {conta['usuario']}?")
        if resposta:
            # Remove do array original (não ordenado)
            dados_original = carregar_dados()
            for i, conta_original in enumerate(dados_original):
                if (conta_original['site'] == conta['site'] and 
                    conta_original['usuario'] == conta['usuario']):
                    dados_original.pop(i)
                    break
            
            if salvar_dados(dados_original):
                lista_contas.delete(indice)
                messagebox.showinfo("Sucesso", "Conta excluída com sucesso!")
                logging.info(f"Conta excluída: {conta['site']} - {conta['usuario']}")
            else:
                messagebox.showerror("Erro", "Não foi possível excluir a conta!")
    
    # Botões
    tk.Button(frame_botoes, text="👁️ Ver Detalhes", command=ver_detalhes,
             bg="#17a2b8", fg="white", font=("Arial", 10)).pack(side=tk.LEFT, padx=5)
    
    tk.Button(frame_botoes, text="📋 Copiar Senha", command=copiar_senha,
             bg="#28a745", fg="white", font=("Arial", 10)).pack(side=tk.LEFT, padx=5)
    
    tk.Button(frame_botoes, text="🗑️ Excluir", command=excluir_conta,
             bg="#dc3545", fg="white", font=("Arial", 10)).pack(side=tk.LEFT, padx=5)
    
    # NOVO BOTÃO: Exportar Todas as Contas
    tk.Button(frame_botoes, text="📤 Exportar TXT", command=exportar_contas_txt,
             bg="#ff9800", fg="white", font=("Arial", 10)).pack(side=tk.LEFT, padx=5)
    
    tk.Button(frame_botoes, text="Fechar", command=janela_contas.destroy,
             bg="#6c757d", fg="white", font=("Arial", 10)).pack(side=tk.RIGHT, padx=5)

def mostrar_console():
    """Mostra o console de logs"""
    global janela_console_global, console_handler_global
    
    logging.info("Abrindo console de logs...")
    
    if janela_console_global is not None and janela_console_global.winfo_exists():
        janela_console_global.lift()
        return
    
    janela_console = tk.Toplevel(janela)
    janela_console.title("Console de Logs - Sistema de Gerenciamento de Senhas")
    janela_console.configure(bg="#1e1e2f")
    
    # Restaura a posição salva ou usa padrão
    restaurar_posicao_console(janela_console, 800, 400)
    
    # Frame principal
    main_frame = tk.Frame(janela_console, bg="#1e1e2f")
    main_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
    
    # Área de texto para logs
    text_logs = scrolledtext.ScrolledText(main_frame, height=20, width=80, 
                                         bg="#0d1117", fg="#00ff00", 
                                         font=("Consolas", 9),
                                         insertbackground="white")
    text_logs.pack(fill=tk.BOTH, expand=True)
    text_logs.configure(state='disabled')
    
    # Frame para botões
    frame_botoes = tk.Frame(main_frame, bg="#1e1e2f")
    frame_botoes.pack(fill=tk.X, pady=10)
    
    # Handler personalizado para o console
    console_handler = ConsoleHandler(text_logs)
    console_handler.setLevel(logging.INFO)
    formatter = logging.Formatter('%(asctime)s - %(levelname)s - %(message)s')
    console_handler.setFormatter(formatter)
    
    # Adiciona o handler ao logger principal
    logging.getLogger().addHandler(console_handler)
    
    # Guarda referências globais
    janela_console_global = janela_console
    console_handler_global = console_handler
    
    def limpar_console():
        text_logs.configure(state='normal')
        text_logs.delete(1.0, tk.END)
        text_logs.configure(state='disabled')
        logging.info("Console limpo")
    
    def fechar_console():
        global janela_console_global, console_handler_global
        
        # Remove o handler do logger
        if console_handler_global:
            logging.getLogger().removeHandler(console_handler_global)
            console_handler_global = None
        
        # Salva a posição antes de fechar
        salvar_posicao_console(janela_console)
        
        janela_console_global = None
        janela_console.destroy()
        logging.info("Console fechado")
    
    # Botões
    tk.Button(frame_botoes, text="🧹 Limpar Console", command=limpar_console,
             bg="#17a2b8", fg="white", font=("Arial", 10)).pack(side=tk.LEFT, padx=5)
    
    tk.Button(frame_botoes, text="❌ Fechar", command=fechar_console,
             bg="#dc3545", fg="white", font=("Arial", 10)).pack(side=tk.RIGHT, padx=5)
    
    # Configura o fechamento da janela
    janela_console.protocol("WM_DELETE_WINDOW", fechar_console)
    
    logging.info("Console de logs aberto com sucesso")

def mostrar_sobre():
    """Mostra informações sobre o sistema"""
    sobre_texto = """
Sistema de Gerenciamento de Senhas

🔒 Características:
• Armazenamento seguro com criptografia AES
• Gerador de senhas personalizável
• Categorização automática de sites
• Detecção de contas duplicadas
• Interface moderna e intuitiva
• Console de logs integrado
• Exportação de contas em TXT

📊 Funcionalidades:
• Adicionar, visualizar e excluir contas
• Gerar senhas fortes
• Categorizar sites automaticamente
• Verificar duplicatas
• Logs detalhados do sistema
• Exportar contas para arquivos TXT

🛡️ Segurança:
• Criptografia Fernet (AES)
• Chave de criptografia local
• Dados protegidos
• Verificação de integridade

Desenvolvido com Python e Tkinter
Versão 2.0 - Sistema Completo
"""
    
    messagebox.showinfo("Sobre o Sistema", sobre_texto)
    logging.info("Informações do sistema exibidas")

# === Interface Principal ===
janela = tk.Tk()
janela.title("Gerenciador de Senhas")
janela.geometry("500x600")
janela.configure(bg="#1e1e2f")
janela.resizable(False, False)

# Verificação de senha mestre
senha_mestre = simpledialog.askstring("Senha Mestre", "Digite a senha mestre:", show="*")
if senha_mestre != SENHA_MESTRE:
    messagebox.showerror("Acesso Negado", "Senha mestre incorreta.")
    janela.destroy()
    exit()

logging.info("Acesso concedido - Senha mestre correta")

# Título
tk.Label(janela, text="🔐 Gerenciador de Senhas", font=("Arial", 18, "bold"), 
         bg="#1e1e2f", fg="white").pack(pady=20)

# Frame principal para os CAMPOS DE ENTRADA
frame_campos = tk.Frame(janela, bg="#1e1e2f")
frame_campos.pack(fill=tk.BOTH, expand=True, padx=30, pady=10)

# === CAMPOS DE ENTRADA VISÍVEIS ===

# Campo Site
tk.Label(frame_campos, text="Site:", bg="#1e1e2f", fg="white", 
         font=("Arial", 10, "bold")).grid(row=0, column=0, sticky="w", pady=10)
entry_site = tk.Entry(frame_campos, font=("Arial", 12), width=30)
entry_site.grid(row=0, column=1, sticky="ew", pady=10, padx=(10, 0))

# Campo Usuário
tk.Label(frame_campos, text="Usuário:", bg="#1e1e2f", fg="white", 
         font=("Arial", 10, "bold")).grid(row=1, column=0, sticky="w", pady=10)
entry_usuario = tk.Entry(frame_campos, font=("Arial", 12), width=30)
entry_usuario.grid(row=1, column=1, sticky="ew", pady=10, padx=(10, 0))

# Campo Senha
tk.Label(frame_campos, text="Senha:", bg="#1e1e2f", fg="white", 
         font=("Arial", 10, "bold")).grid(row=2, column=0, sticky="w", pady=10)

frame_senha = tk.Frame(frame_campos, bg="#1e1e2f")
frame_senha.grid(row=2, column=1, sticky="ew", pady=10, padx=(10, 0))

entry_senha = tk.Entry(frame_senha, show="*", font=("Arial", 12))
entry_senha.pack(side=tk.LEFT, fill=tk.X, expand=True)

# Botões para senha
frame_botoes_senha = tk.Frame(frame_senha, bg="#1e1e2f")
frame_botoes_senha.pack(side=tk.RIGHT, padx=(5, 0))

btn_mostrar = tk.Button(frame_botoes_senha, text="👁️", 
                       command=lambda: entry_senha.config(show="" if entry_senha.cget('show') == '*' else "*"),
                       bg="#444", fg="white", font=("Arial", 8), width=3)
btn_mostrar.pack(side=tk.LEFT, padx=2)

btn_gerar = tk.Button(frame_botoes_senha, text="🎲", 
                     command=mostrar_gerador_senha,
                     bg="#17a2b8", fg="white", font=("Arial", 8), width=3)
btn_gerar.pack(side=tk.LEFT, padx=2)

# Campo Apelido
tk.Label(frame_campos, text="Apelido (opcional):", bg="#1e1e2f", fg="white", 
         font=("Arial", 10, "bold")).grid(row=3, column=0, sticky="w", pady=10)
entry_apelido = tk.Entry(frame_campos, font=("Arial", 12), width=30)
entry_apelido.grid(row=3, column=1, sticky="ew", pady=10, padx=(10, 0))

# Configurar peso da coluna para expansão
frame_campos.columnconfigure(1, weight=1)

# Frame para botões principais
frame_botoes = tk.Frame(janela, bg="#1e1e2f")
frame_botoes.pack(fill=tk.X, padx=30, pady=20)

# Botões principais
tk.Button(frame_botoes, text="➕ Adicionar Conta", command=adicionar_conta, 
          bg="#28a745", fg="white", font=("Arial", 12, "bold"), 
          height=2).pack(fill=tk.X, pady=5)

tk.Button(frame_botoes, text="📋 Ver Contas", command=ver_contas, 
          bg="#17a2b8", fg="white", font=("Arial", 12, "bold"), 
          height=2).pack(fill=tk.X, pady=5)

tk.Button(frame_botoes, text="📤 Exportar TXT", command=exportar_contas_txt, 
          bg="#ff9800", fg="white", font=("Arial", 12), 
          height=2).pack(fill=tk.X, pady=5)

tk.Button(frame_botoes, text="📊 Console", command=mostrar_console, 
          bg="#6c757d", fg="white", font=("Arial", 12), 
          height=2).pack(fill=tk.X, pady=5)

tk.Button(frame_botoes, text="ℹ️ Sobre", command=mostrar_sobre, 
          bg="#6c757d", fg="white", font=("Arial", 12), 
          height=2).pack(fill=tk.X, pady=5)

# Status bar
status_bar = tk.Label(janela, text="Sistema Iniciado | Pronto para uso", 
                     bg="#2b2b3d", fg="#00ff00", font=("Arial", 8), anchor="w")
status_bar.pack(fill=tk.X, side=tk.BOTTOM)

logging.info("Interface principal carregada com sucesso")
logging.info("Sistema pronto para uso")

# Inicia a interface
janela.mainloop()