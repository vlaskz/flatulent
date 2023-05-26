# Flatulent

Flatulent é uma biblioteca de compressão que combina o algoritmo LZW com a codificação de Huffman para obter taxas de compressão eficientes. Ela oferece as classes `FartCompressor` e `FartDecompressor` para comprimir e descomprimir dados, respectivamente.

## Instalação

Para instalar a biblioteca Flatulent, você pode usar o pip:

pip install flatulent


## Exemplo de uso

Aqui está um exemplo básico de como utilizar a biblioteca Flatulent para comprimir e descomprimir dados:

```python
from flatulent import FartCompressor, FartDecompressor

data = 'ABABABA' * 100000

compressor = FartCompressor()
compressed = compressor.compress(data)
print('Compressed size:', len(compressed))

decompressor = FartDecompressor()
decompressed = decompressor.decompress(compressed)
print('Decompressed size:', len(decompressed))
