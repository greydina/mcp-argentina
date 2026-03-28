#!/usr/bin/env python3
"""Quick test script para verificar tools."""

import asyncio
from mcp_argentina.infrastructure.mcp import tools


async def main():
    print("Testing MCP Argentina tools...\n")
    
    # Test 1: get_dolar
    print("1. Testing get_dolar('blue')...")
    try:
        result = await tools.get_dolar('blue')
        print(f"   ✓ Success!")
        print(f"   Compra: ${result['compra']}")
        print(f"   Venta: ${result['venta']}")
        print(f"   Fecha: {result['fecha']}\n")
    except Exception as e:
        print(f"   ✗ Error: {e}\n")
        return False
    
    # Test 2: get_cotizaciones
    print("2. Testing get_cotizaciones()...")
    try:
        result = await tools.get_cotizaciones()
        print(f"   ✓ Success!")
        print(f"   Tipos disponibles: {list(result.keys())}\n")
    except Exception as e:
        print(f"   ✗ Error: {e}\n")
        return False
    
    # Test 3: convertir
    print("3. Testing convertir(100 USD → ARS, blue)...")
    try:
        result = await tools.convertir(
            monto=100,
            de="USD",
            a="ARS",
            tipo_cambio="blue"
        )
        print(f"   ✓ Success!")
        print(f"   100 USD = ${result['monto_convertido']} ARS")
        print(f"   Cotización usada: {result['cotizacion_usada']} (${result['valor_cotizacion']})\n")
    except Exception as e:
        print(f"   ✗ Error: {e}\n")
        return False
    
    print("✅ All tests passed!")
    return True


if __name__ == "__main__":
    success = asyncio.run(main())
    exit(0 if success else 1)
