from db import get_connection

def atualizar_estrutura_empresa():
    conn = get_connection()
    cur = conn.cursor()

    # Cria tabela de configuração da empresa (1 registro)
    cur.execute(
        """
        CREATE TABLE IF NOT EXISTS empresa_config (
            id INTEGER PRIMARY KEY,
            nome_fantasia TEXT,
            razao_social TEXT,
            cnpj TEXT,
            ie TEXT,
            endereco TEXT,
            bairro TEXT,
            cidade TEXT,
            uf TEXT,
            telefone TEXT,
            pix_chave TEXT
        );
        """
    )

    # Garante que exista pelo menos 1 registro (id = 1)
    cur.execute("SELECT id FROM empresa_config WHERE id = 1;")
    row = cur.fetchone()
    if not row:
        cur.execute(
            """
            INSERT INTO empresa_config
                (id, nome_fantasia, razao_social, cnpj, ie,
                 endereco, bairro, cidade, uf, telefone, pix_chave)
            VALUES
                (1, 'MANDACARU TEC SISTEMAS', 'Mandacaru Tec Sistemas',
                 '', '', '', '', '', '', '', '');
            """
        )
        print("Registro padrão de empresa_config criado (id=1).")

    conn.commit()
    conn.close()
    print("Atualização de estrutura (empresa_config) concluída.")


if __name__ == "__main__":
    atualizar_estrutura_empresa()
