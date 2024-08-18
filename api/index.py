import psycopg2
from flask import Flask, render_template, request, redirect, url_for, session
from urllib.parse import quote, unquote

app = Flask(__name__)
app.secret_key = 'supersecretkey'

# Configurações de conexão com o banco de dados Postgres
DB_CONFIG = {
    'dbname': 'zapcart',
    'user': 'IK-R-S',
    'password': 'E5zjlaZiSK3Q',
    'host': 'ep-calm-wildflower-96501958.eu-central-1.aws.neon.tech'
}

# Conexão e criação da tabela no Postgres
def init_db():
    conn = psycopg2.connect(**DB_CONFIG)
    cursor = conn.cursor()
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS carrinhos (
            id SERIAL PRIMARY KEY,
            pedido TEXT NOT NULL
        )
    ''')
    conn.commit()
    cursor.close()
    conn.close()

# Inicializa o banco de dados
init_db()

# Dados JSON dos produtos
produtos = [
    {"Produto": "Arroz", "Marca": "Tio João", "Preço": 25.00, "Localização": "Corredor 3", "Tipo": "Não perecíveis"},
    {"Produto": "Feijão", "Marca": "Kicaldo", "Preço": 8.50, "Localização": "Corredor 3", "Tipo": "Não perecíveis"},
    {"Produto": "Leite", "Marca": "Parmalat", "Preço": 4.50, "Localização": "Corredor 7", "Tipo": "Laticínios"},
    {"Produto": "Manteiga", "Marca": "Aviação", "Preço": 12.00, "Localização": "Corredor 7", "Tipo": "Laticínios"},
    {"Produto": "Café", "Marca": "Melitta", "Preço": 10.00, "Localização": "Corredor 4", "Tipo": "Não perecíveis"},
    {"Produto": "Açúcar", "Marca": "União", "Preço": 4.00, "Localização": "Corredor 3", "Tipo": "Não perecíveis"},
    {"Produto": "Macarrão", "Marca": "Renata", "Preço": 5.50, "Localização": "Corredor 5", "Tipo": "Não perecíveis"},
    {"Produto": "Óleo de Soja", "Marca": "Soya", "Preço": 7.00, "Localização": "Corredor 6", "Tipo": "Não perecíveis"},
    {"Produto": "Farinha de Trigo", "Marca": "Dona Benta", "Preço": 6.50, "Localização": "Corredor 4", "Tipo": "Não perecíveis"},
    {"Produto": "Molho de Tomate", "Marca": "Quero", "Preço": 3.20, "Localização": "Corredor 5", "Tipo": "Não perecíveis"},
    {"Produto": "Refrigerante", "Marca": "Coca-Cola", "Preço": 8.00, "Localização": "Corredor 8", "Tipo": "Refrigerantes"},
    {"Produto": "Sabão em Pó", "Marca": "Omo", "Preço": 15.00, "Localização": "Corredor 10", "Tipo": "Produtos de limpeza"},
    {"Produto": "Desodorante", "Marca": "Rexona", "Preço": 12.50, "Localização": "Corredor 12", "Tipo": "Higiene pessoal"},
    {"Produto": "Shampoo", "Marca": "Seda", "Preço": 10.90, "Localização": "Corredor 12", "Tipo": "Higiene pessoal"},
    {"Produto": "Creme Dental", "Marca": "Colgate", "Preço": 6.00, "Localização": "Corredor 12", "Tipo": "Higiene pessoal"},
    {"Produto": "Detergente", "Marca": "Ypê", "Preço": 2.30, "Localização": "Corredor 11", "Tipo": "Produtos de limpeza"},
    {"Produto": "Papel Higiênico", "Marca": "Neve", "Preço": 16.00, "Localização": "Corredor 11", "Tipo": "Higiene pessoal"},
    {"Produto": "Frango Congelado", "Marca": "Seara", "Preço": 20.00, "Localização": "Corredor 9", "Tipo": "Origem animal"},
    {"Produto": "Queijo Mussarela", "Marca": "Vigor", "Preço": 22.00, "Localização": "Frios", "Tipo": "Laticínios"},
    {"Produto": "Achocolatado", "Marca": "Nescau", "Preço": 8.50, "Localização": "Corredor 4", "Tipo": "Não perecíveis"}
]

categorias = [
    'Açougue', 'Bebidas alcoólicas', 'Casa', 'Frios', 'Frutas', 'Higiene pessoal', 
    'Laticínios', 'Legumes', 'Não perecíveis', 'Origem animal', 'Padaria', 
    'Produtos de limpeza', 'Produtos para pets', 'Refrigerantes', 'Saúde', 'Sucos', 
    'Verduras', 'Outros'
]

def get_cart():
    """Helper function to get the cart as a dictionary"""
    carrinho = session.get('carrinho', {})
    if isinstance(carrinho, list):
        carrinho = {str(index): item for index, item in enumerate(carrinho)}
        session['carrinho'] = carrinho
    return carrinho

@app.route('/')
def index():
    categoria_selecionada = request.args.get('categoria', 'Não perecíveis')
    produtos_filtrados = [p for p in produtos if p['Tipo'] == categoria_selecionada]
    carrinho = get_cart()
    carrinho_count = sum(item['quantidade'] for item in carrinho.values())
    return render_template('index.html', categorias=categorias, produtos=produtos_filtrados, categoria_selecionada=categoria_selecionada, carrinho_count=carrinho_count)

@app.route('/add_to_cart/<produto_nome>')
def add_to_cart(produto_nome):
    categoria = request.args.get('categoria', 'Não perecíveis')
    produto_nome = unquote(produto_nome)
    produto = next((p for p in produtos if p["Produto"] == produto_nome), None)
    if produto:
        carrinho = get_cart()
        
        # Utiliza o nome do produto como chave única
        produto_id = produto_nome
        
        if produto_id in carrinho:
            carrinho[produto_id]['quantidade'] += 1
            carrinho[produto_id]['subtotal'] = carrinho[produto_id]['quantidade'] * produto['Preço']
        else:
            carrinho[produto_id] = {
                'produto': produto,
                'quantidade': 1,
                'subtotal': produto['Preço']
            }
        session['carrinho'] = carrinho
    
    return redirect(url_for('index', categoria=categoria))

@app.route('/cart')
def cart():
    carrinho = get_cart()
    total = sum(item['subtotal'] for item in carrinho.values())
    return render_template('cart.html', carrinho=carrinho, total=total)

@app.route('/remove_from_cart/<produto_nome>')
def remove_from_cart(produto_nome):
    categoria = request.args.get('categoria', 'Não perecíveis')
    carrinho = get_cart()
    produto_nome = unquote(produto_nome)
    if produto_nome in carrinho:
        if carrinho[produto_nome]['quantidade'] > 1:
            carrinho[produto_nome]['quantidade'] -= 1
            carrinho[produto_nome]['subtotal'] = carrinho[produto_nome]['quantidade'] * carrinho[produto_nome]['produto']['Preço']
        else:
            del carrinho[produto_nome]
        session['carrinho'] = carrinho
    return redirect(url_for('cart', categoria=categoria))

@app.route('/imprimir_lista', methods=['POST'])
def imprimir_lista():
    carrinho = get_cart()
    total = sum(item['subtotal'] for item in carrinho.values())
    
    # Gera a string da lista
    lista = ''
    for item in carrinho.values():
        lista += f"{item['produto']['Produto']} (x{item['quantidade']})\nR$ {item['subtotal']}\n\n"
    lista += f"TOTAL: R$ {total}"
    
    # Salva no banco de dados
    conn = psycopg2.connect(**DB_CONFIG)
    cursor = conn.cursor()
    cursor.execute('INSERT INTO carrinhos (pedido) VALUES (%s) RETURNING id', (lista,))
    carrinho_id = cursor.fetchone()[0]
    conn.commit()
    cursor.close()
    conn.close()
    
    # Limpa o carrinho
    session['carrinho'] = {}
    
    return redirect(url_for('pedido', carrinho_id=carrinho_id))

@app.route('/pedidos/<int:carrinho_id>')
def pedido(carrinho_id):
    conn = psycopg2.connect(**DB_CONFIG)
    cursor = conn.cursor()
    cursor.execute('SELECT pedido FROM carrinhos WHERE id = %s', (carrinho_id,))
    pedido = cursor.fetchone()
    cursor.close()
    conn.close()
    
    if pedido:
        return render_template('pedido.html', pedido=pedido[0])
    else:
        return "Pedido não encontrado", 404
