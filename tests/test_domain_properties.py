"""
Test suite for enforcing domain model design principles and constraints.

This module contains tests that ensure the domain model follows
strict design principles including:
- All domain classes must be dataclasses
- Attributes must use approved types (primitives, domain classes,
  or their collections)
- Type hierarchies must be valid throughout nested structures

These tests act as architectural enforcement to maintain a clean domain model
that follows Domain-Driven Design principles.
"""

import inspect
import unittest
from dataclasses import is_dataclass
from typing import Optional, Union, Literal, get_args, get_origin, get_type_hints

# Import the domain module
import domain

# Expanded list of primitive types
PRIMITIVE_TYPES = {
    int,
    str,
    bool,
    float,
    dict,
    list,
    bytes,
    tuple,
    set,
    frozenset,
}


class TestDomainModule(unittest.TestCase):
    """Test suite for validating domain model structure and type constraints."""

    def test_classes_are_dataclasses(self):
        """
        Verify that all domain classes are properly decorated as dataclasses.

        This ensures:
        - Clean data structure definitions
        - Automatic implementation of __init__, __eq__, __repr__
        - Immutable data objects when frozen=True
        - Consistent object creation and comparison behavior
        """
        for name, obj in inspect.getmembers(domain, inspect.isclass):
            # Only check classes defined in our domain module
            if obj.__module__ == domain.__name__:
                with self.subTest(class_name=name):
                    self.assertTrue(
                        is_dataclass(obj),
                        f"Class '{name}' in module {obj.__module__} is not a dataclass. "
                        "All domain classes must be decorated with @dataclass. "
                        "This ensures consistent initialization, comparison, and "
                        "immutability when frozen=True is used."
                    )

    def test_attributes_have_valid_types(self):
        """
        Ensure all attributes of dataclasses in domain.py have valid types:
        - Primitive types
        - Optional/List wrappers around primitive types or domain classes
        - Other domain classes
        """
        domain_classes = {
            obj for name, obj in inspect.getmembers(domain, inspect.isclass)
        }
        for name, cls in inspect.getmembers(domain, inspect.isclass):
            if is_dataclass(cls):
                with self.subTest(dataclass=name):
                    hints = get_type_hints(cls)
                    for attr, attr_type in hints.items():
                        with self.subTest(attribute=attr):
                            valid, error_msg = self._is_valid_type(attr_type, domain_classes)
                            self.assertTrue(
                                valid,
                                f"Invalid type for attribute '{attr}' "
                                f"in class {name} (defined in {cls.__module__}): "
                                f"{error_msg or f'Found type {attr_type} which is not allowed.'} "
                                "Only primitive types, Optional/List/Dict wrappers, "
                                "or domain classes are allowed. "
                                f"If using a domain class, ensure it's defined in {domain.__name__}. "
                                "Valid primitive types are: "
                                f"{', '.join(t.__name__ for t in PRIMITIVE_TYPES)}. "
                                "For collections, only Optional[], List[], and Dict[str, T] "
                                "are allowed where T is a primitive or domain type."
                            )

    def _format_type_error(self, attr_type, context=""):
        """Format a helpful type error message"""
        if hasattr(attr_type, '__origin__'):
            origin = get_origin(attr_type)
            args = get_args(attr_type)
            return (
                f"{context}Invalid type construction: {origin.__name__}[{', '.join(str(a) for a in args)}]. "
                f"Check that all type arguments are either primitive types "
                f"({', '.join(t.__name__ for t in PRIMITIVE_TYPES)}) or "
                f"domain classes defined in {domain.__name__}.py"
            )
        return (
            f"{context}Invalid type: {attr_type}. Must be a primitive type "
            f"({', '.join(t.__name__ for t in PRIMITIVE_TYPES)}), "
            f"a domain class, or a supported collection type."
        )

    def _is_valid_type(self, attr_type, domain_classes):
        """Recursively check if a type is valid"""
        # Get the actual type if it's a ForwardRef
        if hasattr(attr_type, '__forward_arg__'):
            try:
                # Handle forward references to types defined later
                attr_type = getattr(domain, attr_type.__forward_arg__)
            except AttributeError:
                return False, f"Forward reference '{attr_type.__forward_arg__}' not found in domain module. " \
                             f"Ensure the referenced class is defined in {domain.__name__}.py"
        
        # Check if type is from a domain submodule
        if hasattr(attr_type, '__module__') and attr_type.__module__.startswith('domain.'):
            return True, None
            
        if attr_type in PRIMITIVE_TYPES or attr_type in domain_classes:
            return True, None
            
        origin = get_origin(attr_type)
        if origin is Optional:
            inner_type = get_args(attr_type)[0]
            return self._is_valid_type(inner_type, domain_classes)
        if origin is Union:
            inner_types = get_args(attr_type)
            for inner_type in inner_types:
                if inner_type is type(None):
                    continue
                valid, msg = self._is_valid_type(inner_type, domain_classes)
                if not valid:
                    return False, msg
            return True, None
        if origin is list:
            inner_type = get_args(attr_type)[0]
            # Check if inner_type is from domain submodule
            if hasattr(inner_type, '__module__') and inner_type.__module__.startswith('domain.'):
                return True, None
            if hasattr(inner_type, '__name__') and hasattr(domain, inner_type.__name__):
                return True, None
            return self._is_valid_type(inner_type, domain_classes)
        if origin is dict:
            key_type, value_type = get_args(attr_type)
            if key_type is not str:
                return False, "Dict keys must be strings in domain models"
            # For Dict, we allow str keys and check value type
            if value_type in domain_classes or (
                hasattr(value_type, '__module__') and 
                value_type.__module__.startswith('domain.')
            ):
                return True, None
            return self._is_valid_type(value_type, domain_classes)
        if origin is Literal:
            values = get_args(attr_type)
            invalid_values = [
                value for value in values 
                if not type(value) in PRIMITIVE_TYPES
            ]
            if invalid_values:
                return False, (
                    f"Literal values must be primitive types, found: "
                    f"{', '.join(str(type(v)) for v in invalid_values)}. "
                    f"Valid types are: {', '.join(t.__name__ for t in PRIMITIVE_TYPES)}"
                )
            return True, None

        return False, self._format_type_error(attr_type)
