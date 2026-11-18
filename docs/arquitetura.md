# Arquitetura do MVP

Projeto acadêmico da Tecnoação. Aplicação Django monolítica modular com apresentação em templates HTML, regras de negócio nas views/forms e persistência com ORM (PostgreSQL 17 na implantação). Entidades: Maquina (UUID e série única), Documento (arquivo privado associado à máquina e ao criador) e Manutencao (intervenções técnicas).

Fluxo: administrador autenticado cadastra máquina -> associa documentos -> gera QR Code individual -> técnico autenticado escaneia código e consulta a ficha e os arquivos autorizados.

O QR Code identifica o equipamento mas não concede acesso a documentos sem autorização. Arquivos são servidos por view autenticada e ficam fora de diretórios públicos.

Fora do escopo: integração com CNC/CLP, estoque e aplicativo nativo/offline.
