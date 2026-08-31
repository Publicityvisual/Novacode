#!/usr/bin/env python3
"""
Novacode Autonomous Test Runner & Auto-Healer
Detects test suites (pytest, npm test, cargo test, go test) and coordinates auto-healing.
"""
import os, sys, subprocess
from pathlib import Path

def detect_and_run_tests():
    cwd = Path.cwd()
    cmd = None
    
    if (cwd / "pytest.ini").exists() or (cwd / "tests").exists() or any(cwd.glob("test_*.py")):
        cmd = ["pytest"]
    elif (cwd / "package.json").exists():
        cmd = ["npm", "test"]
    elif (cwd / "Cargo.toml").exists():
        cmd = ["cargo", "test"]
    elif any(cwd.glob("*_test.go")):
        cmd = ["go", "test", "./..."]
    else:
        print("⚠️ No se detectó una suite de pruebas estándar (pytest, npm test, cargo test, go test).")
        return

    print(f"🧪 Novacode Test Runner: Ejecutando '{' '.join(cmd)}'...")
    res = subprocess.run(cmd, capture_output=True, text=True)
    
    if res.returncode == 0:
        print("🟢 Todos los tests pasaron exitosamente al 100%!")
        print(res.stdout)
    else:
        print("🔴 Fallos detectados en los tests:\n")
        print(res.stdout or res.stderr)
        
        if "--heal" in sys.argv:
            print("\n🤖 Iniciando Agente de Auto-Sanación Novacode...")
            heal_prompt = f"Corrige el siguiente fallo en las pruebas hasta que pasen en verde:\n\n{res.stdout or res.stderr}"
            subprocess.run(["/Users/djkoveck/.local/bin/novacode", heal_prompt])
        else:
            print("\n💡 Ejecuta 'novacode test --heal' para que Novacode resuelva los fallos automáticamente.")

def main():
    detect_and_run_tests()

if __name__ == "__main__":
    main()
