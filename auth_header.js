document.write(`
    <div style="background: #1a73e8; color: white; padding: 12px 40px; display: flex; justify-content: space-between; align-items: center; box-shadow: 0 2px 10px rgba(0,0,0,0.1); font-family: 'Inter', sans-serif;">
        <div style="font-size: 18px; font-weight: bold; cursor:pointer;" onclick="window.location.href='cliente.html'">⚽ Camisa 10</div>
        <div id="container-autenticacao">
            <div style="display: flex; gap: 10px; align-items: center;" id="area-login-formulario">
                <span style="font-size: 14px;">Identifique-se:</span>
                <input type="email" id="login_email" placeholder="Seu E-mail" style="padding: 6px 12px; border: none; border-radius: 4px; font-size: 14px;">
                <input type="password" id="login_senha" placeholder="Sua Senha" style="padding: 6px 12px; border: none; border-radius: 4px; font-size: 14px;">
                <button onclick="realizarLoginGlobal()" style="background: #28a745; color: white; border: none; padding: 6px 15px; border-radius: 4px; cursor: pointer; font-weight: bold; font-size: 14px;">Entrar</button>
                <button onclick="window.location.href='cadastro_de_login_cliente.html'" style="background: transparent; color: white; border: 1px solid white; padding: 5px 12px; border-radius: 4px; cursor: pointer; font-size: 13px; font-weight: 500; transition: 0.2s;">Cadastrar-se</button>
            </div>
        </div>
    </div>
`);

async function realizarLoginGlobal() {
    const email = document.getElementById('login_email').value;
    const senha = document.getElementById('login_senha').value; // Coleta o valor do campo de senha

    if (!email) { alert("Por favor, digite seu e-mail."); return; }
    if (!senha) { alert("Por favor, digite sua senha."); return; }

    try {
        // Certifique-se de receber 'email' e 'senha' na sua rota correspondente do Flask
        const res = await fetch('http://127.0.0.1:5000/login-cliente', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ email, senha })
        });
        const dados = await res.json();

        if (res.ok) {
            localStorage.setItem('cliente_id', dados.cliente_id);
            localStorage.setItem('cliente_nome', dados.nome);
            renderizarUsuarioLogado(dados.nome);
        } else { 
            alert(dados.error || "Dados de acesso incorretos."); 
        }
    } catch (e) { 
        alert("Erro ao conectar com o servidor Flask."); 
    }
}

function renderizarUsuarioLogado(nome) {
    const container = document.getElementById('container-autenticacao');
    if (container) {
        container.innerHTML = `
            <div style="font-weight: bold; display: flex; gap: 12px; align-items: center; font-size: 14px;">
                <span style="cursor: pointer; display: flex; align-items: center; gap: 5px; text-decoration: underline;" onclick="window.location.href='perfil.html'" title="Clique para ver seu perfil">
                    👤 Olá, ${nome}!
                </span>
                <button onclick="window.location.href='perfil.html'" style="background: #ffffff; color: #1a73e8; border: none; padding: 6px 12px; border-radius: 4px; cursor: pointer; font-weight: bold; font-size: 13px;">Meu Perfil</button>
                <button onclick="window.location.href='carrinho.html'" style="background: #ff9900; color: white; border: none; padding: 6px 12px; border-radius: 4px; cursor: pointer; font-weight: bold; font-size: 13px;">🛒 Ver Meu Carrinho</button>
                <button onclick="logoutGlobal()" style="background: #dc3545; color: white; border: none; padding: 6px 12px; border-radius: 4px; cursor: pointer; font-size: 13px;">Sair</button>
            </div>
        `;
    }
}

function logoutGlobal() {
    localStorage.removeItem('cliente_id');
    localStorage.removeItem('cliente_nome');
    location.reload();
}

document.addEventListener("DOMContentLoaded", () => {
    const nomeSalvo = localStorage.getItem('cliente_nome');
    if (nomeSalvo) { 
        renderizarUsuarioLogado(nomeSalvo); 
    }
});

function gerenciarBotaoUsuario() {
    const clienteId = localStorage.getItem('cliente_id');

    if (clienteId && clienteId !== "null" && clienteId !== "undefined" && clienteId.trim() !== "") {
        window.location.href = "perfil.html";
    } else {
        window.location.href = "cadastro_de_login_cliente.html";
    }
}

function adicionarAoCarrinho(id, nome, preco, imagem, tamanhoEscolhido) {
    let carrinho = JSON.parse(localStorage.getItem('carrinho')) || [];

    const tamanho = tamanhoEscolhido ? tamanhoEscolhido.toUpperCase() : 'M';

    const produtoExistente = carrinho.find(item => item.camisa_id === id && item.tamanho === tamanho);

    if (produtoExistente) {
        produtoExistente.quantidade += 1;
    } else {
        carrinho.push({
            camisa_id: id,
            nome: nome,
            preco: preco,
            imagem: imagem || 'https://picsum.photos/250',
            quantidade: 1,
            tamanho: tamanho 
        });
    }
    localStorage.setItem('carrinho', JSON.stringify(carrinho));
    alert(`${nome} (Tamanho ${tamanho}) adicionada ao carrinho!`);
}