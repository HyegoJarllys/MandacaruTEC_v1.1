import React, { useState } from 'react';
import { Database, MessageCircle, Zap, Clock, Bell, TrendingUp, Package, AlertTriangle, ChevronRight, Check, Code } from 'lucide-react';

const N8NArchitecture = () => {
  const [selectedWorkflow, setSelectedWorkflow] = useState(null);
  const [activeTab, setActiveTab] = useState('architecture');

  const workflows = [
    {
      id: 'webhook-vendas',
      name: 'Webhook de Vendas',
      icon: Zap,
      color: 'bg-yellow-500',
      trigger: 'A cada venda no PDV',
      description: 'Recebe dados da venda em tempo real e processa alertas críticos',
      nodes: [
        { type: 'Webhook', config: 'POST /venda-realizada' },
        { type: 'PostgreSQL', config: 'Atualiza estoque' },
        { type: 'Code', config: 'Verifica se estoque < mínimo' },
        { type: 'IF', config: 'Estoque crítico?' },
        { type: 'Evolution API', config: 'Envia alerta WhatsApp' },
      ],
      code: `// No seu PDV (após finalizar venda)
async function enviarVendaParaN8n(resumo) {
  await fetch('http://localhost:5678/webhook/venda-realizada', {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({
      venda_id: resumo.id,
      itens: resumo.itens,
      total: resumo.total,
      data_hora: resumo.data_hora
    })
  });
}`
    },
    {
      id: 'bot-whatsapp',
      name: 'Bot de Consultas WhatsApp',
      icon: MessageCircle,
      color: 'bg-green-500',
      trigger: 'Mensagem recebida no WhatsApp',
      description: 'Responde perguntas do dono sobre estoque, vendas e relatórios',
      nodes: [
        { type: 'Evolution Webhook', config: 'Recebe mensagem' },
        { type: 'Code', config: 'Detecta intenção (NLP simples)' },
        { type: 'Switch', config: 'Rota por tipo de consulta' },
        { type: 'PostgreSQL', config: 'Busca dados' },
        { type: 'Code', config: 'Formata resposta' },
        { type: 'Evolution API', config: 'Envia resposta' },
      ],
      commands: [
        { cmd: 'estoque [produto]', desc: 'Consulta quantidade em estoque' },
        { cmd: 'vendas hoje', desc: 'Relatório do dia' },
        { cmd: 'top 5', desc: 'Produtos mais vendidos' },
        { cmd: 'parados', desc: 'Produtos sem venda há 7+ dias' },
        { cmd: 'previsão [produto]', desc: 'Quando vai acabar' },
      ]
    },
    {
      id: 'alerta-diario',
      name: 'Relatório Diário Automático',
      icon: Clock,
      color: 'bg-blue-500',
      trigger: 'Cron: Todo dia às 20h',
      description: 'Envia resumo do dia automaticamente',
      nodes: [
        { type: 'Schedule', config: 'Cron: 0 20 * * *' },
        { type: 'PostgreSQL', config: 'SELECT vendas do dia' },
        { type: 'Code', config: 'Calcula métricas' },
        { type: 'Evolution API', config: 'Envia relatório' },
      ],
      output: `📊 *Resumo do Dia - 14/11/2025*

💰 Faturamento: R$ 1.847,50
🛒 Vendas: 23
📈 Ticket médio: R$ 80,33

🔥 *Top 3 Produtos:*
1. Arroz 5kg - 12 unidades
2. Feijão 1kg - 8 unidades  
3. Óleo de Soja - 7 unidades

⚠️ *Alertas:*
• Café Pilão: apenas 3 pacotes
• Açúcar Cristal: 5 kg restantes`
    },
    {
      id: 'alerta-estoque',
      name: 'Verificação de Estoque',
      icon: Package,
      color: 'bg-orange-500',
      trigger: 'Cron: A cada 2 horas',
      description: 'Verifica produtos com estoque baixo e envia alertas',
      nodes: [
        { type: 'Schedule', config: 'Cron: 0 */2 * * *' },
        { type: 'PostgreSQL', config: 'SELECT produtos WHERE qtd < minimo' },
        { type: 'IF', config: 'Há produtos críticos?' },
        { type: 'Code', config: 'Gera lista + sugestão de compra' },
        { type: 'Evolution API', config: 'Envia alerta' },
      ]
    },
    {
      id: 'analise-semanal',
      name: 'Análise Semanal Inteligente',
      icon: TrendingUp,
      color: 'bg-purple-500',
      trigger: 'Cron: Domingo às 18h',
      description: 'Análise profunda com insights e recomendações',
      nodes: [
        { type: 'Schedule', config: 'Cron: 0 18 * * 0' },
        { type: 'PostgreSQL', config: 'Dados últimas 4 semanas' },
        { type: 'Code', config: 'Análise de tendências' },
        { type: 'HTTP', config: 'API Claude (opcional)' },
        { type: 'Evolution API', config: 'Envia relatório' },
      ]
    }
  ];

  const dbSchema = {
    produtos: [
      { campo: 'id', tipo: 'SERIAL PRIMARY KEY' },
      { campo: 'codigo_barras', tipo: 'TEXT UNIQUE' },
      { campo: 'nome', tipo: 'TEXT' },
      { campo: 'preco', tipo: 'DECIMAL(10,2)' },
      { campo: 'quantidade_estoque', tipo: 'INTEGER', novo: true },
      { campo: 'estoque_minimo', tipo: 'INTEGER', novo: true },
      { campo: 'ultima_venda', tipo: 'TIMESTAMP', novo: true },
      { campo: 'validade', tipo: 'DATE', novo: true },
    ],
    vendas: [
      { campo: 'id', tipo: 'SERIAL PRIMARY KEY' },
      { campo: 'data_hora', tipo: 'TIMESTAMP' },
      { campo: 'total', tipo: 'DECIMAL(10,2)' },
      { campo: 'forma_pagamento', tipo: 'TEXT' },
    ],
    itens_venda: [
      { campo: 'id', tipo: 'SERIAL PRIMARY KEY' },
      { campo: 'venda_id', tipo: 'INTEGER REFERENCES vendas(id)' },
      { campo: 'codigo_barras', tipo: 'TEXT' },
      { campo: 'quantidade', tipo: 'INTEGER' },
      { campo: 'subtotal', tipo: 'DECIMAL(10,2)' },
    ]
  };

  const setupSteps = [
    {
      title: '1. Configurar PostgreSQL no n8n',
      steps: [
        'No n8n: Settings → Credentials → Add Credential → PostgreSQL',
        'Host: localhost (ou IP do container)',
        'Database: mandacarutec',
        'User: seu_usuario',
        'Password: sua_senha',
        'Port: 5432',
        'Testar conexão'
      ]
    },
    {
      title: '2. Configurar Evolution API',
      steps: [
        'Já deve estar rodando no Docker',
        'No n8n: Add Credential → HTTP Header Auth',
        'Nome: Evolution-API',
        'Header Name: apikey',
        'Header Value: sua_api_key_evolution',
        'Endpoint base: http://evolution-api:8080'
      ]
    },
    {
      title: '3. Adicionar campos ao banco',
      steps: [
        'Execute este SQL no PostgreSQL:',
        'ALTER TABLE produtos ADD COLUMN quantidade_estoque INTEGER DEFAULT 0;',
        'ALTER TABLE produtos ADD COLUMN estoque_minimo INTEGER DEFAULT 10;',
        'ALTER TABLE produtos ADD COLUMN ultima_venda TIMESTAMP;',
        'ALTER TABLE produtos ADD COLUMN validade DATE;'
      ]
    },
    {
      title: '4. Modificar PDV para chamar webhook',
      steps: [
        'Em pdv_functions.py, adicione após salvar_venda_no_banco():',
        'import requests',
        'requests.post("http://localhost:5678/webhook/venda-realizada", json=resumo)',
        'Também atualize quantidade_estoque após cada venda'
      ]
    }
  ];

  return (
    <div className="min-h-screen bg-gradient-to-br from-slate-900 via-blue-900 to-slate-900 text-white p-6">
      <div className="max-w-7xl mx-auto">
        
        {/* Header */}
        <div className="text-center mb-8">
          <h1 className="text-4xl font-bold mb-2 bg-gradient-to-r from-blue-400 to-green-400 bg-clip-text text-transparent">
            Arquitetura do Agente IA
          </h1>
          <p className="text-slate-300">PDV Mandacaru + n8n + Evolution API + PostgreSQL</p>
        </div>

        {/* Tabs */}
        <div className="flex gap-2 mb-6 bg-slate-800 p-1 rounded-lg w-fit mx-auto">
          <button
            onClick={() => setActiveTab('architecture')}
            className={`px-6 py-3 rounded-md transition ${activeTab === 'architecture' ? 'bg-blue-600' : 'hover:bg-slate-700'}`}
          >
            Workflows
          </button>
          <button
            onClick={() => setActiveTab('database')}
            className={`px-6 py-3 rounded-md transition ${activeTab === 'database' ? 'bg-blue-600' : 'hover:bg-slate-700'}`}
          >
            Banco de Dados
          </button>
          <button
            onClick={() => setActiveTab('setup')}
            className={`px-6 py-3 rounded-md transition ${activeTab === 'setup' ? 'bg-blue-600' : 'hover:bg-slate-700'}`}
          >
            Configuração
          </button>
        </div>

        {/* Architecture Tab */}
        {activeTab === 'architecture' && (
          <>
            {!selectedWorkflow ? (
              <div className="grid md:grid-cols-2 lg:grid-cols-3 gap-4">
                {workflows.map(wf => {
                  const Icon = wf.icon;
                  return (
                    <div
                      key={wf.id}
                      onClick={() => setSelectedWorkflow(wf)}
                      className="bg-slate-800 rounded-lg p-6 cursor-pointer hover:bg-slate-750 transition border border-slate-700 hover:border-blue-500"
                    >
                      <div className={`${wf.color} w-14 h-14 rounded-lg flex items-center justify-center mb-4`}>
                        <Icon size={28} />
                      </div>
                      <h3 className="text-xl font-bold mb-2">{wf.name}</h3>
                      <div className="text-sm text-slate-400 mb-3">
                        <Clock size={14} className="inline mr-1" />
                        {wf.trigger}
                      </div>
                      <p className="text-slate-300 text-sm mb-4">{wf.description}</p>
                      <span className="text-blue-400 text-sm flex items-center gap-1">
                        Ver detalhes <ChevronRight size={16} />
                      </span>
                    </div>
                  );
                })}
              </div>
            ) : (
              <div className="bg-slate-800 rounded-lg p-8 border border-slate-700">
                <button
                  onClick={() => setSelectedWorkflow(null)}
                  className="text-slate-400 hover:text-white mb-6 flex items-center gap-2"
                >
                  ← Voltar
                </button>

                <div className="flex items-start justify-between mb-6">
                  <div className="flex items-center gap-4">
                    <div className={`${selectedWorkflow.color} w-16 h-16 rounded-lg flex items-center justify-center`}>
                      {React.createElement(selectedWorkflow.icon, { size: 32 })}
                    </div>
                    <div>
                      <h2 className="text-3xl font-bold mb-2">{selectedWorkflow.name}</h2>
                      <p className="text-slate-400">{selectedWorkflow.description}</p>
                    </div>
                  </div>
                </div>

                {/* Trigger */}
                <div className="bg-slate-900 rounded-lg p-4 mb-6 border border-green-500">
                  <div className="flex items-center gap-2 text-green-400 mb-2">
                    <Zap size={20} />
                    <span className="font-bold">Trigger</span>
                  </div>
                  <p className="text-slate-200">{selectedWorkflow.trigger}</p>
                </div>

                {/* Nodes Flow */}
                <div className="mb-6">
                  <h3 className="text-xl font-bold mb-4 text-blue-400">Fluxo de Nós (Nodes)</h3>
                  <div className="space-y-3">
                    {selectedWorkflow.nodes.map((node, idx) => (
                      <div key={idx} className="flex items-center gap-4">
                        <div className="bg-blue-600 w-10 h-10 rounded-full flex items-center justify-center font-bold">
                          {idx + 1}
                        </div>
                        <div className="bg-slate-900 flex-1 p-4 rounded-lg border border-slate-700">
                          <div className="font-bold text-blue-400">{node.type}</div>
                          <div className="text-sm text-slate-300">{node.config}</div>
                        </div>
                      </div>
                    ))}
                  </div>
                </div>

                {/* Commands (for bot) */}
                {selectedWorkflow.commands && (
                  <div className="mb-6">
                    <h3 className="text-xl font-bold mb-4 text-green-400">Comandos Disponíveis</h3>
                    <div className="grid md:grid-cols-2 gap-3">
                      {selectedWorkflow.commands.map((cmd, idx) => (
                        <div key={idx} className="bg-slate-900 p-4 rounded-lg border border-slate-700">
                          <code className="text-green-400 font-mono">{cmd.cmd}</code>
                          <p className="text-slate-300 text-sm mt-2">{cmd.desc}</p>
                        </div>
                      ))}
                    </div>
                  </div>
                )}

                {/* Code Example */}
                {selectedWorkflow.code && (
                  <div className="mb-6">
                    <h3 className="text-xl font-bold mb-4 text-purple-400">Código de Integração (PDV)</h3>
                    <div className="bg-slate-900 p-4 rounded-lg border border-slate-700 font-mono text-sm text-slate-300 overflow-x-auto">
                      <pre>{selectedWorkflow.code}</pre>
                    </div>
                  </div>
                )}

                {/* Output Example */}
                {selectedWorkflow.output && (
                  <div>
                    <h3 className="text-xl font-bold mb-4 text-yellow-400">Exemplo de Saída</h3>
                    <div className="bg-slate-900 p-6 rounded-lg border border-slate-700">
                      <pre className="text-slate-200 whitespace-pre-wrap">{selectedWorkflow.output}</pre>
                    </div>
                  </div>
                )}
              </div>
            )}
          </>
        )}

        {/* Database Tab */}
        {activeTab === 'database' && (
          <div className="space-y-6">
            <div className="bg-slate-800 rounded-lg p-8 border border-slate-700">
              <h2 className="text-2xl font-bold mb-4 flex items-center gap-2">
                <Database className="text-blue-400" />
                Estrutura do Banco PostgreSQL
              </h2>
              
              {Object.entries(dbSchema).map(([tableName, fields]) => (
                <div key={tableName} className="mb-8">
                  <h3 className="text-xl font-bold text-green-400 mb-3">Tabela: {tableName}</h3>
                  <div className="bg-slate-900 rounded-lg overflow-hidden border border-slate-700">
                    <table className="w-full">
                      <thead className="bg-slate-950">
                        <tr>
                          <th className="text-left p-3 text-blue-400">Campo</th>
                          <th className="text-left p-3 text-blue-400">Tipo</th>
                          <th className="text-left p-3 text-blue-400">Status</th>
                        </tr>
                      </thead>
                      <tbody>
                        {fields.map((field, idx) => (
                          <tr key={idx} className="border-t border-slate-800">
                            <td className="p-3 font-mono text-slate-200">{field.campo}</td>
                            <td className="p-3 text-slate-300">{field.tipo}</td>
                            <td className="p-3">
                              {field.novo ? (
                                <span className="bg-yellow-600 text-yellow-100 px-2 py-1 rounded text-xs">
                                  ADICIONAR
                                </span>
                              ) : (
                                <span className="bg-green-600 text-green-100 px-2 py-1 rounded text-xs">
                                  EXISTENTE
                                </span>
                              )}
                            </td>
                          </tr>
                        ))}
                      </tbody>
                    </table>
                  </div>
                </div>
              ))}

              <div className="bg-blue-900 border border-blue-500 rounded-lg p-6 mt-6">
                <h3 className="font-bold text-xl mb-3 flex items-center gap-2">
                  <AlertTriangle size={24} className="text-yellow-400" />
                  Importante: Migração do SQLite para PostgreSQL
                </h3>
                <p className="text-slate-200 mb-3">
                  Seu sistema atual usa SQLite. Para usar o agente, você precisa migrar para PostgreSQL.
                </p>
                <div className="bg-slate-900 p-4 rounded-lg">
                  <p className="text-sm text-slate-300 mb-2">Passos:</p>
                  <ol className="list-decimal list-inside space-y-1 text-slate-300">
                    <li>Instalar PostgreSQL no Docker</li>
                    <li>Criar banco "mandacarutec"</li>
                    <li>Rodar create_db.py adaptado para PostgreSQL</li>
                    <li>Exportar dados do SQLite e importar</li>
                    <li>Atualizar db.py para usar psycopg2</li>
                  </ol>
                </div>
              </div>
            </div>
          </div>
        )}

        {/* Setup Tab */}
        {activeTab === 'setup' && (
          <div className="space-y-4">
            {setupSteps.map((section, idx) => (
              <div key={idx} className="bg-slate-800 rounded-lg p-6 border border-slate-700">
                <h3 className="text-xl font-bold mb-4 text-blue-400">{section.title}</h3>
                <div className="space-y-3">
                  {section.steps.map((step, stepIdx) => (
                    <div key={stepIdx} className="flex items-start gap-3">
                      <div className="bg-blue-600 w-6 h-6 rounded-full flex items-center justify-center text-xs font-bold mt-1 flex-shrink-0">
                        {stepIdx + 1}
                      </div>
                      <div className="bg-slate-900 flex-1 p-3 rounded-lg border border-slate-700">
                        <code className="text-slate-200 text-sm">{step}</code>
                      </div>
                    </div>
                  ))}
                </div>
              </div>
            ))}

            <div className="bg-gradient-to-r from-green-900 to-blue-900 rounded-lg p-6 border border-green-500">
              <h3 className="text-2xl font-bold mb-3 flex items-center gap-2">
                <Check size={28} className="text-green-400" />
                Checklist Final
              </h3>
              <div className="space-y-2 text-slate-200">
                <label className="flex items-center gap-2">
                  <input type="checkbox" className="w-5 h-5" />
                  <span>PostgreSQL configurado no n8n</span>
                </label>
                <label className="flex items-center gap-2">
                  <input type="checkbox" className="w-5 h-5" />
                  <span>Evolution API conectada</span>
                </label>
                <label className="flex items-center gap-2">
                  <input type="checkbox" className="w-5 h-5" />
                  <span>Campos novos adicionados ao banco</span>
                </label>
                <label className="flex items-center gap-2">
                  <input type="checkbox" className="w-5 h-5" />
                  <span>PDV chamando webhook após venda</span>
                </label>
                <label className="flex items-center gap-2">
                  <input type="checkbox" className="w-5 h-5" />
                  <span>Workflows importados no n8n</span>
                </label>
                <label className="flex items-center gap-2">
                  <input type="checkbox" className="w-5 h-5" />
                  <span>Teste de envio WhatsApp OK</span>
                </label>
              </div>
            </div>
          </div>
        )}

      </div>
    </div>
  );
};

export default N8NArchitecture;
