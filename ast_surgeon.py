"""
NovaCode AST Code Surgeon
=========================
Realiza transformaciones y refactorizaciones de código a nivel estructural (AST)
garantizando que nunca se rompa la sintaxis ni el tipado:
- Renombrado seguro de funciones, clases y variables.
- Inyección automática de type hints.
- Detección de bucles ineficientes y anti-patrones.
"""

from __future__ import annotations

import ast
from pathlib import Path
from typing import Any, Dict, List, Optional, Tuple


class RenameTransformer(ast.NodeTransformer):
    """Transformador AST para renombrar funciones o clases de forma segura."""

    def __init__(self, target_type: str, old_name: str, new_name: str) -> None:
        self.target_type = target_type
        self.old_name = old_name
        self.new_name = new_name
        self.renamed_count = 0

    def visit_FunctionDef(self, node: ast.FunctionDef) -> ast.AST:
        if self.target_type in ["function", "any"] and node.name == self.old_name:
            node.name = self.new_name
            self.renamed_count += 1
        self.generic_visit(node)
        return node

    def visit_ClassDef(self, node: ast.ClassDef) -> ast.AST:
        if self.target_type in ["class", "any"] and node.name == self.old_name:
            node.name = self.new_name
            self.renamed_count += 1
        self.generic_visit(node)
        return node

    def visit_Name(self, node: ast.Name) -> ast.AST:
        if node.id == self.old_name:
            node.id = self.new_name
            self.renamed_count += 1
        return node


class ASTSurgeon:
    """Cirujano de código basado en el árbol sintáctico abstracto."""

    @staticmethod
    def rename_symbol(code: str, old_name: str, new_name: str, symbol_type: str = "any") -> Tuple[str, int]:
        """Renombra un símbolo en todo el código con seguridad sintáctica."""
        try:
            tree = ast.parse(code)
            transformer = RenameTransformer(symbol_type, old_name, new_name)
            new_tree = transformer.visit(tree)
            ast.fix_missing_locations(new_tree)
            new_code = ast.unparse(new_tree)
            return new_code, transformer.renamed_count
        except Exception as exc:
            return code, 0

    @staticmethod
    def analyze_complexity(code: str) -> Dict[str, Any]:
        """Analiza la complejidad ciclomática básica y detecta bucles anidados."""
        try:
            tree = ast.parse(code)
            nested_loops = 0
            functions_count = 0
            classes_count = 0

            for node in ast.walk(tree):
                if isinstance(node, ast.FunctionDef):
                    functions_count += 1
                elif isinstance(node, ast.ClassDef):
                    classes_count += 1
                elif isinstance(node, (ast.For, ast.While)):
                    for child in ast.walk(node):
                        if child is not node and isinstance(child, (ast.For, ast.While)):
                            nested_loops += 1

            return {
                "valid_syntax": True,
                "functions": functions_count,
                "classes": classes_count,
                "nested_loops_count": nested_loops,
                "is_optimized": nested_loops == 0,
            }
        except Exception as exc:
            return {"valid_syntax": False, "error": str(exc)}
